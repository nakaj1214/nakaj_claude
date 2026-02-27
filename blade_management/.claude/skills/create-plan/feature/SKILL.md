---
name: create-plan
description: |
  Proposal → (Gemini CLI) plan.md + analysis.md → (Codex CLI) review loop → (Codex) implement.
  Must/High が残る限り「Gemini修正 → Codex再レビュー」を繰り返す。
  Gemini修正を2回やっても Must が残る場合のみ、Claude Code が plan.md 更新を引き継ぐ。
metadata:
  short-description: Proposal → Plan/Analysis (Gemini) → Review loop (Codex) → Implement (Codex)
disable-model-invocation: true
---

# create-plan（1ファイル完結・堅牢版）

## 目的

- `docs/implement/proposal.md` を入力として、Gemini CLIで
  - `docs/implement/plan.md`
  - `docs/implement/analysis.md`
  を生成する
- Codex CLIで `plan.md` をレビューし、`docs/implement/review.md` に Must/High/Medium/Low を出す
- Must/High が残る限り「Gemini修正 → Codex再レビュー」を回す
- Geminiが2回修正しても Must が残る場合は Claude Code が plan.md 更新を引き継ぐ
- APPROVED になったら Codex が実装（Medium/Lowは安全なら拾って良い）

---

## 固定ファイル

| File | Role |
|------|------|
| `docs/implement/proposal.md` | Input（read-only） |
| `docs/implement/analysis.md` | Output（Gemini生成） |
| `docs/implement/plan.md` | Output（Gemini/Claude Codeで更新） |
| `docs/implement/review.md` | Output（Codexが上書き更新） |

---

## ループ/リトライ設定

- MAX_REVIEW_LOOP: 8（Codexレビュー反復の上限）
- MAX_GEMINI_FIX: 2（Geminiでのplan修正上限。超えてMustが残るならCCへ）
- MAX_RETRY: 3（Gemini/Codexの失敗時リトライ回数）
- 収束条件:
  - `review.md` の最後の非空行が `APPROVED`
  - かつ Must=0、High=0

---

## Step 0: 前提チェック（必須）

```bash
set -euo pipefail

# proposal.md 存在チェック
if [ ! -f "docs/implement/proposal.md" ]; then
  echo "[ERROR] docs/implement/proposal.md が見つかりません。先にファイルを作成してください。"
  exit 1
fi

# CLI 存在チェック
if ! command -v gemini >/dev/null 2>&1; then
  echo "[ERROR] gemini コマンドが見つかりません。Gemini CLIをインストールしてください。"
  echo "[INFO]  インストール: https://github.com/google-gemini/gemini-cli"
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "[ERROR] codex コマンドが見つかりません。Codex CLIをインストールしてください。"
  exit 1
fi

mkdir -p "docs/implement"
```

### カウンタ初期化（Claude Codeが内部で管理）

- `loop_iter = 0`
- `gemini_fix_iter = 0`

---

## Step 1: Geminiで plan.md / analysis.md を生成（リトライ付き）

### Gemini CLIの呼び出し仕様

Gemini CLIはstdinをコンテキストとして受け取り、`--prompt` でプロンプトを渡す。
出力はstdoutに書かれるため、ファイルにリダイレクトして受け取る。

```
cat <ファイル> | gemini --prompt "<プロンプト>" > <出力先>
```

> **注意**: `gemini --prompt` は Gemini CLI（`@google/generative-ai` 系 CLI）の公式構文。
> インストール済みバージョンが異なる場合は `gemini --help` で確認すること。

### 出力フォーマット（bundle形式）

Geminiのstdoutは必ず以下の区切りを含む形式とする：

```
===BEGIN plan.md===
（plan.md本文）
===END plan.md===

===BEGIN analysis.md===
（analysis.md本文）
===END analysis.md===
```

### 実行

