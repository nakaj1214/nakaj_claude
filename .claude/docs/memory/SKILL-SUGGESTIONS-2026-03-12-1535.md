---
tags: ['session', 'automation']
scope: session
date: 2026-03-12
---

# スキル候補レポート — 2026-03-12 15:35

## 検出されたパターン

- `docs/implement/plan.md` が同セッション内で **Write ツールによる上書き** を繰り返している（セッション `a15a2663` で21回・24回・40回・55回・62回・83回・109回・167回・170回・174回・238回・250回・273回 など計13回以上上書き）
- `docs/implement/proposal.md` も同様に頻繁に上書きされる（計10回以上）
- Codex レビューループが CHANGES_REQUIRED → 計画修正 → 再レビューを**最大18回**繰り返している（plan.md の直前セッション）
- `excel_range_select_copy.js` と `stock.css` がセットで繰り返し編集されている（同一概念の表現方法を box-shadow → outline → ::after と3回転換）
- Blade テンプレートのインライン `<script>` ブロックを外部 .js ファイルに抽出する作業が **8ファイル以上**で繰り返された（inbound, stock, order, outbound, debug/outbound_spreadsheet, auth/login, analytics/daily_items, analytics/suppliers）
- `settings.json` が同セッション内で細かく複数回編集された（4回以上連続）
- 大量削除（lines_removed 20行以上）が複数回発生し、アプローチ転換の証拠となっている

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `blade-inline-js` | 「インライン JS を外部ファイルに分離して」「Blade の script を外に出して」「no-inline-js ルールを適用して」 | Blade テンプレート内の `<script>` ブロックを自動検出し、対応する `js/pages/*.js` または `js/components/**/*_init.js` を生成。blade ファイルの script タグを `@if(config('app.env')==='production') secure_asset / @else asset @endif` パターンに置換。no-inline-js.md ルールに従い例外（data属性渡し）も検出 | 高 |
| `codex-review-escalate` | Codex レビューが5回以上 CHANGES_REQUIRED になったとき、または「何度やっても APPROVED にならない」「レビューが通らない」 | 現在の plan.md の問題構造を分析し、「なぜ APPROVED されないか」の根本原因を診断。曖昧な記述パターン・影響範囲の漏れ・受入条件の不足を項目別にレポートし、リライト戦略を提示。codex-review の max_iterations に関係なく動作 | 高 |

---

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| `plan-quality-checker` | plan.md 作成後・Codex レビュー前に自動起動。影響範囲の漏れ・受入条件の曖昧さを事前チェック | Laravel/jQuery/CSS の変更パターンを理解した上で、影響ファイル漏れ（Blade と CSS の両方変更が必要な場合など）・受入条件の「確認できること」vs「動作すること」の区別・非対象の明記有無を診断。Codex レビュー前のセルフチェックとして機能し、レビューイテレーション数を削減する | 高 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse（Write） | `docs/implement/plan.md` または `docs/implement/proposal.md` が Write ツールで3回以上上書きされた場合 | `.claude/staging/plan-rewrite-alert/` に既存実装あり。**本番登録を推奨**。「計画を3回以上書き直しています。実装着手前に proposal.md の要件を絞るか、別トピックに分割することを検討してください」と警告 | 高 |
| PostToolUse（Edit） | Edit ツールで `lines_removed >= 20` かつ `excel_range_select_copy.js` / `*.css` が対象 | `.claude/staging/large-delete-guard/` に既存実装あり。**本番登録を推奨**。「大量削除はアプローチ転換の証拠です。tasks/fix-attempts.md に転換理由を記録してください」と警告 | 高 |
| PostToolUse（Edit/Write） | `src/public/js/` 配下の UI スタイル変数（class 名・box-shadow・background 等）を変更した場合 | `.claude/skills/js-css-sync-check/` に既存実装あり。**本番登録を推奨**。対応 CSS ファイルの未反映クラス定義を grep して差分を報告 | 中 |
| PostToolUse（Write） | `settings.json` が Write で上書きされた場合（Edit ではなく全体上書き） | 変更前後の diff を表示し「hooks/permissions 変更が意図したものか確認してください」と警告。誤った全体書き換えによるフック設定消失を防止 | 中 |

---

## 観察事項

- **Codex レビューイテレーション数の異常増加**: plan.md 1件に対して最大18回のレビューが発生している。これは plan.md の構造よりも「Codex に何を聞いているか（プロンプト品質）」の問題である可能性が高い。`codex-review` スキルの `base-instructions` パラメータ設計の見直しを検討する価値がある
- **`docker-compose.yml` の繰り返し編集**: MariaDB 追加・phpMyAdmin 設定変更・volumes 追加など数回の編集が行われた。インフラ変更を1回の計画で完結させる習慣がまだ確立されていない
- **`MEMORY.md` の定期的な更新**: 各セッションで重要な発見をメモリに保存するパターンは適切に機能している。自動化より手動継続を推奨