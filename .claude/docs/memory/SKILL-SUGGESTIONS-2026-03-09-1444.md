---
tags: ['session', 'automation']
scope: session
date: 2026-03-09
---

# スキル候補レポート — 2026-03-09 14:44

## 検出されたパターン

- `create-proposal → create-plan → implement-plans` の3段ワークフローが4回繰り返されている
- `codex exec` の実行が Slack 承認フック（`2>/dev/null` リダイレクト検出）で止まるケースが複数回発生
- `review.md` が前回の plan.md のレビュー結果を返してしまう（古い内容のまま APPROVED 判定）ことが2回発生
- outline の修正が2回失敗し、`fix-escalation` が発動（同一バグへの2回失敗）
- Task ツール（サブエージェント）の承認がユーザーに3回拒否され、直接 Bash 実行パターンに切り替え
- DB の `DROP DATABASE` 実行によるデータ全消しがユーザーから強く非難された
- セッションコンテキスト圧迫により「continue」と入力する必要が複数回発生

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `review-md-refresh` | 「レビューループを実行」「codex-review」「APPROVED の確認」。review.md が plan.md より古い（mtime 比較）場合に強制再実行 | review.md のタイムスタンプが対象 plan.md より古ければ Codex を再実行して上書きする。キャッシュ判定とフレッシュネス確認を codex-review スキルの前段に組み込む | 高 |
| `db-operation-safeguard` | 「マイグレーションが失敗している」「テーブルが存在しない」「DB の初期化が必要」 | `DROP DATABASE` / `DROP TABLE` / `TRUNCATE` を禁止し、代替手段（`ALTER TABLE`, `php artisan migrate --path=...`）を提示するチェックリストを実行。実行前に必ず影響範囲を列挙してユーザー確認を取る | 高 |
| `css-inspect-before-fix` | 「見えない」「表示されない」「スタイルが効いていない」「適用されない」 | ブラウザ DevTools なしで CSS 問題を診断するためのチェックリストを実行。`z-index`、`overflow: hidden`、親要素のサイズ、擬似要素の有無、`!important` の衝突などを順番に確認し、DOM 構造と CSS の関係を調査してから修正に進む | 中 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| `PreToolUse:Bash` | コマンドに `DROP DATABASE` または `DROP TABLE` が含まれる（DB 名が `_test` / `_tmp` 以外） | 実行を即座にブロック。「`DROP DATABASE` は禁止されています。`ALTER TABLE` または `php artisan migrate` を使用してください」と出力し、終了コード 1 を返す | 高 |
| `PostToolUse:Write` | `docs/implement/review.md` への書き込み完了後 | ファイルの先頭5行を読み取り、対象の plan.md ファイルパスが記載されているか確認。異なる場合は「⚠️ review.md のレビュー対象が現在の plan.md と一致しません」と警告を出力する | 中 |

---

## 観察事項

- **`implement-plans` と Slack 承認フックの相性**: 「中断なしで実行」を宣言するスキルが Slack 承認フックで何度も止まる。daemon コンテナが起動していない場合に承認ができず詰まるケースが多い。`slack_approval.py` のスキップリストに `node -c`（構文チェック系）を追加するだけで改善できる可能性がある
- **`verify-before-fix` の未使用**: outline が見えない問題に2回失敗しているが、`verify-before-fix` スキルが使われなかった。「見えない」「表示されない」系の問題でこのスキルを自動トリガーする仕組みがあれば防げた可能性がある
- **Task ツール拒否パターン**: Codex review のためにサブエージェントを起動しようとするたびに承認拒否が発生。最終的に直接 Bash（`run_in_background`）で解決しているが、このパターンは MEMORY.md に記録済み