```bash
set -euo pipefail

# プロンプトをファイルに書き出す（ヒアドキュメント展開の安全対策）
PROMPT_FILE="$(mktemp)"
cat > "${PROMPT_FILE}" <<'PROMPT'
あなたはシニアエンジニアです。stdin に proposal.md の内容が渡されます。
以下2つのMarkdownを生成してください。

1) docs/implement/plan.md（実装計画）
2) docs/implement/analysis.md（コード影響分析）

出力は必ず次の区切りを厳守してください（区切り行はそのまま出力）:

===BEGIN plan.md===
(ここにplan.md本文。Markdown。保存してそのまま使える)
===END plan.md===

===BEGIN analysis.md===
(ここにanalysis.md本文。Markdown。保存してそのまま使える)
===END analysis.md===

制約:
- 余計な前置き/解説/謝辞を書かない
- plan.mdは必ず以下を含む:
  - 目的 / スコープ / 非スコープ
  - 影響範囲（変更/追加予定ファイルの候補と理由）
  - 実装ステップ（順序と依存が分かるように）
  - 各ステップの検証（テストコマンドや手動観点）
  - 例外・エラーハンドリング方針
  - テスト/検証方針（自動/手動）
  - リスクと対策（最低3つ）
  - 完了条件（計測可能/判定可能）
- analysis.mdは必ず以下を含む:
  - 影響が出そうな箇所（危険箇所）
  - 既存コードの懸念点（壊れやすい点）
  - 追加で確認すべき観点（セキュリティ/権限/データ整合など）
  - 想定失敗パターンと回避策
PROMPT

BUNDLE_PATH="/tmp/gemini_plan_bundle.txt"
PROMPT_TEXT="$(cat "${PROMPT_FILE}")"
rm -f "${PROMPT_FILE}"

ok=0
for attempt in 1 2 3; do
  echo "[INFO] Gemini generate attempt=${attempt}"

  set +e
  cat "docs/implement/proposal.md" | gemini --prompt "${PROMPT_TEXT}" > "${BUNDLE_PATH}"
  # パイプの各コマンドの終了コードを個別に取得
  pipe_status=("${PIPESTATUS[@]}")
  cat_rc="${pipe_status[0]:-1}"
  gemini_rc="${pipe_status[1]:-1}"
  set -e

  if [ "${gemini_rc}" -ne 0 ]; then
    echo "[WARN] Gemini failed: cat_rc=${cat_rc} gemini_rc=${gemini_rc}"
    sleep $((attempt * 2))
    continue
  fi

  # マーカー存在チェック
  marker_ok=1
  for marker in \
    '^===BEGIN plan\.md===$' \
    '^===END plan\.md===$' \
    '^===BEGIN analysis\.md===$' \
    '^===END analysis\.md===$'; do
    if ! grep -qE "${marker}" "${BUNDLE_PATH}"; then
      echo "[WARN] marker missing: ${marker}"
      marker_ok=0
      break
    fi
  done
  [ "${marker_ok}" -eq 0 ] && { sleep $((attempt * 2)); continue; }

  # サイズチェック（300バイト以下は失敗扱い）
  bundle_size="$(wc -c < "${BUNDLE_PATH}" | tr -d ' ')"
  if [ "${bundle_size}" -le 300 ]; then
    echo "[WARN] bundle too small: ${bundle_size} bytes"
    sleep $((attempt * 2))
    continue
  fi

  ok=1
  break
done

if [ "${ok}" -ne 1 ]; then
  echo "[ERROR] Gemini出力が安定しません。bundleを確認してください: ${BUNDLE_PATH}"
  exit 1
fi
```

### 1-3) bundleから plan.md / analysis.md を切り出し（上書き保存）

```bash
: > "docs/implement/plan.md"
: > "docs/implement/analysis.md"

awk '
  BEGIN { in_plan=0; in_analysis=0 }
  /^===BEGIN plan\.md===$/ { in_plan=1; next }
  /^===END plan\.md===$/ { in_plan=0; next }
  /^===BEGIN analysis\.md===$/ { in_analysis=1; next }
  /^===END analysis\.md===$/ { in_analysis=0; next }
  { if (in_plan)     { print >> "docs/implement/plan.md" }
    if (in_analysis) { print >> "docs/implement/analysis.md" } }
' "${BUNDLE_PATH}"

# 切り出し後のサイズチェック
plan_size="$(wc -c < "docs/implement/plan.md" | tr -d ' ')"
analysis_size="$(wc -c < "docs/implement/analysis.md" | tr -d ' ')"

if [ "${plan_size}" -le 100 ] || [ "${analysis_size}" -le 100 ]; then
  echo "[ERROR] 切り出し後のファイルが小さすぎます: plan=${plan_size}B analysis=${analysis_size}B"
  echo "[ERROR] bundleを確認してください: ${BUNDLE_PATH}"
  exit 1
fi

echo "[INFO] plan.md=${plan_size}B analysis.md=${analysis_size}B"
```

