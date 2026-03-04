---
name: codex-review
description: |
  指定されたドキュメントファイルに対して Codex レビューループを実行する。
  APPROVED になるか最大反復回数に達するまで、各ラウンドで Claude がブロッキング問題を修正する。
  実装計画、設計ドキュメント、その他の構造化ドキュメントを Codex でレビューする際に使用する。
  トリガー: "Codex review", "codex-review", "review with Codex", "Codex loop"。
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
