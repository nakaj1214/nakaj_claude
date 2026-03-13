---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

# スキル候補レポート — 2026-03-11 09:04

## 検出されたパターン

- **create-proposal → create-plan → implement-plans の連鎖実行**: セッション全体を通じて 3 スキルが順番に自動起動するパターンが明確に存在した
- **Codex レビューループの複数イテレーション**: `mcp__codex__codex` を呼び出し → `review_1.md` を読む → Blocking 修正 → 再呼び出し、が 4 回繰り返された
- **Read 忘れによる Edit エラー**: 「File has not been read yet. Read it first」エラーが同一セッション内で 4 回以上発生した
- **番号付きファイルの引数渡し**: デフォルト (`proposal.md`) ではなく `proposal_1.md` / `plan_1.md` を使用するため、引数でファイル番号を指定するパターンが出現した
- **複数ファイル横断の `btn-outline` 一括置換**: Blade / JS / CSS の 4〜5 ファイルを個別に検索・置換する作業が繰り返し発生した

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `full-pipeline` | 「proposal から実装まで一気に」「prompt.md を実装して」「フルパイプラインで」 | `create-proposal` → `create-plan` → `implement-plans` を引数付きで連続実行するラッパー。番号付きファイル（`prompt_1.md` → `proposal_1.md` → `plan_1.md`）にも対応 | 高 |
| `read-then-edit` | *(フック候補に移管)* | Edit 前に自動 Read を強制するガードスキルまたはプレフライトチェック | 高 |

---

## エージェント候補

*(今回のセッションで 2 回以上出現した独立エージェントユースケースはありませんでした)*

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PreToolUse (Edit) | `tool_name == "Edit"` かつ対象ファイルが未読 | 編集前に対象ファイルを自動 Read してからEditを実行。「File has not been read yet」エラーを根絶 | 高 |
| PostToolUse (mcp__codex__codex) | Codex 呼び出し完了後 | `review_*.md` を自動 Read して判定（APPROVED / CHANGES_REQUIRED）をユーザーにサマリー通知。手動 Read コマンドを省略 | 中 |

---

## 観察事項

- **番号付きファイル命名規則**: `proposal_1.md` / `plan_1.md` のように番号を付けるパターンが出現したが、既存スキルがデフォルトで `proposal.md` / `plan.md` を想定しているため齟齬が生じやすい。`create-proposal` の INSTRUCTIONS に「引数が渡された場合は番号付きファイルを出力先にする」旨を追記するだけで解決可能（スキル新規作成は不要）。
- **Codex レビュー 4 イテレーション**: 1 回目で Blocking が 5 件、合計 4 回で APPROVED という結果は許容範囲内だが、初回の plan.md に「影響ファイル一覧」「テストコマンド」「認可方針」が不足していることが繰り返しの原因。`create-plan` の INSTRUCTIONS に「影響ファイル表を必須とし、`php artisan test` コマンドは `cd src &&` 付きで記載する」を追加すると初回 Blocking を減らせる可能性がある。