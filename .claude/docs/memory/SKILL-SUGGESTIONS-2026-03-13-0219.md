---
tags: ['session', 'automation']
scope: session
date: 2026-03-13
---

# スキル候補レポート — 2026-03-13 02:19

## 検出されたパターン

- `docs/implement/proposal.md` → `plan.md` の Write による全面書き直しが1セッション内で6〜10回以上発生
- `excel_range_select_copy.js` への編集が35回以上集中（box-shadow → outline → ::after と3回アプローチピボット）
- JS ファイルのクラス名変更時に対応する CSS が未更新でスタイル不整合が発生
- Codex レビューが20回近く繰り返される（1回の plan.md に対して最大25回超）
- `settings.json` を同一セッション内で4〜5回修正（`disabledMcpjsonServers`、matcher 設定など）
- Slack フックスクリプト（`slack_approval.py`, `notify-slack.py`, `stop-notify.py`）に同一パターンの変更（勤務時間チェック追加）が3ファイルに繰り返し適用

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `js-css-sync-check` | 「セル選択」「ハイライト」「box-shadow」「outline」などUIスタイル変更後に自動 | 変更した JS ファイルで参照されるCSSクラス名をGrepし、対応する CSS ファイルに定義があるかを確認・報告する | 高 |
| `codex-review-budget` | `create-plan` スキル実行時に自動トリガー | Codex レビューが5回を超えた場合に plan.md のサイズを計測し、300行を超えているなら「スコープ分割を検討してください」と警告する | 高 |
| `settings-validator` | `.claude/settings.json` を Edit/Write した後に自動 | `settings.json` を JSON パースして matcher・hooks キー構造を検証し、不正な構造があれば即時報告する | 中 |
| `hook-batch-apply` | 「全Slackフックに○○を追加して」と言われたとき | 指定した変更を全Slackフックスクリプトに一括適用するスキル | 中 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse (Write) | `docs/implement/plan.md` または `proposal.md` へのWrite | セッション内のWrite回数をカウントし、3回以上なら「計画が安定していません。実装を開始する前に計画を固めてください」と警告を stderr に出力 | 高 |
| PostToolUse (Edit) | `excel_range_select_copy.js` などUIスタイルに関わるJSファイルの編集 | 編集内容にCSSクラス名の追加/変更が含まれる場合、対応するCSSファイルへの確認を促すメッセージを表示 | 高 |
| PostToolUse (Edit) | `.claude/settings.json` の編集 | `python3 -c "import json; json.load(open('.claude/settings.json'))"` で構文チェックを実行し、エラーがあれば報告 | 中 |

---

## 観察事項

- **Codex レビューのタイムアウト問題**: Task サブエージェント経由での `codex exec` 実行が不安定で、MCP 方式への移行が複数回記録されている。自動化よりもドキュメント整備（lessons.md への記録）で対応済み。
- **`docker-compose.yml` の繰り返し編集**: MariaDB サービス追加と phpmyadmin 設定が複数回修正されているが、構造理解の問題であり自動化対象ではない。
- **インライン JS 禁止ルール**: Blade から JS ファイルへの移行作業が繰り返し発生しており、`no-inline-js.md` ルールが既に作成済み。ルールの適用徹底で対応可能。