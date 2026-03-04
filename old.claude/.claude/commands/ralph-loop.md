---
description: "現在のセッションで Ralph Loop を開始する"
argument-hint: "PROMPT [--max-iterations N] [--completion-promise TEXT]"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh:*)"]
hide-from-slash-command-tool: "true"
---

# Ralph Loop コマンド

セットアップスクリプトを実行して Ralph ループを初期化:

```!
"${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh" $ARGUMENTS
```

タスクに取り組んでください。終了しようとすると、Ralph ループが次のイテレーションのために同じプロンプトを再度提供します。ファイルや git 履歴に残っている過去の作業を参照でき、反復的に改善できます。

重要なルール: 完了プロミスが設定されている場合、その内容が完全かつ疑いなく真である場合にのみ出力してください。ループから抜けるために偽のプロミスを出力しないでください。行き詰まったと感じたり、他の理由で終了すべきだと思っても同様です。ループは真の完了まで継続するよう設計されています。
