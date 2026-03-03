#!/usr/bin/env python3
"""
PostToolUse hook: Track edits, validate syntax, and log to JSONL.

Records Edit/Write operations with syntax checking, sensitive data masking,
and affected file estimation. Outputs additionalContext for Claude feedback.
"""

import fnmatch
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add hooks dir to path for lib imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.jsonl_io import append_jsonl

# --- Constants ---

LOG_DIR = ".claude/logs"
LOG_FILE = os.path.join(LOG_DIR, "edit-history.jsonl")
SESSION_STATE_FILE = "/tmp/claude-edit-tracker-session.json"
MAX_STRING_LENGTH = 200
SYNTAX_CHECK_TIMEOUT = 3
AFFECTED_FILES_TIMEOUT = 3

SENSITIVE_PATH_PATTERNS = [
    "*.env",
    "*.env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*secret*",
    "*credential*",
    "*password*",
    "**/.ssh/*",
    "**/.aws/*",
    "**/.gcloud/*",
    "**/secrets.yaml",
    "**/secrets.json",
    "**/wp-config.php",
]

MASKING_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*[\"']?[\w\-]{16,}", r"\1=***MASKED***"),
    (r"(?i)(secret|token|password|passwd)\s*[:=]\s*[\"']?[\w\-]{8,}", r"\1=***MASKED***"),
    (r"xox[bporas]-[\w\-]{10,}", "***SLACK_TOKEN***"),
    (r"sk-[a-zA-Z0-9]{20,}", "***API_KEY***"),
    (r"ghp_[a-zA-Z0-9]{36}", "***GITHUB_TOKEN***"),
    (r"-----BEGIN [\w ]+ KEY-----", "***PRIVATE_KEY***"),
    (r"(?i)bearer\s+[\w\-.]{20,}", "Bearer ***MASKED***"),
]


# --- Sensitive data protection ---


def is_sensitive_path(file_path: str) -> bool:
    """Check if file path matches sensitive path patterns."""
    basename = os.path.basename(file_path)
    for pattern in SENSITIVE_PATH_PATTERNS:
        if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(file_path, pattern):
            return True
    return False


def mask_sensitive(text: str) -> str:
    """Mask sensitive values in text before logging."""
    for pattern, replacement in MASKING_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


# --- Session state ---


def load_session() -> dict:
    """Load or create session state from /tmp."""
    try:
        if os.path.exists(SESSION_STATE_FILE):
            with open(SESSION_STATE_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {
        "session_id": uuid.uuid4().hex[:8],
        "edit_count": 0,
    }


def save_session(state: dict) -> None:
    """Save session state to /tmp."""
    try:
        with open(SESSION_STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


# --- Syntax checking ---


def check_syntax(file_path: str, ext: str) -> tuple[bool | None, str]:
    """Run language-specific syntax check. Returns (ok, error_message).

    Returns None for ok if check timed out or language is unsupported.
    """
    commands: dict[str, list[str]] = {
        ".py": ["python3", "-c", f"import ast; ast.parse(open('{file_path}').read())"],
        ".php": ["php", "-l", file_path],
        ".js": ["node", "--check", file_path],
        ".json": ["python3", "-c", f"import json; json.load(open('{file_path}'))"],
    }

    cmd = commands.get(ext)
    if cmd is None:
        return None, ""

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SYNTAX_CHECK_TIMEOUT,
        )
        if result.returncode == 0:
            return True, ""
        error_msg = (result.stderr or result.stdout).strip()
        return False, error_msg[:300]
    except subprocess.TimeoutExpired:
        return None, "syntax check timed out"
    except FileNotFoundError:
        return None, f"command not found: {cmd[0]}"
    except Exception as e:
        return None, str(e)[:200]


# --- Affected files estimation ---


def estimate_affected_files(file_path: str) -> list[str]:
    """Estimate affected files by basename glob (lightweight, no grep)."""
    basename = Path(file_path).stem
    if not basename or len(basename) < 3:
        return []

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    affected = []

    try:
        result = subprocess.run(
            ["find", project_dir, "-name", f"*{basename}*", "-type", "f",
             "-not", "-path", "*/node_modules/*",
             "-not", "-path", "*/.git/*",
             "-not", "-path", "*/vendor/*"],
            capture_output=True, text=True,
            timeout=AFFECTED_FILES_TIMEOUT,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line and line != file_path and os.path.isfile(line):
                    rel = os.path.relpath(line, project_dir)
                    affected.append(rel)
    except (subprocess.TimeoutExpired, Exception):
        pass

    return affected[:5]


# --- Line counting ---


def count_lines_changed(old_string: str, new_string: str) -> tuple[int, int]:
    """Count lines added and removed."""
    old_lines = old_string.count("\n") + (1 if old_string else 0) if old_string else 0
    new_lines = new_string.count("\n") + (1 if new_string else 0) if new_string else 0
    added = max(0, new_lines - old_lines)
    removed = max(0, old_lines - new_lines)
    return added, removed


# --- Main ---


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Sensitive path check — skip entirely
    if is_sensitive_path(file_path):
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lower()

    # Extract strings
    old_string = tool_input.get("old_string", "") or ""
    new_string = tool_input.get("new_string", "") or tool_input.get("content", "") or ""

    # Mask and truncate
    old_masked = mask_sensitive(old_string)[:MAX_STRING_LENGTH]
    new_masked = mask_sensitive(new_string)[:MAX_STRING_LENGTH]

    # Line counts
    lines_added, lines_removed = count_lines_changed(old_string, new_string)

    # Syntax check (only if file exists)
    syntax_ok = None
    syntax_error = ""
    if os.path.isfile(file_path):
        syntax_ok, syntax_error = check_syntax(file_path, ext)

    # Affected files
    affected_files = estimate_affected_files(file_path)

    # Session state
    session = load_session()
    session["edit_count"] = session.get("edit_count", 0) + 1
    save_session(session)

    # Build log entry
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    rel_path = os.path.relpath(file_path, project_dir) if file_path.startswith(project_dir) else file_path

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "file": rel_path,
        "ext": ext,
        "old_string": old_masked,
        "new_string": new_masked,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "syntax_ok": syntax_ok,
        "affected_files": affected_files,
        "session_edit_count": session["edit_count"],
        "session_id": session["session_id"],
    }

    # Write to JSONL log
    try:
        append_jsonl(LOG_FILE, json.dumps(entry, ensure_ascii=False))
    except Exception as e:
        print(f"[edit-tracker] JSONL write failed: {e}", file=sys.stderr)

    # Build additionalContext
    if syntax_ok is False:
        context = (
            f"[edit-tracker] ✗ SYNTAX ERROR in {rel_path}:\n"
            f"  {syntax_error}\n"
            f"  → この編集を修正してください"
        )
    elif syntax_ok is True:
        parts = [f"[edit-tracker] ✓ syntax OK"]
        if affected_files:
            parts.append(f"影響候補: {', '.join(affected_files[:3])}")
        parts.append(f"セッション内編集: {session['edit_count']}回目")
        context = " | ".join(parts)
    else:
        parts = [f"[edit-tracker] ✓ logged ({ext or 'unknown'})"]
        parts.append(f"セッション内編集: {session['edit_count']}回目")
        context = " | ".join(parts)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
