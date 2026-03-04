# Create Plan — 詳細手順

## Fixed Files

| File | Role |
|------|------|
| `docs/implement/prompt.md` | Input: User-written request (read-only, informal) |
| `docs/implement/proposal.md` | Intermediate: Structured requirements (generated from prompt.md) |
| `docs/implement/plan.md` | Output: Implementation plan (create/update by Claude) |
| `docs/implement/review.md` | Output: Codex review result (create/update by Codex) |

---

## Step 0: prompt.md → proposal.md（要件構造化）

### 0-1. prompt.md を読む

Read `docs/implement/prompt.md`.

If the file does not exist, stop and tell the user:
> `docs/implement/prompt.md` が見つかりません。先にファイルを作成してください。

### 0-2. proposal.md を生成する

prompt.md の内容を読み、`proposal-quality-gate` スキルの構造化テンプレートに従って
`docs/implement/proposal.md` を生成する。

- prompt.md はユーザーが自由に書いた依頼文（非構造化）
- proposal.md は Claude が構造化した要件書（REQ-001 形式）
- 曖昧な記述には `[要確認]` タグを付ける
- 対象ファイルが不明な場合はコードベースを調査して推測する

### 0-3. Proposal Quality Gate

生成した proposal.md に対して品質チェック（7項目）を実行する。

詳細: [proposal-quality-gate INSTRUCTIONS.md](../proposal-quality-gate/INSTRUCTIONS.md)

品質チェックの結果:
- **PASS** → Step 1 に進む
- **FAIL** → proposal.md をリライトし、ユーザー承認後に Step 1 に進む

### 0-4. ユーザー確認

proposal.md の内容をユーザーに提示し、`[要確認]` タグの確認と承認を得る。

---

## Step 1: Read Proposal

Read `docs/implement/proposal.md`（Step 0 で生成済み）.

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

## Step 4: Done（plan.md 作成完了）

plan.md の作成が完了したら、ユーザーに報告して停止する。

Report to user (in Japanese):

```
## 計画作成完了

### 作成ファイル
- docs/implement/plan.md

### 次のステップ
- 計画の内容を確認してください
- Codex レビューが必要な場合は `/codex-review` を実行してください
- 実装を開始する場合は `/implement-plans` を実行してください
```

---

## Step 5: Codex Review Loop（オプション — 手動実行）

ユーザーが明示的に Codex レビューを要求した場合のみ実行する。
`/codex-review` スキルを以下のパラメータで呼び出す:

- **target_file**: `docs/implement/plan.md`
- **review_file**: `docs/implement/review.md`
- **max_iterations**: 5
- **checklist**: (use default)
- **slack_notify**: true

See [codex-review INSTRUCTIONS](../codex-review/INSTRUCTIONS.md) for detailed loop behavior.

---

## Notes

- **create-plan は plan.md を作成した段階で停止する（Step 4 で完了）**
- Codex レビューは別途 `/codex-review` で手動実行する（自動では実行しない）
- **Claude は APPROVED 判定を自分で行ってはならない。** Codex レビューを実行した場合、Codex が APPROVED を出さなかったらユーザーに状況を報告して判断を仰ぐこと
