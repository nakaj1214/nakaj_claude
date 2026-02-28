---
name: create-plan
description: |
  Reads docs/implement/proposal.md and creates docs/implement/plan.md.
  Then runs a Codex review loop until APPROVED or max iterations reached.
metadata:
  short-description: Proposal → Plan with Codex review loop
---

# Create Plan

`docs/implement/proposal.md` を読み込み、`docs/implement/plan.md` を作成する。
その後 Codex によるレビューループを回し、APPROVED になるまで plan.md を更新し続ける。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 5ステップワークフロー（Read → Investigate → Create → Review Loop → Done）
- [evaluations/evals.json](evaluations/evals.json) — テストケース（作成推奨）
