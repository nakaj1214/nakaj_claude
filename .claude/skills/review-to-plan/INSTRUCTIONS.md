# Review to Plan — 詳細手順

## Fixed Files

| File | Role |
|------|------|
| `docs/implement/review.md` | Input: レビュー指摘事項 (read-only) |
| `docs/implement/plan.md` | Input/Output: 実装計画書 (update by Claude) |

---

## Step 1: Read Review

Read `docs/implement/review.md`.

ファイルが存在しない場合は停止し、ユーザーに通知する:
> `docs/implement/review.md` が見つかりません。先にレビューを実施してください。

---

## Step 2: Read Current Plan

Read `docs/implement/plan.md`.

ファイルが存在しない場合は停止し、ユーザーに通知する:
> `docs/implement/plan.md` が見つかりません。先に `/create-plan` で計画を作成してください。

---

## Step 3: Classify Review Items

レビュー内の各指摘事項を以下のカテゴリに分類する:

| カテゴリ | 意味 | plan.md への影響 |
|---------|------|-----------------|
| **Blocking** | 計画の根本的な問題 | ステップの追加・大幅修正が必要 |
| **Improvement** | 改善提案 | ステップの修正・詳細化 |
| **Clarification** | 曖昧な箇所の指摘 | 記述の明確化 |
| **Cosmetic** | 書式・表現の問題 | 軽微な修正 |

---

## Step 4: Map to Plan Sections

各指摘事項を plan.md のどのセクションに影響するか特定する:

- 実装ステップ（Step N）に対する指摘 → 該当ステップを修正
- スコープに対する指摘 → スコープセクションを更新
- テスト方針に対する指摘 → テスト/検証方針を更新
- リスクに対する指摘 → リスクと対策を更新
- 完了条件に対する指摘 → 完了条件を更新
- 新しい要件の追加 → 新ステップを追加

---

## Step 5: Update plan.md

plan.md を更新する。更新時のルール:

1. **既存の構造を維持する**: セクション見出しやフォーマットを変えない
2. **変更箇所にマーカーを付ける**: `<!-- [review] 変更理由 -->` コメントを追記
3. **ステップ追加時は番号を振り直す**: 既存ステップの順序を崩さない
4. **削除ではなく修正**: 指摘に基づいてステップを削除せず、修正する

---

## Step 6: Report Changes

ユーザーに変更内容を報告する:

```
## レビュー反映完了

### 反映した指摘事項

| # | カテゴリ | 指摘内容 | 反映先 | 対応内容 |
|---|---------|---------|--------|---------|
| 1 | Blocking | {summary} | Step N | {what changed} |
| 2 | Improvement | {summary} | スコープ | {what changed} |
...

### 変更サマリー
- 修正したステップ: {list}
- 追加したステップ: {list or なし}
- その他の変更: {list or なし}

### 次のステップ
plan.md を確認し、問題なければ `/implement-plans` で実装を開始してください。
```

---

## Notes

- review.md の形式は自由（箇条書き、表、文章いずれでも対応可能）
- Codex レビュー結果の `review.md` にも、手動レビューの `review.md` にも対応する
- 反映後に review.md は変更しない（履歴として保持）
- 不明瞭な指摘はユーザーに確認を取る（推測で反映しない）
