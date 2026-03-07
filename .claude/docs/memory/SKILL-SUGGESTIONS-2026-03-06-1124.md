---
tags: ['session', 'automation']
scope: session
date: 2026-03-06
---

# スキル候補レポート — 2026-03-06 11:24

## 検出されたパターン

- `/proposal-quality-gate` → `/create-plan` → `codex-review` ループ → `/implement-plans` の直列起動が毎回同じ順序で実行された（3回以上）
- `Edit` ツール実行前にファイルを読まず "File has not been read yet" エラーが発生（`datatable.js`、`table_ui.js`、`plan.md` で計4回）
- codex-review が APPROVED になるまで5回以上反復し、同カテゴリの blocking issue（認可範囲・バリデーション具体性・ファイル参照不整合）が繰り返し指摘された（2セッションで各5回）
- フロントエンドデバッグで「console.log 追加 → ユーザーがログを verification.md に貼り付け → ログ削除」の手順が2課題で繰り返された（課題7・課題1）
- Docker コンテナ内のファイル所有権問題（root 所有）で直接編集できず、docker exec による chown が必要だった（2回）
- `notify-slack.py` と `slack_approval.py` フックが `invalid_blocks` / fail-closed エラーで繰り返しブロックされた（ExitPlanMode で5回以上）
- 同一課題（RETRY-001 スクロール・RETRY-002 セル色分け）が4〜5回修正しても解決せず、根本原因の特定よりも推測での修正を繰り返した
- 実装後のテスト実行 `php artisan test` が毎回手動で実行された

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `browser-debug` | 「ブラウザのログを見たい」「DevToolsで確認したい」「console.logを追加して」 | 対象ファイルにデバッグログを自動挿入 → antigravity/Playwright でログ収集 → ログ削除まで一連を自動化 | 高 |
| `fix-docker-permissions` | 「Permission denied」「EACCES」エラー + Laravel プロジェクト | docker exec で対象ファイルの所有者を `www-data` または uid 1000 に変更するコマンドを実行 | 中 |
| `propose-one` | 「1個ずつ修正」「次の修正に進みたい」「確実に修正できるように」 | prompt.md の未解決課題から1件だけ選んで proposal.md に書き込み、quality gate → plan 作成まで実行 | 高 |

---

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| `codex-review-strict` | codex-review ループが5回以上かかる場合 | 認可範囲・バリデーション方針・ファイル参照の3カテゴリに絞って事前チェックし、APPROVED 収束を高速化する。反復前に「この3点を確認したか」をゲートとして設ける | 高 |
| `browser-evidence-collector` | 「動かない」「挙動がおかしい」などフロントエンド不具合報告 | antigravity/Playwright でスクリーンショット・コンソールログ・DOM を収集し verification.md に書き込む。修正前の証拠収集を自動化 | 高 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PreToolUse（Edit） | `Edit` ツールが呼ばれたとき | 対象ファイルパスが現セッションで未読の場合に警告を出力し、自動で `Read` を先行実行する。"File has not been read yet" エラーを事前防止 | 高 |
| PostToolUse（Edit/Write） | PHP/JS ファイルの編集後 | `php artisan test` を自動実行してテスト結果をサマリー出力。回帰バグを即時検知 | 中 |
| PreToolUse（ExitPlanMode） | ExitPlanMode 前 | Slack フックを通さずに計画内容を直接コンソールに出力し、ユーザーに承認 y/n を求めるシンプルな承認フローに置き換え。`notify-slack.py` の `invalid_blocks` エラーを回避 | 中 |

---

## 観察事項

- **codex-review の反復コスト**: 1ループあたり約50k tokens × 5回 = 250k tokens/計画書。CHANGES_REQUIRED の原因カテゴリが2セッション連続で同じ（認可・バリデーション・ファイル参照）であり、事前チェックリストをスキルに組み込むことで大幅に削減できる可能性がある
- **「推測修正サイクル」の繰り返し**: 課題7（要求納期）と課題1（スクロール）で同じパターン（推測 → 失敗 → 自己分析 → 証拠収集 → 解決）が発生。`verify-before-fix` スキルが存在するにもかかわらずトリガーされなかった。スキルのトリガー description を「同じ箇所を2回目修正する前」にも反応するよう強化するとよい
- **`verify-before-fix` スキルの未活用**: 「改善されていない（5回目）」という明確な繰り返し失敗シグナルがあったが、同スキルが自動起動されなかった。description に「修正が改善されていないと言われたとき」を明示すべき