# スキル / フック実行ルール

## スキル指示を変更しない

INSTRUCTIONS.md 内のコマンド・モデル名・パラメータはそのまま使用する。「認識できない」は変更理由にならない。おかしいと思ったらユーザーに確認。

## Slack フックの動作を理解する

Slack 通知・承認フックは `settings.json` に登録済みで **有効** である。Claude がこれらを無効化・スキップしてはならない。

- **`slack_approval.py`**: Bash コマンド実行時に `approval_skip_patterns.txt` で自動分類される
  - `skip` コマンド（grep, cat, ls, git status 等）: Slack 通知なしで自動実行
  - `require` コマンド（rm, chmod, kill, sudo 等）: Slack に承認リクエストを送信
  - 未定義コマンド: デフォルトで承認リクエスト（fail-safe）
- **`notify-slack.py`**: ExitPlanMode / AskUserQuestion 時にユーザーへ通知
- **`stop-notify.py`**: Claude の作業完了時にユーザーへ通知
- **Codex MCP** (`mcp__codex__codex`): Bash ツール経由ではないため承認不要（自動実行）

## スキル内でフックスクリプトを直接呼ぶ場合

スキルの INSTRUCTIONS.md がフックスクリプト（例: `edit-approval.py`）の直接実行を指示しているが、
そのスクリプトが `settings.json` のフックに登録されていない場合は、黙ってスキップする（承認不要）。

## ファイルは常に最新を読む

- `prompt.md` 等は毎回再読み込み（キャッシュに頼らない）
- `<!-- -->` コメントアウト = 完了/延期。非コメント行 = アクティブ要件
