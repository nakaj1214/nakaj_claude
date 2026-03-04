---
name: create-plan
description: |
  Reads docs/implement/proposal.md and creates docs/implement/plan.md.
  Then runs a Codex review loop (via codex-review skill) until APPROVED or max iterations reached.
metadata:
  short-description: Proposal → Plan with Codex review loop
  dependencies:
    - codex-review
---

# Create Plan

`docs/implement/proposal.md` を読み込み、`docs/implement/plan.md` を作成する。
その後 `codex-review` スキルを呼び出してレビューループを実行し、APPROVED になるまで plan.md を更新し続ける。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 5ステップワークフロー（Read → Investigate → Create → Review Loop → Done）
- [codex-review](../codex-review/SKILL.md) — Codex レビューループスキル（Step 4 で使用）
- [evaluations/evals.json](evaluations/evals.json) — テストケース（作成推奨）
