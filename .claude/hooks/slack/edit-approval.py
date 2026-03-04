#!/usr/bin/env python3
"""
PreToolUse フック: Slack ベースの Edit/Write 承認（バックグラウンドエージェント用）。

Claude Code がファイルを編集または書き込もうとした際に Slack メッセージを送信し、
以下の方法で許可/拒否をポーリングする:
  - 絵文字リアクション: :white_check_mark:（許可） または :x:（拒否）
  - スレッド返信: "allow" / "deny" 等のキーワード（日本語にも対応）
  - Block Kit ボタン（Socket Mode デーモン実行中の場合）

必須環境変数（.claude/settings.json の env セクションで設定）:
  SLACK_BOT_TOKEN        - Slack Bot Token (xoxb-...)
  SLACK_CHANNEL_ID       - Slack Channel ID (C0XXXXXXX)
  SLACK_APPROVER_USER_ID - 承認者の Slack ユーザー ID (U0XXXXXXX, Bot ID ではない)

オプション:
  EDIT_APPROVAL_ENABLED  - "1" に設定して有効化（デフォルト: 無効）

終了コード:
  0: 許可（ツール実行を継続）
  2: ブロック（ツール実行を阻止）
"""

import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import timezone
from pathlib import Path
from typing import Optional

# --- Constants ---
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2
POLL_INTERVAL_SECONDS = 5
POLL_MAX_COUNT = 60  # 5s * 60 = max 5 minutes
PREVIEW_CHARS = 300  # Max chars for content preview in Slack message

# --- Load env with settings.json fallback ---
_HOOKS_DIR = Path(__file__).resolve().parent.parent  # .claude/hooks/
sys.path.insert(0, str(_HOOKS_DIR))
from lib.env import get as _env

# Environment variables
BOT_TOKEN = _env("SLACK_BOT_TOKEN")
CHANNEL_ID = _env("SLACK_CHANNEL_ID")
APPROVER_USER_ID = _env("SLACK_APPROVER_USER_ID")
EDIT_APPROVAL_ENABLED = _env("EDIT_APPROVAL_ENABLED") or "0"

# File paths
PROJECT_DIR = _env("CLAUDE_PROJECT_DIR")
_BASE = Path(PROJECT_DIR) if PROJECT_DIR else _HOOKS_DIR.parent.parent
AUDIT_LOG_PATH = _BASE / ".claude/logs/edit_approval_audit.jsonl"

# Socket Mode IPC
IPC_DIR = _BASE / ".claude/hooks/ipc"
DAEMON_PID_FILE = IPC_DIR / "daemon.pid"
IPC_POLL_INTERVAL_SECONDS = 0.5
IPC_TIMEOUT_SECONDS = 300  # 5 minutes

ALLOW_REACTION = "white_check_mark"
DENY_REACTION = "x"
ALLOW_KEYWORDS: frozenset = frozenset({"allow", "ok", "yes", "y", "承認", "許可"})
DENY_KEYWORDS: frozenset = frozenset({"deny", "no", "ng", "n", "拒否", "却下", "block"})


def write_audit_log(
    file_path: str,
    tool_name: str,
    decision: str,
    trigger: str,
    approver_user: Optional[str] = None,
    thread_ts: Optional[str] = None,
) -> None:
    """Append one record to the edit approval audit log."""
    try:
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.datetime.now(timezone.utc).isoformat(),
            "file_path": file_path,
            "tool_name": tool_name,
            "decision": decision,
            "trigger": trigger,
            "approver_user": approver_user,
            "thread_ts": thread_ts,
        }
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[edit_approval] Failed to write audit log: {e}", file=sys.stderr)


