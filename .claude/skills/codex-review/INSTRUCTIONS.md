# Codex Review — Detailed Instructions

## Input Parameters

The caller specifies these when invoking the skill.
Parse them from the user's message or skill arguments.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `target_file` | Yes | — | Path to the file to review |
| `review_file` | No | `{target_file dir}/review.md` | Path for the review output |
| `max_iterations` | No | 5 | Maximum review loop iterations |
| `checklist` | No | (built-in default) | Custom review checklist — inline text, or path to a `.md` file |
| `slack_notify` | No | true | Whether to send Slack notifications |

---

## Step 1: Initialize

1. Verify `target_file` exists. If not, stop and tell the user:
   > `{target_file}` が見つかりません。ファイルパスを確認してください。

2. Resolve `review_file` default:
   - If not specified, use the same directory as `target_file` with filename `review.md`
   - Example: `docs/design.md` → `docs/review.md`

3. Resolve `checklist`:
   - If a file path is given (ends with `.md`), read that file and use its content
   - If inline text is given, use it directly
   - If not specified, use the **Default Checklist** below

4. If `slack_notify` is true, send a start notification:

```bash
python3 .claude/hooks/notify-slack.py \
  --title ":mag: codex-review 開始" \
  --message "対象: {target_file}\nレビューループを開始します。"
```

---

## Step 2: Review Loop

Repeat up to `max_iterations` times.

### 2-1. Launch Codex Review (subagent)

```
Task tool parameters:
- subagent_type: "general-purpose"
- run_in_background: false
- prompt: |
    Review a document file using Codex CLI.

    Steps:
    1. Read the file: {target_file}
    2. Run Codex CLI:

    codex exec --model gpt-5.3-codex -c model_reasoning_effort="high" --sandbox workspace-write --full-auto "
    You are a senior engineer reviewing a document.
    Your ONLY allowed file operation is writing to {review_file}.
    Do NOT create, modify, or delete any other files.
    Read {target_file} and write a structured review to {review_file}.

    Review checklist:
    {resolved_checklist}

    Output format for {review_file}:
    # レビュー対象
    - {target_file}

    # まず結論
    - 判定: (APPROVED / CHANGES_REQUIRED)
    - 要点（3〜5行）:

    # 必須修正（Blocking）
    - [ ]

    # 推奨（Non-blocking）
    - [ ]

    # 影響範囲の追加提案
    -

    # テスト追加/修正提案
    -

    # リスク再評価
    -

    # 次アクション
    -

    APPROVED or CHANGES_REQUIRED
    " 2>/dev/null

    3. Read {review_file} and return:
       - The verdict (APPROVED or CHANGES_REQUIRED)
       - Blocking issues (if any)
       - Non-blocking recommendations (if any)
```

### 2-2. Read Verdict

Check the last non-empty line of `{review_file}`:
- `APPROVED` → go to Step 3 (done)
- `CHANGES_REQUIRED` → go to 2-3

If `slack_notify` is true, send a notification:

```bash
python3 .claude/hooks/notify-slack.py \
  --title ":mag: codex-review レビュー結果 (#{iteration}回目)" \
  --message "判定: {verdict}\n{blocking issues summary, if any}"
```

### 2-3. Fix Target File (Claude)

Read `{review_file}` and update `{target_file}`:
- Fix all **Blocking** issues
- Apply **Non-blocking** recommendations if reasonable
- Do NOT change the overall structure unless required

If `slack_notify` is true, send a notification:

```bash
python3 .claude/hooks/notify-slack.py \
  --title ":pencil2: codex-review 修正完了 (#{iteration}回目)" \
  --message "レビュー指摘に基づき {target_file} を更新しました。次のレビューを開始します。"
```

Go back to 2-1 (next iteration).

### Iteration Limit

If `max_iterations` reached without `APPROVED`:

**Claude は自分で APPROVED 判定を行ってはならない。**
ユーザーに以下を報告し、判断を仰ぐこと:

1. 残っている blocking issues の一覧
2. これまでの修正履歴の要約
3. 次のアクションの選択肢を提示:
   - blocking issues を手動で解決してから再実行
   - 現状のまま APPROVED として進める（ユーザーの明示的な承認が必要）
   - proposal.md を見直して要件を修正する

> :warning: レビューループが{max_iterations}回を超えました。以下の blocking issues が残っています。

If `slack_notify` is true:

```bash
python3 .claude/hooks/notify-slack.py \
  --title ":warning: codex-review レビュー上限到達" \
  --message "{max_iterations}回のレビューループで APPROVED になりませんでした。ユーザー判断が必要です。\n{review_file} を確認してください。"
```

Stop the loop and **wait for user decision**. Do NOT proceed automatically.

---

## Step 3: Done

If `slack_notify` is true:

```bash
python3 .claude/hooks/notify-slack.py \
  --title ":white_check_mark: codex-review 完了" \
  --message "{target_file} が APPROVED されました（{N}回目で承認）。\n• {target_file}\n• {review_file}"
```

Report to user (in Japanese):

```
## Codex レビュー完了

✅ 判定: APPROVED（{N}回目で承認）

### ファイル
- {target_file}（レビュー対象）
- {review_file}（レビュー結果）

### 次のステップ
必要に応じて次の作業をお知らせください。
```

---

## Default Checklist

Used when `checklist` parameter is not specified:

```
1. Scope clarity - Is the purpose/non-purpose clear? Are there vague expressions?
2. Completeness - Are all affected files/components/routes/validation/authorization/DB/frontend/config listed?
3. Implementation order - Are dependencies in the correct order?
4. Test/verification specificity - Are test commands and manual check points concrete?
5. Risks and mitigations - Are at least 3 risks listed with concrete mitigations?
6. Completion criteria - Is the acceptance condition clear and measurable?
```

---

## Notes

- Codex is called via subagent to preserve main context window
- Codex cannot access Claude's file context — target_file content is read by Codex directly from the workspace
- **Claude は APPROVED / CHANGES_REQUIRED の判定を自分で行ってはならない。** 判定は Codex のみが行う。Codex が APPROVED を出さずにループ上限に達した場合は、ユーザーに報告して判断を仰ぐこと
- The max_iterations limit is a hard cap to prevent infinite loops
