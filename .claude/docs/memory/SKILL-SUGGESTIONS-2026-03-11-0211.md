---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

# スキル候補レポート — 2026-03-11 02:11

## 検出されたパターン

- `create-proposal` → `create-plan` → `codex-review` → `implement-plans` のフルワークフローが1セッション内で完結した
- `codex exec` が2回連続でタイムアウト・ハングし、毎回サブエージェントによる手動フォールバックが必要だった（b5ia8vlk8、b6okzl0r7）
- `create-proposal` のデフォルトパス（`docs/implement/`）と実際の作業ディレクトリ（`docs/skills-create-plan/`）が異なり、引数指定が必要だった
- 4つの Slack フックファイルに同一パターンの変更（`is_work_hours()` インポート＋チェック追加）を並列適用した

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `codex-exec-with-fallback` | 「Codex でレビューして」「codex-review を使って」 | `codex exec` を Bash 直接実行し、タイムアウト（120秒）またはハング検出時はサブエージェントによるレビューに自動フォールバック。フォールバック理由をユーザーに通知する | 高 |
| `create-proposal-with-path` | 「このディレクトリで proposal を作って」「同階層で実行して」 | `create-proposal` の `prompt.md` / `proposal.md` のパスをスキル引数で上書き可能にする。デフォルトは `docs/implement/`、引数指定時はそのディレクトリを使用 | 中 |

## エージェント候補

このセッションでは特筆すべきパターンは検出されませんでした。

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse: Bash | `codex exec` を含む Bash コマンドがタイムアウト（exit code 124 またはプロセス残留なし）で終了 | 「Codex がタイムアウトしました。サブエージェントによるフォールバックレビューを実行しますか？」と提案 | 中 |

## 観察事項

- **`docs/implement/` 固定パスの設計制約**: `create-proposal` と `create-plan` は `docs/implement/` を固定パスとしているが、今回のように `docs/skills-create-plan/` 等の別ディレクトリで作業するケースが発生した。スキル引数での上書きを標準サポートにすることで混乱を防げる（今回は引数 `同階層のパスで実行して` で対処）
- **Slack フック一括変更パターン**: 4ファイルに同一の `is_work_hours()` チェックを追加するパターンは今回1回だが、今後フックに共通処理を追加するたびに同様の作業が発生する可能性がある。`bulk-text-replace` スキルで代替可能