---

## Step 2: Codexで plan.md をレビューして review.md を生成/更新

### review.md の必須フォーマット

Codexは Must/High/Medium/Low を必ず分け、先頭に件数を明記し、最後の非空行を `APPROVED` か `CHANGES_REQUIRED` にする。

```markdown
# レビュー対象
- docs/implement/plan.md

# まず結論
- 判定: (APPROVED / CHANGES_REQUIRED)
- Must: {N}
- High: {N}
- Medium: {N}
- Low: {N}
- 要点（3〜5行）:

# Must（Blocking）
- [ ] ...

# High
- [ ] ...

# Medium
- [ ] ...

# Low
- [ ] ...

# 影響範囲の追加提案
-

# テスト追加/修正提案
-

# リスク再評価
-

# 次アクション
-

APPROVED or CHANGES_REQUIRED
```

### Codex実行（MAX_RETRY回リトライ）

```bash
ok=0
for attempt in 1 2 3; do
  echo "[INFO] Codex review attempt=${attempt}"

  set +e
  codex --full-auto "
You are a senior engineer reviewing an implementation plan.
Your ONLY allowed file operation is writing to docs/implement/review.md.
Do NOT create, modify, or delete any other files.

Read docs/implement/plan.md and write a structured review to docs/implement/review.md.

Review checklist:
1. Scope clarity (目的/含む/含まないの曖昧さ)
2. Completeness of affected files (ルート/認可/DB/設定/バリデーション/画面/ジョブ等の漏れ)
3. Implementation order (依存順が正しいか)
4. Test/verification specificity (コマンド/観点が具体的か)
5. Risks and mitigations (最低3件、具体的)
6. Completion criteria (判定可能/計測可能か)

You MUST:
- Use Must/High/Medium/Low sections with counts in summary
- End the file with exactly: APPROVED or CHANGES_REQUIRED (last non-empty line)
"
  codex_rc=$?
  set -e

  if [ "${codex_rc}" -ne 0 ]; then
    echo "[WARN] Codex failed: rc=${codex_rc}"
    sleep $((attempt * 2))
    continue
  fi

  # review.md の存在とサイズチェック
  if [ ! -f "docs/implement/review.md" ]; then
    echo "[WARN] review.md が生成されませんでした"
    sleep $((attempt * 2))
    continue
  fi

  review_size="$(wc -c < "docs/implement/review.md" | tr -d ' ')"
  if [ "${review_size}" -le 50 ]; then
    echo "[WARN] review.md too small: ${review_size}B"
    sleep $((attempt * 2))
    continue
  fi

  ok=1
  break
done

if [ "${ok}" -ne 1 ]; then
  echo "[ERROR] Codexレビューが安定しません。"
  exit 1
fi
```

---

## Step 3: レビューループ（Gemini修正 → Codex再レビュー）

Claude Codeは `loop_iter` と `gemini_fix_iter` を管理しながら以下を繰り返す。

### 3-A) 判定読み取り

```bash
VERDICT="$(awk 'NF { line=$0 } END { print line }' "docs/implement/review.md")"
echo "[INFO] verdict=${VERDICT}, loop_iter=${loop_iter}, gemini_fix_iter=${gemini_fix_iter}"
```

| VERDICTの値 | 次のアクション |
|------------|--------------|
| `APPROVED` | Step 4へ |
| `CHANGES_REQUIRED` | Step 3-Bへ |
| それ以外 | フォーマット不正 → Step 2（Codexレビュー）をやり直す |

### 3-B) Must/High が残る場合の修正

#### 条件分岐

```
if loop_iter >= MAX_REVIEW_LOOP(8):
    → Step 3-C（上限到達）

elif gemini_fix_iter < MAX_GEMINI_FIX(2):
    → Step 3-B-1（Gemini修正）

else: # gemini_fix_iter >= 2 かつ Must が残る
    → Step 3-B-2（Claude Code引き継ぎ）
```

#### 3-B-1) Geminiで plan.md を更新

plan.md と review.md を stdin に渡し、更新後の plan.md 本文のみを返させる。

