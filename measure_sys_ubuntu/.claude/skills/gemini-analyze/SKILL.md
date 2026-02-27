# Gemini Analyze

Gemini CLI を tmux の左上ペイン(pane 0)で実行し、分析結果を回収する。

## Activation
- 「geminiで分析」
- 「/gemini-analyze」
- 「まず分析して」

## Instructions
- tmux セッション名は現在アタッチ中のセッション（例: ai-relay-<project>）を前提とする
- pane 0 = Gemini
- 出力が混ざらないように clear-history してから投げる

```bash
set -euo pipefail

SESSION_NAME="$(tmux display-message -p '#S')"

# pane割り当て
PANE_GEMINI="0.0"

source ~/.claude/scripts/tmux_pane_rpc.sh

# 入力は、直近のユーザー要求をそのまま使う想定（手で貼る運用でもOK）
REQUEST="${1:-"Analyze the user's latest request and output in FACTS/ROOT CAUSE/MIN TESTS/RECOMMENDED FIX format."}"

pane_rpc "${SESSION_NAME}" "${PANE_GEMINI}" "gemini \"${REQUEST}\"" '^>' 180 220
