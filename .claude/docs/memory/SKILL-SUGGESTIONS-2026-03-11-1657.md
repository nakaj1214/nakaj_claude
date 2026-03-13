---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

スレッドの要約分析とスキル候補レポートを作成します。

# スキル候補レポート — 2026-03-11 16:57

## 検出されたパターン

- `prompt_N.md` → `/create-proposal` → `/create-plan` → `/implement-plans` のフルパイプラインを何度も手動で順次トリガーしている
- `/create-plan` 内の Codex レビューループが多数回（12回）繰り返され、毎回 blocking 修正 → 再レビューのサイクルが発生
- MCP ツール (`mcp__codex__codex`) の呼び出しが Slack フックにブロックされ、設定修正が必要だった
- Blade ファイルのインライン JS 発見 → 外部ファイルへの移行作業が繰り返し発生
- CSS クラス（`btn-outline-*` / `btn-info`）の禁止・置換が複数ファイルにまたがって繰り返し実施された

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `propose-and-plan` | 「提案して計画も作って」「proposal と plan を作成して」「prompt_N.md から全部進めて」 | `prompt.md` / `prompt_N.md` を読み込み、`/create-proposal` → `/create-plan` を自動的に連鎖実行するオーケストレーションスキル | 高 |
| `scan-inline-js` | 「インライン JS を探して」「直書き JS を検出して」「no-inline-js 違反を確認して」 | Blade ファイルを Grep して `<script>` タグの直書きを一覧表示し、対応する外部 JS ファイル名候補を提案 | 中 |

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse | `Edit` / `Write` で `*.blade.php` を編集した直後 | `<script>` の直書きがないか grep し、あれば警告メッセージを表示（no-inline-js ルール違反の即時検知） | 中 |

## 観察事項

- **Codex レビューが多数回になる傾向**: 12回繰り返したのは計画の粒度が大きいためで、要件を事前に小さく分割するか、plan の雛形を充実させれば回数を減らせる可能性がある。スキル化より plan テンプレートの改善で対応するのが適切。
- **Bootstrap クラス禁止の繰り返し**: `btn-outline-*` / `btn-info` / `btn-primary` のホバー問題が複数回報告された。CSS 側のグローバルオーバーライドで対処済みだが、`pre-commit` フックで `btn-outline-` の混入を検知するとより確実。
- **MCP フック設定の誤り**: `settings.json` の matcher に `mcp__codex__codex` を含めていたことで Slack 承認フックがブロックした。設定の記録はあるが、自動化よりドキュメント整備が優先。