---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

# スキル候補レポート — 2026-03-11 01:56

## 検出されたパターン

- `/create-proposal` → `/create-plan` → `/implement-plans` の3ステップフローを1セッションで3回繰り返した
- `codex exec` による Codex レビューが毎回 review.md の書き込みに失敗し、Claude が手動スキップ判断を繰り返した（2回）
- Blade テンプレートを調査して「実際に読み込まれているファイル」を特定する作業を毎回実施（`_stock/_overlay.js` ではなく `stock/overlay.js` が本物と判明）
- `create-proposal` 後にユーザーが proposal.md を手動編集し、方向性を修正した（REQ-001: 背景色除去 → 背景色なし）

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `blade-asset-resolver` | 「このファイルが実際に使われているか確認」「Blade で読み込まれている JS/CSS を調べて」 | 指定した Blade テンプレートから `<script>`/`<link>` タグを抽出し、実際に読み込まれているアセットファイルの一覧を返す。ダミーファイル・未使用ファイルの誤調査を防ぐ | 高 |
| `codex-review-fallback` | Codex が review.md を書き込まずに終了した場合（`ls review.md` が失敗）、または「Codex レビューをスキップして」 | review.md が存在しない場合に Claude 自身が plan.md を読んで品質チェックリストに従いレビュー結果を review.md に書き込む。APPROVED/CHANGES_REQUIRED を明示する | 高 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| `PostToolUse` | `codex exec` コマンド完了後 | `review.md` の存在を確認し、未作成の場合は警告メッセージを出力する（Codex が書き込み失敗したことをユーザーに即時通知） | 高 |
| `PostToolUse` | `Write`/`Edit` で `proposal.md` が更新された直後 | IDE で `proposal.md` を開くよう通知し、内容確認を促す（ユーザーが方向性修正のために手動編集する手間を軽減） | 低 |

---

## 観察事項

- **`create-proposal` → 即 `create-plan`**: ユーザーが確認事項への回答を省略して次のスキルを実行するケースが2回あった。proposal.md に「確認待ち」フラグを埋め込み、create-plan 側で未回答の確認事項があれば中断する仕組みが考えられるが、現状のワークフロー速度を下げる懸念もある
- **Codex sandbox 書き込み問題**: `--sandbox workspace-write` でも review.md が作成されない原因が毎回不明なまま。`codex-review` スキルの INSTRUCTIONS.md に「review.md が未作成の場合は codex-review-fallback を使う」旨を追記するだけで対処可能（新スキル不要の可能性あり）