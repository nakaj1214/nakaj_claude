---
allowed-tools: Bash(git checkout --branch:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
description: コミット、プッシュ、PR を作成する
---

## コンテキスト

- 現在の git ステータス: !`git status`
- 現在の git diff（ステージ済みおよび未ステージの変更）: !`git diff HEAD`
- 現在のブランチ: !`git branch --show-current`

## タスク

上記の変更に基づいて:

1. main ブランチにいる場合は新しいブランチを作成する
2. 適切なメッセージで単一のコミットを作成する
3. ブランチを origin にプッシュする
4. `gh pr create` を使ってプルリクエストを作成する
5. 1つのレスポンスで複数のツールを呼び出す機能がある。上記のすべてを単一のメッセージで実行すること。他のツールを使用したり、他のことをしないこと。これらのツール呼び出し以外のテキストやメッセージを送信しないこと。
