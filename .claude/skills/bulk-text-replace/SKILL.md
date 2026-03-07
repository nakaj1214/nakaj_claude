---
name: bulk-text-replace
description: >
  複数ファイルにまたがる同一テキストを一括置換するスキル。
  Grep で対象ファイルを特定し、sed または Python スクリプトで一括置換してから差分を確認する。
  「〜を全ファイルで〜に変更して」「複数ファイルの○○を一括で置換して」「横断置換」「全体置換」に使用する。
  ルール・スキルファイルの用語変更、設定値の一括更新、命名規則変更後のリネームに特に有効。
---

# 一括テキスト置換

複数ファイルにまたがる同一テキストを安全に一括置換する。
個別 Edit を繰り返す代わりに、grep で対象を確認してから sed/perl で一括実行。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 置換フロー・安全確認・実行コマンド
- [evaluations/evals.json](evaluations/evals.json) — テストケース
