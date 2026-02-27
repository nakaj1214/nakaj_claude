# Codex Review

Codex CLI を tmux の左下ペイン(pane 2)で実行し、レビュー結果を回収する。

## Activation
- 「codexにレビュー」
- 「/codex-review」
- 「レビューして」

## Instructions
- pane 2 = Codex
- Must/Should/Could 形式で返すように依頼する
- 設計レビューは「全文コード」ではなく、DECISIONS/PATCH PLAN/TEST PLAN中心で渡す

```bash
set -euo pipefail

SESSION_NAME="$(tmux display-message -p '#S')"

# pane割り当て
PANE_CODEX="0.2"

source ~/.claude/scripts/tmux_pane_rpc.sh

REQUEST="${1:-"Review the previous design in Must/Should/Could format. Must items require rationale and acceptance criteria."}"

# Codexの入力待ち検出（典型: ›）
pane_rpc "${SESSION_NAME}" "${PANE_CODEX}" "${REQUEST}" '^›' 240 260
