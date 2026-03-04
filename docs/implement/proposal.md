# 実装要件書

> このファイルは create-plan の入力です。
> 各要件は「具体的な Before/After」「対象ファイル」「受入条件」を含めてください。

---

## 概要

Slack通知の過剰送信を防ぎ、重要な通知のみを送信するように修正する。
現状のコードには以下の問題がある:

### 検出した問題

| # | 問題 | 原因ファイル | 詳細 |
|---|------|-------------|------|
| 1 | 完了通知が毎ターン発火する | `stop-notify.py:95` | `stop_reason` が `end_turn` と `tool_use` の両方で発火。`end_turn` は Claude の応答ごとに発生するため、タスク完了ではなく毎ターン通知が飛ぶ |
| 2 | サブエージェント終了でも発火する | `stop-notify.py:95` | Stop hook はサブエージェント終了時にも呼ばれる可能性がある。フィルタリングなし |
| 3 | ls コマンドで承認通知が飛ぶ（潜在的） | `slack_approval.py` | `approval_skip_patterns.txt` に `skip:ls` があるので **現状では問題なし**。ただし Hook が settings.json に未登録のため未検証 |

> **結論**: 問題1・2 は `stop-notify.py` に存在する。問題3 はパターンファイルで対策済みだが動作未検証。

---

## 要件一覧

### REQ-001: stop-notify.py の通知フィルタリング（最重要）

- **対象ファイル**: `.claude/hooks/stop-notify.py`
- **Before（現状）**: `stop_reason` が `end_turn` または `tool_use` のすべてで通知を送信する（95行目）。Claude の応答ターンごとに Slack 通知が飛ぶ
- **After（期待）**: 以下の条件で**のみ**完了通知を送信する:
  - `stop_reason` が `end_turn` のとき（`tool_use` は除外）
  - 最後のユーザーメッセージから一定以上の処理が行われたとき（単純な質問応答では通知しない）
  - **または**: Stop hook の代わりにスキル（create-plan, implement-plans）の最終ステップで明示的に `stop-notify.py --message` を呼ぶ方式に変更
- **受入条件**:
  - Claude が応答するたびに通知が飛ばない
  - create-plan / implement-plans の完了時には通知が届く
  - 単純な質問応答（「こんにちは」等）では通知しない

### REQ-002: サブエージェント完了時の通知抑制

- **対象ファイル**: `.claude/hooks/stop-notify.py`
- **Before（現状）**: Stop hook がサブエージェント（Task ツール）の終了時にも発火する可能性がある
- **After（期待）**: メインセッションの完了時のみ通知し、サブエージェントの終了では通知しない
- **受入条件**:
  - サブエージェント実行中に Slack 通知が飛ばない
  - メインの作業完了時には通知が届く
- **備考**: Stop hook の stdin データにサブエージェント判別情報があるか要調査。なければ REQ-001 の「明示呼び出し方式」で解決

### REQ-003: settings.json の Hook 登録（前回の REQ-001〜003 を統合）

- **対象ファイル**: `.claude/settings.json`
- **Before（現状）**: PreToolUse hook と Stop hook が settings.json に未登録のため、全スクリプトが発動しない
- **After（期待）**: 必要な Hook が登録され、各スクリプトが適切なタイミングで発動する
- **受入条件**:
  - PreToolUse > Bash: `slack_approval.py` が登録済み
  - PreToolUse > ExitPlanMode|AskUserQuestion: `notify-slack.py` が登録済み
  - Stop（またはスキル内明示呼び出し）: `stop-notify.py` が適切に配置
  - `ls`, `git status` 等の安全なコマンドでは承認通知が飛ばない

### REQ-004: 環境変数の設定

- **対象ファイル**: `.claude/settings.json`（env セクション）
- **Before（現状）**: SLACK_BOT_TOKEN 等が未設定で全スクリプトが自動スキップ（exit 0）
- **After（期待）**: 環境変数が設定され Slack API が動作する
- **受入条件**:
  - SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SLACK_APPROVER_USER_ID が設定済み
  - テストメッセージが Slack に届く
- **備考**: ユーザーから値を提供してもらう

---

## 前回の要件で継続するもの

> 前回の proposal.md の REQ-004〜007 は本要件の前提として引き続き有効。
> ただし今回のスコープは「通知の過剰送信防止」が主題。

- 計画書なし直接編集時の承認フロー（edit-approval.py の改修）
- ファイル削除時の承認フロー（slack_approval.py + patterns で対応済み）
- Socket Mode デーモン管理の改善

---

## 保留中（今回のスコープ外）

- skills 以外の重複・競合・下位互換ファイルの調査と統合
- .claude の100点満点評価と改善提案
- _shared/ フォルダの .claude への統合・移植
- .claude/STRUCTURE.md の作成
