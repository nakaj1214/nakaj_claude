"""Load environment variables with fallback to .claude/settings.json."""

import json
import os
import re
from pathlib import Path

_settings_env: dict | None = None


def _strip_jsonc(text: str) -> str:
    """Strip // comments and trailing commas from JSONC (JSON with Comments)."""
    # Remove // comments (but not inside strings)
    result = re.sub(r'(?<!["\w:])//.*', "", text)
    # Remove trailing commas before } or ]
    result = re.sub(r",\s*([}\]])", r"\1", result)
    return result


def _load_settings_env() -> dict:
    """Load env section from .claude/settings.json as fallback for missing env vars."""
    candidates = [
        Path(os.environ.get("CLAUDE_PROJECT_DIR", "")) / ".claude/settings.json",
        Path(__file__).resolve().parent.parent.parent / "settings.json",
    ]
    for path in candidates:
        if path.is_file():
            try:
                raw = path.read_text(encoding="utf-8")
                cleaned = _strip_jsonc(raw)
                data = json.loads(cleaned)
                return data.get("env", {})
            except Exception:
                continue
    return {}


def get(key: str) -> str:
    """Get env var from os.environ, falling back to settings.json env section."""
    global _settings_env
    if _settings_env is None:
        _settings_env = _load_settings_env()
    return os.environ.get(key, "") or _settings_env.get(key, "")
