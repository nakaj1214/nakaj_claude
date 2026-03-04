## 実装計画: Slack通知の過剰送信防止

### 目的

Slack通知の過剰送信を防ぎ、重要な通知のみを送信する。
現状 `stop-notify.py` が毎ターン発火している根本原因を修正し、settings.json に必要な Hook を登録する。

### スコープ

- 含むもの:
  - stop-notify.py の通知ロジック修正（REQ-001, REQ-002）
  - settings.json への Hook 登録（REQ-003）
  - 環境変数テンプレートの追加（REQ-004）
- 含まないもの:
  - edit-approval.py の改修（前回要件の継続、今回スコープ外）
  - Socket Mode デーモンの改善
  - skills 以外のファイル統合

### 根本原因分析

**調査で判明した事実:**

| 項目 | 事実 |
|------|------|
| Stop hook の stdin | `stop_reason` フィールドは**存在しない**。実際は `session_id`, `hook_event_name`, `stop_hook_active`, `last_assistant_message` 等 |
| `stop-notify.py:92` | `data.get("stop_reason", "end_turn")` → 常にデフォルト値 `"end_turn"` が返る |
| `stop-notify.py:95` | `if stop_reason not in ("end_turn", "tool_use")` → `"end_turn"` は含まれるため、この条件は**常に通過** |
| サブエージェント | サブエージェント終了は `SubagentStop` イベント（`Stop` とは別）。`Stop` にのみ登録すればサブエージェントでは発火しない |
| settings.json | 現在 PreToolUse / Stop フックは**未登録**。登録すれば即座に動作開始 |

**結論:** `stop_reason` という存在しないフィールドに依存した条件分岐が根本原因。さらに、Stop hook は Claude の応答ごとに発火するため、フィルタリングなしでは大量通知になる。

### 設計方針

**ハイブリッド方式を採用:**

1. **Stop hook は残す**（一般的な作業完了通知として）。ただし以下のフィルタリングを追加:
   - `stop_hook_active` が `true` の場合はスキップ（再帰防止）
   - `last_assistant_message` の内容・長さで「実質的な作業完了」かを判定
   - 短い応答（挨拶・単純な質問応答）では通知しない

2. **スキルからの明示呼び出しも併用**（create-plan, implement-plans の完了時）:
   - CLI モード `stop-notify.py --message "..." --title "..."` で確実に通知

### 影響範囲（変更/追加予定ファイル）

- `.claude/hooks/stop-notify.py`: 通知フィルタリングロジックの修正（REQ-001, REQ-002）
- `.claude/settings.json`: PreToolUse / Stop フックの登録、env セクション追加（REQ-003, REQ-004）

### 実装ステップ

#### Step 1: stop-notify.py の修正（REQ-001, REQ-002）

- [ ] `handle_hook()` 関数を修正:
  - `stop_reason` の参照を削除（存在しないフィールド）
  - `hook_event_name` が `"Stop"` であることを確認（`SubagentStop` は対象外）
  - `stop_hook_active` が `true` なら `sys.exit(0)`（再帰防止）
  - `last_assistant_message` の長さチェック: 200文字未満の短い応答では通知しない
- [ ] フィルタリングのログ出力を stderr に追加（デバッグ用）

**修正前（現状）:**
```python
def handle_hook() -> None:
    data = json.load(sys.stdin)
    stop_reason = data.get("stop_reason", "end_turn")
    if stop_reason not in ("end_turn", "tool_use"):
        sys.exit(0)
    # → 常に通過して通知
```

**修正後:**
```python
MIN_MESSAGE_LENGTH = 200

def handle_hook() -> None:
    data = json.load(sys.stdin)

    # Subagent check: hook_event_name で判別
    if data.get("hook_event_name") != "Stop":
        sys.exit(0)

    # Recursion guard
    if data.get("stop_hook_active"):
        sys.exit(0)

    # Short response filter: 単純な応答では通知しない
    message = data.get("last_assistant_message", "")
    if len(message) < MIN_MESSAGE_LENGTH:
        sys.exit(0)

    # 通知送信
    ...
```

**検証**: 修正後、stop-notify.py を手動テスト:
1. 短いメッセージ（100文字未満）→ 通知なし
2. 長いメッセージ（200文字以上）→ 通知あり
3. `stop_hook_active: true` → 通知なし
4. `hook_event_name: "SubagentStop"` → 通知なし