def slack_api_request(method: str, payload: dict) -> Optional[dict]:
    """Call Slack Web API with retry on 429. Returns response dict or None on failure."""
    url = f"https://slack.com/api/{method}"
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {BOT_TOKEN}",
    }
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("ok"):
                    return result
                print(
                    f"[edit_approval] Slack API {method} error: {result.get('error')}",
                    file=sys.stderr,
                )
                return None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", RETRY_WAIT_SECONDS))
                time.sleep(retry_after)
                continue
            print(f"[edit_approval] HTTP error {e.code}: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"[edit_approval] Request failed: {e}", file=sys.stderr)
            return None
    return None


def truncate(text: str, max_chars: int = PREVIEW_CHARS) -> str:
    """Truncate text and append ellipsis if too long."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"


def build_edit_diff(old_str: str, new_str: str, context_lines: int = 3) -> str:
    """Build a compact diff showing only changed lines with context.

    Instead of showing full old/new strings (which may be large),
    find the actual differences and show a few lines of context around them.
    """
    old_lines = old_str.splitlines()
    new_lines = new_str.splitlines()

    import difflib

    diff = list(difflib.unified_diff(
        old_lines, new_lines, lineterm="", n=context_lines
    ))

    if not diff:
        return "(変更なし)"

    # Skip the --- / +++ header lines, show only hunks
    result_lines = []
    for line in diff[2:]:  # skip --- and +++ headers
        if len("\n".join(result_lines)) > PREVIEW_CHARS:
            result_lines.append("…")
            break
        result_lines.append(line)

    return "\n".join(result_lines) if result_lines else "(変更なし)"


def build_notification_text(tool_name: str, file_path: str, tool_input: dict) -> str:
    """Build Slack notification text showing file path and change preview."""
    mention = f"<@{APPROVER_USER_ID}> " if APPROVER_USER_ID else ""
    icon = ":pencil2:" if tool_name == "Edit" else ":page_facing_up:"

    lines = [f"{mention}{icon} *ファイル編集承認待ち* (`{tool_name}`)", f"`{file_path}`"]

    if tool_name == "Edit":
        old_str = tool_input.get("old_string", "")
        new_str = tool_input.get("new_string", "")
        diff_text = build_edit_diff(old_str, new_str)
        lines.append(f"*差分:*\n```{diff_text}```")
    elif tool_name in ("Write", "NotebookEdit"):
        content = tool_input.get("content", tool_input.get("new_source", ""))
        total_lines = content.count("\n") + 1
        lines.append(f"*新規ファイル ({total_lines}行):*\n```{truncate(content)}```")

    lines.append(":white_check_mark: で承認 / :x: で拒否（リアクション or スレッド返信: allow/deny）")
    return "\n".join(lines)


def is_daemon_running() -> bool:
    """Return True if the Socket Mode daemon pid file exists."""
    return DAEMON_PID_FILE.exists()


def send_approval_request_polling(text: str) -> Optional[dict]:
    """Send plain text approval request (polling mode)."""
    return slack_api_request(
        "chat.postMessage",
        {"channel": CHANNEL_ID, "text": text},
    )


def send_approval_request_blocks(text: str) -> Optional[dict]:
    """Send Block Kit approval request (Socket Mode IPC path)."""
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "承認"},
                    "style": "primary",
                    "action_id": "approve",
                    "value": "approve",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "拒否"},
                    "style": "danger",
                    "action_id": "deny",
                    "value": "deny",
                },
            ],
        },
    ]
    return slack_api_request(
        "chat.postMessage",
        {"channel": CHANNEL_ID, "text": text, "blocks": blocks},
    )


def wait_for_ipc_decision(message_ts: str) -> tuple:
    """Wait for Socket Mode daemon to write a decision via file-based IPC."""
    IPC_DIR.mkdir(parents=True, exist_ok=True)
    pending_file = IPC_DIR / f"{message_ts}.pending"
    decision_file = IPC_DIR / f"{message_ts}.decision"
    pending_file.write_text(message_ts)
    deadline = time.time() + IPC_TIMEOUT_SECONDS
    try:
        while time.time() < deadline:
            if decision_file.exists():
                decision = decision_file.read_text().strip()
                if decision in ("allow", "deny"):
                    return decision, "daemon", message_ts
            time.sleep(IPC_POLL_INTERVAL_SECONDS)
        return "timeout", None, None
    finally:
        pending_file.unlink(missing_ok=True)
        decision_file.unlink(missing_ok=True)


def poll_for_decision(message_ts: str) -> tuple:
    """Poll Slack for emoji reaction or thread reply decision."""
    for _ in range(POLL_MAX_COUNT):
        time.sleep(POLL_INTERVAL_SECONDS)
        # Check reactions
        reaction_result = slack_api_request(
            "reactions.get",
            {"channel": CHANNEL_ID, "timestamp": message_ts, "full": True},
        )
        if reaction_result:
            reactions = reaction_result.get("message", {}).get("reactions", [])
            for reaction in reactions:
                name = reaction.get("name", "")
                users = reaction.get("users", [])
                if APPROVER_USER_ID not in users:
                    continue
                if name == ALLOW_REACTION:
                    return "allow", APPROVER_USER_ID, message_ts
                elif name == DENY_REACTION:
                    return "deny", APPROVER_USER_ID, message_ts
        # Check thread replies
        replies_result = slack_api_request(
            "conversations.replies",
            {"channel": CHANNEL_ID, "ts": message_ts},
        )
        if replies_result:
            messages = replies_result.get("messages", [])
            for msg in messages[1:]:
                if msg.get("user") != APPROVER_USER_ID:
                    continue
                text = msg.get("text", "").strip().lower()
                if text in ALLOW_KEYWORDS:
                    return "allow", APPROVER_USER_ID, message_ts
                elif text in DENY_KEYWORDS:
                    return "deny", APPROVER_USER_ID, message_ts
    return "timeout", None, None


def update_message_status(message_ts: str, original_text: str, status_text: str) -> None:
    """Update the original approval message to show final status."""
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": original_text}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": status_text}]},
    ]
    slack_api_request(
        "chat.update",
        {"channel": CHANNEL_ID, "ts": message_ts, "text": original_text, "blocks": blocks},
    )


def main() -> None:
    """Main entry point: read PreToolUse hook input and decide allow/block."""
    # EDIT_APPROVAL_ENABLED=1 で有効化（デフォルト無効）
    if EDIT_APPROVAL_ENABLED != "1":
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "NotebookEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", tool_input.get("notebook_path", ""))
    if not file_path:
        sys.exit(0)

    # Slack credentials not set: skip
    if not BOT_TOKEN or not CHANNEL_ID:
        write_audit_log(file_path, tool_name, "skip", "token_not_set")
        sys.exit(0)

    if not APPROVER_USER_ID:
        write_audit_log(file_path, tool_name, "deny", "approver_not_set")
        print("[edit_approval] SLACK_APPROVER_USER_ID が未設定のため承認をブロック", file=sys.stderr)
        sys.exit(2)

    notification_text = build_notification_text(tool_name, file_path, tool_input)
    daemon_running = is_daemon_running()

    if daemon_running:
        response = send_approval_request_blocks(notification_text)
    else:
        response = send_approval_request_polling(notification_text)

    if not response:
        write_audit_log(file_path, tool_name, "deny", "error")
        print("[edit_approval] Slack API error: blocking (fail-closed)", file=sys.stderr)
        sys.exit(2)

    thread_ts = response.get("ts", "")

    if daemon_running:
        decision, approver_user, message_ts = wait_for_ipc_decision(thread_ts)
    else:
        decision, approver_user, message_ts = poll_for_decision(thread_ts)

    if decision == "allow":
        update_message_status(thread_ts, notification_text, ":white_check_mark: 承認済み")
        write_audit_log(file_path, tool_name, "allow", "slack", approver_user, thread_ts)
        sys.exit(0)
    elif decision == "deny":
        update_message_status(thread_ts, notification_text, ":x: 拒否されました")
        write_audit_log(file_path, tool_name, "deny", "slack", approver_user, thread_ts)
        sys.exit(2)
    else:  # timeout
        update_message_status(
            thread_ts, notification_text,
            ":hourglass: タイムアウト（5分）: 編集をブロックしました"
        )
        write_audit_log(file_path, tool_name, "timeout", "timeout", None, thread_ts)
        sys.exit(2)


if __name__ == "__main__":
    main()
