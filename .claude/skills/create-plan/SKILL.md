---
name: create-plan
description: |
  docs/implement/prompt.md（ユーザーの依頼文）を読み込み、構造化した docs/implement/proposal.md を生成し、
  そこから docs/implement/plan.md を作成する。plan.md 作成後に停止する。
metadata:
  short-description: Prompt → Proposal → Plan
  dependencies:
    - proposal-quality-gate
---

# Create Plan

`docs/implement/prompt.md`（ユーザーの依頼文）を読み込み、構造化した `docs/implement/proposal.md` を生成し、
そこから `docs/implement/plan.md` を作成する。plan.md 作成後に停止する。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — Prompt → Proposal → Plan ワークフロー
- [proposal-quality-gate](../proposal-quality-gate/SKILL.md) — proposal.md の品質チェック（Step 0 で使用）
- [evaluations/evals.json](evaluations/evals.json) — テストケース（作成推奨）
