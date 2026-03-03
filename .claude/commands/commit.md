---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: git コミットを作成する
---

## コンテキスト

- 現在の git ステータス: !`git status`
- 現在の git diff（ステージ済みおよび未ステージの変更）: !`git diff HEAD`
- 現在のブランチ: !`git branch --show-current`
- 直近のコミット: !`git log --oneline -10`

## タスク

上記の変更に基づいて、単一の git コミットを作成する。

1つのレスポンスで複数のツールを呼び出す機能がある。単一のメッセージでステージングとコミットの作成を実行すること。他のツールを使用したり、他のことをしないこと。これらのツール呼び出し以外のテキストやメッセージを送信しないこと。
