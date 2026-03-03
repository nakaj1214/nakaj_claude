---
description: リモートで削除済みの [gone] マーク付きローカル git ブランチを、関連するワークツリーの削除を含めてすべてクリーンアップする。
---

## タスク

リモートリポジトリで削除された古いローカルブランチをクリーンアップするために、以下の bash コマンドを実行する。

## 実行するコマンド

1. **まず、ブランチを一覧表示して [gone] ステータスのものを特定する**
   以下のコマンドを実行する:
   ```bash
   git branch -v
   ```

   注意: '+' プレフィックスが付いたブランチには関連するワークツリーがあり、削除前にワークツリーを削除する必要がある。

2. **次に、[gone] ブランチに対して削除が必要なワークツリーを特定する**
   以下のコマンドを実行する:
   ```bash
   git worktree list
   ```

3. **最後に、ワークツリーを削除し [gone] ブランチを削除する（通常ブランチとワークツリーブランチの両方に対応）**
   以下のコマンドを実行する:
   ```bash
   # Process all [gone] branches, removing '+' prefix if present
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     echo "Processing branch: $branch"
     # Find and remove worktree if it exists
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ ! -z "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
       echo "  Removing worktree: $worktree"
       git worktree remove --force "$worktree"
     fi
     # Delete the branch
     echo "  Deleting branch: $branch"
     git branch -D "$branch"
   done
   ```

## 期待される動作

これらのコマンドを実行すると、以下が行われる:

- すべてのローカルブランチとそのステータスの一覧を表示
- [gone] ブランチに関連するワークツリーを特定して削除
- [gone] マーク付きの全ブランチを削除
- 削除されたワークツリーとブランチについてフィードバックを提供

[gone] マークのブランチがない場合は、クリーンアップの必要がなかったことを報告する。
