---
name: propose-one
description: >
  docs/implement/prompt.md から課題を1つだけ選び、proposal → plan まで自動実行する。
  「1個ずつ確実に修正」のワークフローを強制し、複数課題を同時に扱うことで生じる混乱を防ぐ。
  「1つだけ実装して」「一個ずつ進めて」「propose-one」「最初のタスクだけ」と言われたときにトリガーする。
  create-plan の単一タスク版ラッパー。
---

# 単一課題の計画実行

prompt.md から課題を1つ選んで proposal → plan まで実行する。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 課題選択・proposal・plan 生成の手順
