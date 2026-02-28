#!/usr/bin/env python3
"""
PreCompact hook: 自動コンパクション直前にハンドオーバーとスキル候補レポートを生成する。

Claude Code が会話を自動圧縮する直前に発火し:
1. 会話トランスクリプトを intact なうちに読み込む
2. claude -p (並列) でハンドオーバー要約とパターン分析を生成
3. .claude/docs/memory/ に以下を保存:
   - HANDOVER-YYYY-MM-DD.md      — 次セッションへの引き継ぎ
   - SKILL-SUGGESTIONS-YYYY-MM-DD.md — 自動化候補レポート

matcher: "auto" = 自動コンパクションのみ（手動 /compact は除外）

Settings.json への登録例:
  {
    "hooks": {
      "PreCompact": [
        {
          "matcher": "auto",
          "hooks": [
            {
              "type": "command",
              "command": "python C:/path/to/_shared/hooks/pre-compact-handover.py"
            }
          ]
        }
      ]
    }
  }

Environment variables (optional):
  HANDOVER_MEMORY_DIR - 出力先ディレクトリ (default: .claude/docs/memory)
"""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

MEMORY_DIR = os.environ.get("HANDOVER_MEMORY_DIR", ".claude/docs/memory")

HANDOVER_PROMPT = """\
You are generating a handover document for the next Claude session.
Based on the conversation transcript provided, create a concise but complete handover document in Markdown.

Use this exact structure:

# Handover — {date}

## Session Summary
(1-3 sentences: purpose and outcome)

## Completed Work
- (bullet list of completed tasks)

## Incomplete Work
- [ ] (task) — (current status and next step)

## Key Decisions
| Decision | Reason |
|----------|--------|
| ... | ... |

## Issues & Solutions
(problems encountered and how they were resolved)

## Gotchas & Notes
(important things to watch out for)

## Next Steps
1. (highest priority)
2. ...

## Important Files
| File | Role | Status |
|------|------|--------|
| ... | ... | changed/new/reviewed |

Rules:
- Write in the same language as the conversation (Japanese if the conversation is in Japanese)
- Be specific and actionable — the next Claude should be able to resume work immediately
- Keep it concise; skip sections that have nothing to report
"""

SUGGESTIONS_PROMPT = """\
You are analyzing a Claude Code conversation transcript to identify automation opportunities.

Based on the transcript, find recurring patterns and gaps that could be improved with new skills, agents, or hooks.

Use this exact structure:

# スキル候補レポート — {date}

## 検出されたパターン
(会話中に繰り返し登場したタスク・質問・操作を箇条書きで)

## スキル候補
| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| ... | (ユーザーが言いそうなフレーズ) | ... | 高/中/低 |

## エージェント候補
| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| ... | ... | ... | 高/中/低 |

## フック候補
| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| ... | ... | ... | 高/中/低 |

## 観察事項
(パターンとして検出されたが自動化優先度が低いもの)

Rules:
- Write in Japanese
- Only suggest if the pattern appeared 2+ times OR is clearly high value
- Be specific: include example trigger phrases and expected output
- Skip sections with nothing to report
- If no meaningful patterns found, write "このセッションでは特筆すべきパターンは検出されませんでした。"
"""


def read_transcript(transcript_path: str) -> str:
    """トランスクリプトを読み込み、テキスト形式に変換する。"""
    try:
        with open(transcript_path, encoding="utf-8") as f:
            data = json.load(f)

        lines = []
        for entry in data:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")

            if isinstance(content, list):
                texts = []
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get("type", "")
                    if btype == "text":
                        texts.append(block.get("text", ""))
                    elif btype == "tool_use":
                        name = block.get("name", "")
                        inp = block.get("input", {})
                        summary = ", ".join(
                            f"{k}={str(v)[:80]}" for k, v in inp.items()
                            if k in ("file_path", "command", "pattern", "path", "old_string")
                        )
                        texts.append(f"[Tool:{name} {summary}]")
                    elif btype == "tool_result":
                        rc = block.get("content", "")
                        if isinstance(rc, list):
                            for r in rc:
                                if isinstance(r, dict) and r.get("type") == "text":
                                    texts.append(f"[Result: {r.get('text', '')[:300]}]")
                        else:
                            texts.append(f"[Result: {str(rc)[:300]}]")
                content = " ".join(texts)

            lines.append(f"{role.upper()}: {content}")

        return "\n\n".join(lines)

    except Exception as e:
        return f"(transcript read error: {e})"


def _run_claude(prompt: str, timeout: int = 120) -> str:
    """claude -p を呼び出して結果テキストを返す。"""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return f"(生成に失敗しました)\n```\n{result.stderr[:500]}\n```"
    except subprocess.TimeoutExpired:
        return "(生成がタイムアウトしました)"
    except FileNotFoundError:
        return "(claude CLI が見つかりません。PATH を確認してください)"
    except Exception as e:
        return f"(エラー: {e})"


def generate_handover(transcript: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    prompt = HANDOVER_PROMPT.format(date=date)
    content = _run_claude(f"{prompt}\n\n---\n\nTRANSCRIPT:\n\n{transcript}")
    if content.startswith("("):
        return f"# Handover — {date}\n\n{content}"
    return content


def generate_suggestions(transcript: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    prompt = SUGGESTIONS_PROMPT.format(date=date)
    content = _run_claude(f"{prompt}\n\n---\n\nTRANSCRIPT:\n\n{transcript}")
    if content.startswith("("):
        return f"# スキル候補レポート — {date}\n\n{content}"
    return content


def save_doc(content: str, filename: str) -> str:
    Path(MEMORY_DIR).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(MEMORY_DIR, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if data.get("trigger") != "auto":
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    if not transcript_path or not os.path.exists(transcript_path):
        print("[pre-compact-handover] transcript not found, skipping.", file=sys.stderr)
        sys.exit(0)

    transcript = read_transcript(transcript_path)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # ハンドオーバーとスキル候補を並列生成
    tasks = {
        "handover": (generate_handover, f"HANDOVER-{date_str}.md"),
        "suggestions": (generate_suggestions, f"SKILL-SUGGESTIONS-{date_str}.md"),
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(fn, transcript): filename
            for fn, filename in tasks.values()
        }
        for future in as_completed(futures):
            filename = futures[future]
            content = future.result()
            path = save_doc(content, filename)
            print(f"[pre-compact-handover] Saved: {path}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
