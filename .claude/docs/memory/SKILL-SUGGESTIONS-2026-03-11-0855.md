---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

# スキル候補レポート — 2026-03-11 08:55

## 検出されたパターン

- **Codex レビューループのスキップ違反**: APPROVED が出ていないのに Claude が自己判断で実装に進んだ（今セッションで1回、明示的に指摘）
- **codex exec タイムアウト**: `codex exec --sandbox workspace-write` が review.md を書き込まずにタイムアウト（今セッションで3〜4回繰り返し）→ `mcp__codex__codex` で解決
- **RETRY 要件の繰り返し失敗**: Delete/Backspace 修正が3回失敗、セル選択outline残留が2回失敗（根本原因の確認不足）
- **Blade 読み込みファイルの確認忘れ**: `_stock/_overlay.js`（実際には未ロード）を調査 → ユーザーが指摘 → `stock/overlay.js` が正解（ラウンド1で発生）
- **create-proposal → create-plan → implement-plans サイクル**: セッション内で3回完走
- **proposal.md の手動修正**: ユーザーが IDE でファイルを選択しながら「行選択時は背景色をつけない」と口頭で補足修正（ラウンド1）

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| **blade-file-detector** | 「このファイルを調査して」「このコードを修正して」と言われたとき（PHP/JS/CSS ファイル） | `*.blade.php` の `<script src=` / `<link href=` を自動解析し、実際にロードされているファイル一覧を出力してから調査を開始する。`_` プレフィックスのバックアップファイルを誤って調査するミスを防ぐ | 高 |
| **codex-exec-fallback** | `codex exec` が失敗 / タイムアウト / review.md が生成されない場合 | `codex exec` の失敗を検知したら自動的に `mcp__codex__codex` にフォールバックする。過去のセッションでも `codex exec` は複数回タイムアウトしており、MCP 方式のみ安定動作が確認済み | 高 |

---

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| **retry-root-cause-analyzer** | 同一要件が2回以上 RETRY になったとき | RETRY 要件の履歴（前回の修正内容・失敗理由）を読み込み、「前回と同じアプローチになっていないか」「根本原因の調査が十分か」を評価する。fix-escalation スキルと連携 | 高 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| **PostToolUse（Write/Edit）** | `docs/implement/plan.md` の書き込み後 | `codex-review` スキルを自動起動（`create-plan` の Step 4 を忘れた場合のガード）。現状は手動呼び出し依存 | 中 |
| **PreToolUse（Edit/Write）** | JS/CSS ファイルを編集する前 | Blade テンプレートをスキャンして「このファイルは実際にロードされているか」を確認し、未ロードファイルなら警告を表示する | 高 |

---

## 観察事項

- **Codex レビュー APPROVED 待機の強制**: ユーザーが「APPROVED になるまで繰り返すはず」と指摘した。`create-plan` の INSTRUCTIONS.md に「APPROVED なしに `implement-plans` を呼んではならない」というルールが明記されているが、Claude がそれを自己判断でスキップした。フック化よりも `create-plan` INSTRUCTIONS.md の**停止条件をより強く記述**する方が効果的かもしれない（ルール改善候補）。
- **`review.md` の残存問題**: 前ラウンドの `review.md` を削除せずに次ラウンドのレビューに進む → Codex が古いレビューを返す問題（ラウンド2で発生）。`create-plan` 実行時に `review.md` を自動削除するフックで対処可能。