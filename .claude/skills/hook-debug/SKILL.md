---
name: hook-debug
description: >
  Claude Code フックの動作確認・デバッグを行うスキル。
  フックが動かない・エラーが出る・スキップされる・予期しない動作をするときに使う。
  「フックが動かない」「hookが効かない」「settings.jsonを確認して」「フックのデバッグ」と言われたとき、
  またはフック実行でエラーメッセージが出たときにトリガーする。
---

# フックデバッグ

Claude Code フックの問題を体系的に診断・修正する。
echo テストで動作確認 → settings.json 検証 → Python スクリプトの import チェックの順で進める。

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 診断フロー・確認コマンド・よくあるエラーと対処
- [evaluations/evals.json](evaluations/evals.json) — テストケース
