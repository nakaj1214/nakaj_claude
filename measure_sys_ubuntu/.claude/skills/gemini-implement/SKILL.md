# Gemini Implement

Gemini CLI を tmux の左上ペイン(pane 0)で実行し、PATCH PLANに基づく実装(diff)を回収する。

## Activation
- 「geminiで実装」
- 「/gemini-implement」
- 「実装して」

## Instructions
- pane 0 = Gemini
- 出力は unified diff を推奨
- 最小差分、無関係な整形は禁止

```bash
set -euo pipefail

SESSION_NAME="$(tmux display-message -p '#S')"

PANE_GEMINI="0.0"

source ~/.claude/scripts/tmux_pane_rpc.sh

REQUEST="${1:-"Implement based on the approved PATCH PLAN. Output as unified diff. Minimal diff only; no unrelated formatting."}"

pane_rpc "${SESSION_NAME}" "${PANE_GEMINI}" "gemini \"${REQUEST}\"" '^>' 300 300
