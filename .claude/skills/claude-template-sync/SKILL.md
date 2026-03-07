---
name: claude-template-sync
description: >
  .claude_remote（テンプレートリポジトリ）から .claude（プロジェクト設定）へのファイル同期を行うスキル。
  改行コードのみの差分や空白差分を自動フィルタし、実質的な変更のあるファイルだけを更新する。
  「テンプレートを同期して」「.claude_remoteの変更を取り込んで」「claude-template-syncして」と言われたときにトリガーする。
---

# Claude テンプレート同期

`.claude_remote/` の更新を `.claude/` に安全に取り込む。
実質的な差分のみを対象に、改行コード差分・空白のみの変更をスキップしながら同期する。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 同期フロー・差分フィルタ・競合解決
- [evaluations/evals.json](evaluations/evals.json) — テストケース