#### Step 2: settings.json に Hook を登録（REQ-003）

- [ ] `PreToolUse` セクションに以下を追加:
  - matcher `"Bash"`: `slack_approval.py` を登録
  - matcher `"ExitPlanMode|AskUserQuestion"`: `notify-slack.py` を登録
- [ ] `Stop` セクションを新規追加:
  - `stop-notify.py` を登録
- [ ] `SubagentStop` には**登録しない**（サブエージェント通知を抑制）

**追加する Hook 設定:**
```json
"PreToolUse": [
  ...(既存のPreToolUseがあれば維持),
  {
    "matcher": "Bash",
    "hooks": [
      {
        "type": "command",
        "command": "python3 \"$(git rev-parse --show-toplevel)/.claude/hooks/slack_approval.py\"",
        "timeout": 310
      }
    ]
  },
  {
    "matcher": "ExitPlanMode|AskUserQuestion",
    "hooks": [
      {
        "type": "command",
        "command": "python3 \"$(git rev-parse --show-toplevel)/.claude/hooks/notify-slack.py\"",
        "timeout": 310
      }
    ]
  }
],
"Stop": [
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command",
        "command": "python3 \"$(git rev-parse --show-toplevel)/.claude/hooks/stop-notify.py\"",
        "timeout": 10
      }
    ]
  }
]
```

**検証**:
- settings.json が valid JSON であること（`python3 -m json.tool` で確認）
- 既存の PostToolUse / PreCompact フックが壊れていないこと

#### Step 3: 環境変数テンプレートの追加（REQ-004）

- [ ] settings.json に `env` セクションを追加（値はプレースホルダー）:
  ```json
  "env": {
    "SLACK_BOT_TOKEN": "",
    "SLACK_CHANNEL_ID": "",
    "SLACK_APPROVER_USER_ID": ""
  }
  ```
- [ ] ユーザーに値の設定を依頼する

**検証**: `lib/env.py` が settings.json の env セクションから値を読み取れることを確認

### 例外・エラーハンドリング方針

- 環境変数未設定時: 全スクリプトが `sys.exit(0)` で静かにスキップ（既存の挙動を維持）
- Slack API エラー: stderr にログ出力し `sys.exit(0)`（通知失敗で作業を止めない）
- JSON パースエラー: `sys.exit(0)` で静かにスキップ

### テスト/検証方針

- 自動テスト: N/A（外部API依存のため手動確認が主）
- 手動確認観点:
  - [ ] 単純な質問（「こんにちは」）で通知が飛ばないこと
  - [ ] create-plan 完了時に通知が届くこと
  - [ ] `ls` コマンド実行で承認通知が飛ばないこと
  - [ ] `rm -rf` コマンドで承認通知が飛ぶこと
  - [ ] ExitPlanMode 発火時に Slack 通知が届くこと
  - [ ] settings.json が valid JSON であること

### リスクと対策

1. リスク: Stop hook 登録後、環境変数未設定のまま全通知がスキップされ動作確認できない → 対策: Step 3 で環境変数テンプレートを追加し、ユーザーに値の入力を依頼
2. リスク: `last_assistant_message` の長さ閾値が不適切で重要な通知が漏れる → 対策: 閾値を `MIN_MESSAGE_LENGTH = 200` として保守的に設定。CLI モード（スキルからの明示呼び出し）はフィルタリングを通らないため確実に通知
3. リスク: PreToolUse に slack_approval.py を登録すると、環境変数設定後に全 Bash コマンドで承認待ちになる → 対策: approval_skip_patterns.txt の skip リストが十分に網羅的であることを確認。`python3`, `ls`, `git status` 等は既に skip 登録済み

### 完了条件

- [ ] stop-notify.py が Stop hook の実際の stdin データ形式に対応している
- [ ] 短い応答（200文字未満）で通知が発火しない
- [ ] サブエージェント終了で通知が発火しない（SubagentStop に未登録）
- [ ] settings.json に PreToolUse / Stop フックが正しく登録されている
- [ ] 環境変数テンプレートが settings.json の env セクションに追加されている
- [ ] 既存フック（PreCompact, PostToolUse）が壊れていない
