"""
hooks/lib/claude_p.py

claude -p（非対話モード）を呼び出すユーティリティ。
タイムアウト・エラーハンドリングを統一する。

使い方:
    from lib.claude_p import run

    result = run("Summarize this: " + text, timeout=120)
"""

import subprocess


def run(prompt: str, timeout: int = 120) -> str:
    """
    claude -p でプロンプトを実行してテキストを返す。

    Parameters
    ----------
    prompt : str
        claude -p に渡すプロンプト（トランスクリプト含む全文）
    timeout : int
        タイムアウト秒数（デフォルト 120）

    Returns
    -------
    str
        生成されたテキスト。エラー時は "(エラーメッセージ)" を返す。
    """
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
        return f"(生成に失敗しました: returncode={result.returncode})\n```\n{result.stderr[:500]}\n```"

    except subprocess.TimeoutExpired:
        return f"(生成がタイムアウトしました: {timeout}秒)"
    except FileNotFoundError:
        return "(claude CLI が見つかりません。PATH を確認してください)"
    except Exception as e:
        return f"(予期しないエラー: {e})"
