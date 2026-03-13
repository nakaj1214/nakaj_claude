---
tags: ['session', 'automation']
scope: session
date: 2026-03-09
---

# スキル候補レポート — 2026-03-09 11:05

## 検出されたパターン

- **Codex 実行ブロック問題**: `codex exec` コマンドに `2>/dev/null` / `2>&1` が含まれると Slack 承認フックがリダイレクト検出して `require` 判定し、毎回承認を求める（3回発生）
- **create-plan → codex-review の連携**: `create-plan` スキルから Codex レビューを呼び出す際、Task ツール経由 / Bash 直接実行 / バックグラウンド実行を試行し、正解パターン（`run_in_background: true` + リダイレクトなし）にたどり着くまで複数回失敗
- **proposal.md 品質チェック**: proposal.md が曖昧な記述を含む場合、plan 作成前にリライトが必要。今回もチェック → リライト → 確認 → 再実行という流れが発生
- **MEMORY.md への学習記録**: Codex 実行方法の正解パターンを MEMORY.md に記録（セッション終盤で毎回実施）

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `codex-exec-safe` | 「Codex を実行して」「codex-review が動かない」「Codex が止まる」 | リダイレクトなし・モデル指定なし・`run_in_background: true` の安全な Codex 実行ラッパー。`approval_skip_patterns.txt` の `skip:codex` に依存しない安定実行パターンを提供 | 高 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| `PreToolUse` (Bash) | `codex exec` コマンドに `2>/dev/null` または `2>&1` が含まれる | コマンドからリダイレクトを自動除去してスキップ判定させる、または approve を自動で返す。Slack への通知を避けつつ Codex 実行をスムーズにする | 高 |

---

## 観察事項

- **codex-review INSTRUCTIONS.md の更新推奨**: Codex 実行時のリダイレクト問題は既知の解決策が出ているが、`codex-review/INSTRUCTIONS.md` にはまだ記載されていない。次回同じ失敗を防ぐため、「`2>/dev/null` 等のリダイレクトを使わない」という注意書きを追記することを推奨
- **Task ツール（サブエージェント）の承認ブロック**: サブエージェント内の Bash 実行も Slack 承認フックの対象になる。`approval_skip_patterns.txt` にサブエージェント向けのパターンを追加することを検討
- **TaskOutput のタイムアウト**: `run_in_background` で実行した Codex の完了を `TaskOutput` でポーリングする際、デフォルトタイムアウトで `<retrieval_status>timeout</retrieval_status>` が2回発生した。長時間タスクの場合の完了確認方法を標準化する余地がある