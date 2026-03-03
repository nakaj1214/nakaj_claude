# Create Plan — 詳細手順

## Fixed Files

| File | Role |
|------|------|
| `docs/implement/proposal.md` | Input: User-written requirements (read-only) |
| `docs/implement/plan.md` | Output: Implementation plan (create/update by Claude) |
| `docs/implement/review.md` | Output: Codex review result (create/update by Codex) |

---

## Step 1: Read Proposal

Read `docs/implement/proposal.md`.

If the file does not exist, stop and tell the user:
> `docs/implement/proposal.md` が見つかりません。先にファイルを作成してください。

Send a Slack notification that the skill has started:

```bash
python3 .claude/hooks/notify-slack.py \
  --title ":rocket: create-plan 開始" \
  --message "proposal.md を読み込み、実装計画の作成を開始します。"
```

---

## Step 2: Investigate Codebase (Claude)

Investigate the codebase based on the scope described in proposal.md:

- Related existing code (classes, functions, modules)
- Files likely to be affected
- Libraries and patterns already in use
- Existing tests relevant to the scope

Use this investigation to inform the plan in the next step.

---

## Step 3: Create plan.md (Claude)

Based on proposal.md, create `docs/implement/plan.md` using the format below.

```markdown
## 実装計画: {Title}

### 目的
{1-2 sentences from proposal}

### スコープ
- 含むもの: {list}
- 含まないもの: {list}

### 影響範囲（変更/追加予定ファイル）
- {file path}: {reason}

### 実装ステップ

#### Step 1: {Title}
- [ ] {Specific task}
- [ ] {Specific task}
**検証**: {Completion criteria}

#### Step 2: {Title}
...

### 例外・エラーハンドリング方針
{policy}

### テスト/検証方針
- 自動テスト: {command or N/A}
- 手動確認観点: {specific checklist}

### リスクと対策
1. リスク: {description} → 対策: {mitigation}
2. リスク: {description} → 対策: {mitigation}
3. リスク: {description} → 対策: {mitigation}

### 完了条件
- [ ] {Acceptance criterion}
```

---

## Step 4: Codex Review Loop

Invoke the `codex-review` skill with the following parameters:

- **target_file**: `docs/implement/plan.md`
- **review_file**: `docs/implement/review.md`
- **max_iterations**: 5
- **checklist**: (use default — the built-in checklist covers implementation plan review)
- **slack_notify**: true

The `codex-review` skill handles the full review loop:
Codex reviews → Claude fixes blocking issues → repeat until APPROVED or max iterations.

See [codex-review INSTRUCTIONS](../codex-review/INSTRUCTIONS.md) for detailed loop behavior.

---

## Step 5: Done

Send a Slack notification that the plan is complete:

```bash
python3 .claude/hooks/notify-slack.py \
  --title ":white_check_mark: create-plan 完了" \
  --message "実装計画が APPROVED されました（{N}回目で承認）。\n• docs/implement/plan.md\n• docs/implement/review.md"
```

Report to user (in Japanese):

```
## 計画作成完了

✅ Codex レビュー: APPROVED（{N}回目で承認）

### 作成ファイル
- docs/implement/plan.md
- docs/implement/review.md（最終レビュー）

### 次のステップ
実装を開始する場合は実装タスクをお知らせください。
```

---

## Notes

- Codex is called via subagent to preserve main context window
- Codex cannot access Claude's file context — plan.md content must be passed explicitly in the prompt
- Claude has final authority; if Codex APPROVED but Claude sees a critical issue, Claude may request another iteration
- Max 5 iterations is a hard limit to prevent infinite loops
