---
name: review-to-plan
description: >
  docs/implement/review.md のレビュー指摘事項を読み取り、
  docs/implement/plan.md の該当箇所を更新する。
  「レビューを反映して」「review.md の指摘を修正」「レビュー→計画反映」
  と言われたときにトリガーする。
metadata:
  short-description: review.md の指摘 → plan.md に反映
---

# Review to Plan

`docs/implement/review.md` のレビュー指摘事項を `docs/implement/plan.md` に反映する。

レビュー → 計画修正の標準フローを自動化し、手動での転記漏れを防ぐ。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## 想定フロー

```
plan.md（実装計画書）
    ↓  レビュー実施
review.md（指摘事項）
    ↓  /review-to-plan
plan.md（指摘を反映した改訂版）
```

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 反映手順・分類基準・差分報告テンプレート

## 関連スキル

- [create-plan](../create-plan/SKILL.md): plan.md の作成（前工程）
- [implement-plans](../implement-plans/SKILL.md): plan.md の実装（後工程）
