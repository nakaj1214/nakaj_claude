---
name: proposal-quality-gate
description: >
  create-plan の中間ステップ。docs/implement/prompt.md（ユーザー依頼文）から
  構造化した docs/implement/proposal.md を生成し、品質チェック（7項目）を実行する。
  曖昧な記述・繰り返し失敗パターン・具体性不足を検出した場合は proposal.md をリライトする。
  create-plan の Step 0 で自動トリガーされる。
---

# Proposal Quality Gate

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 品質チェック基準・リライトテンプレート・判定ロジック

## 関連スキル

- [create-plan](../create-plan/SKILL.md): 計画作成（本スキルの後続）
- [implement-plans](../implement-plans/SKILL.md): 計画の実装
