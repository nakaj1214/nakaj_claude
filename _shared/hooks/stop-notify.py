#!/usr/bin/env python3
"""
Stop hook: Claude が応答を完了した際に Slack へ進捗通知を送信する。

Environment variables (set in .claude/settings.json env section):
  SLACK_BOT_TOKEN   - Slack Bot Token (xoxb-...) [preferred]
  SLACK_CHANNEL_ID  - Slack Channel ID (required when using Bot Token)
  SLACK_WEBHOOK_URL - Slack Incoming Webhook URL [fallback]

Usage (hook mode):
  echo '{"stop_reason": "end_turn"}' | python3 stop-notify.py

Usage (direct):
  python3 stop-notify.py --message "text" [--title "title"]
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "")


def _send_via_bot_token(text: str) -> bool:
    """Send message via Slack Web API (chat.postMessage). Returns True on success."""
    payload = json.dumps({"channel": CHANNEL_ID, "text": text}).encode("utf-8")
    try:
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {BOT_TOKEN}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return bool(result.get("ok"))
    except Exception as e:
        print(f"[stop-notify] Bot Token send failed: {e}", file=sys.stderr)
        return False


def _send_via_webhook(text: str) -> bool:
    """Send message via Incoming Webhook. Returns True on success."""
    payload = json.dumps({"text": text}).encode("utf-8")
    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except urllib.error.URLError as e:
        print(f"[stop-notify] Webhook send failed: {e}", file=sys.stderr)
        return False


def send_slack(message: str, title: str = "") -> bool:
    """Send a message to Slack. Uses Bot Token API if available, else Webhook."""
    text = f"*{title}*\n{message}" if title else message

    if BOT_TOKEN and CHANNEL_ID:
        return _send_via_bot_token(text)

    if WEBHOOK_URL:
        return _send_via_webhook(text)

    print("[stop-notify] No Slack credentials set, skipping.", file=sys.stderr)
    return False


def handle_hook() -> None:
    """Handle Stop hook input from Claude Code."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    stop_reason = data.get("stop_reason", "end_turn")

    # stop_reason が end_turn のときのみ通知（エラーや中断は除外）
    if stop_reason not in ("end_turn", "tool_use"):
        sys.exit(0)

    now = datetime.now().strftime("%H:%M")
    message = f"作業が完了しました。結果を確認してください。"

    send_slack(
        message=message,
        title=f":white_check_mark: Claude Code 応答完了 ({now})",
    )
    sys.exit(0)


def handle_cli() -> None:
    """Handle direct CLI invocation: --message TEXT [--title TITLE]"""
    args = sys.argv[1:]
    message = ""
    title = ""

    i = 0
    while i < len(args):
        if args[i] == "--message" and i + 1 < len(args):
            message = args[i + 1]
            i += 2
        elif args[i] == "--title" and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        else:
            i += 1

    if not message:
        print("Usage: stop-notify.py --message TEXT [--title TITLE]", file=sys.stderr)
        sys.exit(1)

    message = message.replace("\\n", "\n")
    title = title.replace("\\n", "\n")
    success = send_slack(message=message, title=title)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # If stdin has data and no CLI args → hook mode
    if len(sys.argv) == 1 and not sys.stdin.isatty():
        handle_hook()
    else:
        handle_cli()