```bash
TMP_PLAN="$(mktemp)"

{
  echo "===PLAN_MD==="
  cat "docs/implement/plan.md"
  echo ""
  echo "===REVIEW_MD==="
  cat "docs/implement/review.md"
} | gemini --prompt "
stdinにはplan.mdとreview.mdが渡されます。
review.mdのMust/Highを必ず解消するようにplan.mdを全文更新してください。
Medium/Lowは合理的なら反映してよいですが、構造は必要時以外変えないでください。

出力は更新後plan.md本文のみ。
前置き・解説・区切り行は不要。
" > "${TMP_PLAN}"

tmp_size="$(wc -c < "${TMP_PLAN}" | tr -d ' ')"
if [ "${tmp_size}" -le 100 ]; then
  echo "[ERROR] Gemini修正出力が短すぎます。plan.mdの上書きを中止します。"
  rm -f "${TMP_PLAN}"
  exit 1
fi

mv "${TMP_PLAN}" "docs/implement/plan.md"
echo "[INFO] plan.md updated by Gemini (gemini_fix_iter=$((gemini_fix_iter + 1)))"
```

- `gemini_fix_iter += 1`
- `loop_iter += 1`
- → Step 2（Codex再レビュー）へ

---

#### 3-B-2) Gemini修正2回でもMustが残る場合 → Claude Code引き継ぎ

Claude Codeが `docs/implement/review.md` の Must を全て読み、`docs/implement/plan.md` を直接更新する。

**Claude Codeの修正ルール:**
- Must を全て解消（最優先）
- High も可能な範囲で解消
- Medium/Low は合理的なら反映（仕様逸脱・作業膨張はしない）
- 修正後は必ず Step 2（Codex再レビュー）へ戻る

引き継ぎ通知（任意）:
```bash
if [ -f "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-slack.py" ]; then
  python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-slack.py" \
    --title ":warning: create-plan CC引き継ぎ" \
    --message "Gemini修正2回でもMustが残ったため、Claude Codeがplan.md更新を引き継ぎます。"
fi
```

- `loop_iter += 1`
- → Step 2（Codex再レビュー）へ

---

### 3-C) 反復上限（8回）到達時

`loop_iter >= 8` で停止し、ユーザーに以下を提示する：

- 残っている Must/High の一覧
- Geminiで潰し切れなかった理由（不足情報・仕様曖昧・設計判断不足など）
- 次にやるべき1〜3個の具体アクション

上限到達通知（任意）:
```bash
if [ -f "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-slack.py" ]; then
  python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-slack.py" \
    --title ":warning: create-plan レビュー上限到達" \
    --message "8回のレビューループでAPPROVEDになりませんでした。docs/implement/review.md を確認してください。"
fi
```

---

## Step 4: Codexが実装（APPROVED後）

**前提:**
- `review.md` の最後の非空行が `APPROVED`
- Must=0、High=0

```bash
codex --full-auto "
Read docs/implement/plan.md and implement according to the plan.

Rules:
- Follow each implementation step in order
- Run tests/verification described in each step before moving on
- Keep changes small and incremental (easy to diff)
- If Medium/Low issues from review.md are safe and in-scope, fix them during implementation
- If unexpected issues arise, append notes to docs/implement/plan.md before continuing
- Do NOT modify docs/implement/review.md
"
```

---

## Step 5: 完了

```bash
if [ -f "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-slack.py" ]; then
  python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/notify-slack.py" \
    --title ":white_check_mark: create-plan 完了" \
    --message "plan.mdがAPPROVEDされ、Codex実装が完了しました。"
fi
```

ユーザーへの完了報告に含める内容：
- APPROVEDまでの反復回数（`loop_iter`）
- Gemini修正回数（`gemini_fix_iter`）
- Claude Code引き継ぎ有無
- 最終ファイル一覧（plan / review / analysis）
- 実装でMedium/Lowを拾った場合、その要約と理由

---

## 変更点メモ（前バージョンからの修正）

| 項目 | 修正内容 |
|------|---------|
| Gemini呼び出し構文 | `gemini "${PROMPT}"` → `gemini --prompt "${PROMPT_TEXT}"` に修正 |
| プロンプト管理 | ヒアドキュメントを変数展開せず tmpfile 経由に変更（特殊文字の安全対策） |
| PIPESTATUS | `${PIPESTATUS[1]}` で gemini の終了コードを個別取得 |
| サイズ閾値 | bundle: 300B、切り出し後: 100B（より厳格に） |
| Codex呼び出し | `codex exec --full-auto` → `codex --full-auto`（Step4も同様） |
| Step4 実装コマンド | 前バージョンで欠落していたため追加 |
| Slack通知 | 全箇所で存在チェック付きに統一 |
