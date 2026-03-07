---
tags: ['session', 'automation']
scope: session
date: 2026-03-06
---

USER: セル全体が灰色になって期待通りです

---

## スキル候補レポート — 2026-03-06 16:13

### 検出されたパターン

- `proposal.md` → `plan.md` → `codex-review` → 実装 のフローが繰り返されている
- ブラウザキャッシュが原因で「変更が反映されない」報告が複数回発生し、毎回 Console でのスタイル確認コマンドを手動提示している
- デバッグログを追加 → ユーザーがブラウザで実行 → verification.md に結果を貼付 → Claude が分析 というフローが毎回同じ手順で繰り返されている
- `docker compose exec` でコンテナのファイルパーミッション変更（chown/chmod）が複数回実施された
- `ExitPlanMode` のSlackフックが繰り返しエラー（invalid_blocks / fail-closed）で失敗し、ユーザーが拒否するケースが複数回発生
- `develop` → デバッグログ追加 → 調査 → ログ削除 のサイクルが毎回手動で行われている

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `verify-js-cache` | 「変わってない」「反映されてない」「キャッシュ？」と言われたとき | Consoleコマンドを自動生成してスタイルIDや関数の存在を確認するデバッグプロシージャを提供する。`document.getElementById('style-id')?.textContent` のような確認コマンドを即座に提示する | 高 |
| `browser-debug-log` | 「デバッグログを入れて」「確認したい」「原因を調べたい」と言われたとき | ブラウザ上で実行するデバッグ確認コマンドセットを自動生成する。Console実行→verification.mdへの貼付→分析 の標準手順を定型化する | 高 |
| `fix-js-single-issue` | 「1個ずつ直したい」「確実に修正したい」「〇〇が動かない」と言われたとき | 1課題=1計画書=1実装のフローを強制する。`/create-plan` → `codex-review` → 実装 → ブラウザ確認 → 完了 の手順を自動化する | 中 |

---

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| `browser-console-runner` | verification.md の更新後に自動分析が必要なとき | verification.md の内容を受け取りログを解析し「キャッシュ問題か、コード問題か、DOM構造問題か」を分類して原因と確認コマンドを返す | 高 |
| `jquery-datatable-debugger` | DataTablesのDOM操作に関する問題が発生したとき | DataTables Scroller / FixedHeader などプラグインによるDOM変形（thead クローン、scrollBody生成など）の既知パターンを持ち、セレクタ問題の診断に特化する | 中 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse | `Write`/`Edit` で `.js` ファイルが変更されたとき | 「ブラウザキャッシュを無効化するため Ctrl+Shift+R で強制リロードしてください」と自動で通知する | 高 |
| PreToolUse | `ExitPlanMode` が呼ばれたとき | slack_approval.py フックが有効かどうかを `settings.json` で確認し、無効なら即スキップする（現在は毎回fail-closedになりユーザーが拒否している） | 高 |
| PostToolUse | `Write`/`Edit` で `console.log('[DEBUG]` を含む変更が行われたとき | 「デバッグログが残っています。確認後は削除してください」と注意する | 中 |

---

## 観察事項

- `datatable.js` の `initComplete` で DOM が完全に揃っていないタイミングでセレクタを実行するパターンが複数回問題を引き起こした（`find('.dataTables_scrollBody')` が0件など）。DataTables の初期化ライフサイクルについてのメモリエントリを作成する価値がある。
- ファイルパーミッション（root所有）によりローカルからの書き込みができず、docker exec 経由で chown する手順が毎回必要になっている。これは環境設定レベルの問題で、`docker-compose.yml` の `user` 設定で解決できる可能性がある。
- `verify-before-fix` スキルが存在するにもかかわらず、今セッションでは起動されなかった（「直してください」系のトリガーに対して）。スキルのdescriptionを強化すべき可能性がある。