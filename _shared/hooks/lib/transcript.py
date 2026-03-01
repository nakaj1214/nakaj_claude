"""
hooks/lib/transcript.py

Claude Code の JSONL トランスクリプトを読み込み、
テキスト形式に変換するユーティリティ。

使い方:
    from lib.transcript import read

    text = read("/path/to/transcript.jsonl")
"""

import json


def read(path: str, max_result_len: int = 300) -> str:
    """
    JSONL トランスクリプトを読み込み、人間が読めるテキストに変換する。

    Parameters
    ----------
    path : str
        トランスクリプトファイルのパス（.jsonl）
    max_result_len : int
        ToolResult の切り詰め文字数（デフォルト 300）

    Returns
    -------
    str
        "ROLE: content" 形式の文字列（段落区切り）
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return f"(transcript read error: {e})"

    lines = []
    for entry in data:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")

        if isinstance(content, list):
            texts = _parse_content_blocks(content, max_result_len)
            content = " ".join(texts)

        lines.append(f"{role.upper()}: {content}")

    return "\n\n".join(lines)


def _parse_content_blocks(blocks: list, max_result_len: int) -> list[str]:
    texts = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        btype = block.get("type", "")

        if btype == "text":
            texts.append(block.get("text", ""))

        elif btype == "tool_use":
            name = block.get("name", "")
            inp = block.get("input", {})
            summary = ", ".join(
                f"{k}={str(v)[:80]}"
                for k, v in inp.items()
                if k in ("file_path", "command", "pattern", "path", "old_string")
            )
            texts.append(f"[Tool:{name} {summary}]")

        elif btype == "tool_result":
            rc = block.get("content", "")
            if isinstance(rc, list):
                for r in rc:
                    if isinstance(r, dict) and r.get("type") == "text":
                        texts.append(f"[Result: {r.get('text', '')[:max_result_len]}]")
            else:
                texts.append(f"[Result: {str(rc)[:max_result_len]}]")

    return texts
