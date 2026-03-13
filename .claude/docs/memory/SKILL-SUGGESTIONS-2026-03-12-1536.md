---
tags: ['session', 'automation']
scope: session
date: 2026-03-12
---

# スキル候補レポート — 2026-03-12 15:36

## 検出されたパターン

- `docs/implement/plan.md` が Write ツールで20回以上上書き（繰り返し計画書き直し）
- `docs/implement/review.md` が18回以上作成され、Codex レビューループが長期化（最終的に18回目で APPROVED）
- `excel_range_select_copy.js` への集中的な編集（セル選択 outline 問題が3回異なるアプローチで修正試行）
- JS ファイル（`excel_range_select_copy.js`）変更後に対応する CSS（`stock.css`）への追加修正が毎回発生
- `.claude/settings.json` の `matcher` フィールドが複数回往復編集（`Bash` → `Bash|mcp__codex__codex` → `Bash`）
- `docs/implement/proposal.md` も8回以上 Write で上書き（要件書の繰り返し更新）
- セッション終了時に毎回 HANDOVER.md を生成

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| plan-quality-preflight | 「plan.md を作成して」「create-plan」実行前 | plan.md 作成前に proposal.md の完全性（Before/After・対象ファイル・受入条件の3点）を自動チェックし、不足があれば proposal.md の補強を優先する。レビュー前に計画の品質を保証し、18回ループを防止する | 高 |
| codex-loop-limiter | Codex レビューが5回を超えた場合 | `CHANGES_REQUIRED` が5回続いた時点でループを中断し、「計画のアプローチを根本的に見直す必要があります」とユーザーに報告。同じ修正の繰り返しで時間を浪費しないための安全装置 | 高 |

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| js-ui-verifier | JS の UI スタイル変更後（セル描画・ボーダー・背景色など）に自動起動 | 変更された JS ファイルで参照している CSS クラス名を抽出し、対応する CSS ファイル内に定義が存在するか照合。未定義クラスをリストアップして報告する | 高 |
| settings-reviewer | `.claude/settings.json` 編集後に自動起動 | `matcher` パターンの構文検証、`hooks` の `command` パスの存在確認、前後の差分サマリーをSlack通知用にフォーマット | 中 |

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse (Write) | `docs/implement/plan.md` または `docs/implement/proposal.md` への Write が3回を超えた場合 | 「計画書が3回以上書き直されています。実装前に要件を確定させましたか？」という警告を stderr に出力する（`plan-rewrite-alert.py` — staging に存在、本番適用待ち） | 高 |
| PostToolUse (Edit) | Edit ツールで `lines_removed >= 20` の場合 | 「大量削除（{N}行）が検出されました。アプローチをピボットしていますか？前の実装を archive/ に保存しましたか？」と警告する（`large-delete-guard.py` — staging に存在、本番適用待ち） | 中 |
| PostToolUse (Edit) | `excel_range_select_copy.js` または対応する `*.css` ファイルの一方のみが変更された場合 | JS/CSS のペア変更チェックを促す通知を出力する（js-css-sync-check スキルを起動するよう提案） | 中 |

## 観察事項

- **Codex レビューの長期化**: 今セッションで plan.md のレビューが18回繰り返されたが、多くの指摘は「影響範囲の明記不足」「既存実装との競合の未考慮」に集中していた。proposal.md の品質チェック（plan-quality-preflight）を事前に実施すれば、レビュー回数を3〜5回程度に削減できると推定される。
- **staging の hooks が本番未適用**: `plan-rewrite-alert` と `large-delete-guard` が staging に生成済みだが、`settings.json` にはまだ登録されていない。`/materialize` → `/review-staged` の流れで適用を検討すること。
- **settings.json の往復編集**: `matcher` を `Bash|mcp__codex__codex` に変更後すぐに `Bash` に戻す編集パターンが見られた。MCP ツールは Bash フックの対象外であることをルールに明記すると同種の手戻りを防げる。