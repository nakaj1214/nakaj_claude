---
name: codex-review
description: |
  Runs a Codex review loop on a specified document file.
  Iterates until APPROVED or max iterations reached, with Claude fixing blocking issues each round.
  Use when reviewing implementation plans, design docs, or any structured document with Codex.
  Trigger on: "Codex review", "codex-review", "review with Codex", "Codex loop".
metadata:
  short-description: Codex review loop for any document
---

# Codex Review

指定されたドキュメントファイルに対して Codex レビューループを実行する。
APPROVED になるまで（または最大反復回数に達するまで）、Codex レビュー → Claude 修正 を繰り返す。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

| ファイル | 内容 | ロードタイミング |
|--------|------|------------|
| [INSTRUCTIONS.md](INSTRUCTIONS.md) | ワークフローと詳細指示 | スキル起動時 |
