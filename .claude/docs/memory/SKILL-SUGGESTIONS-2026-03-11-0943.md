---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

# スキル候補レポート — 2026-03-11 09:43

## 検出されたパターン

- **numbered ファイル運用** (`prompt_1.md` → `proposal_1.md` → `plan_1.md` → `review_1.md`) — デフォルトのファイル名と異なる連番を毎回使用
- **3段階手動トリガー** — `/create-proposal` → `/create-plan` → (自動) implement-plans を毎回順次起動
- **Codex exec タイムアウト → MCP へ切替** — `codex exec` bash 実行がタイムアウトし、`mcp__codex__codex` へ手動で切り替えた（MEMORY.md に記録済みだが今回も同じエラーが発生）
- **Edit 前の読み取り忘れ** — "File has not been read yet" エラーが複数回発生（5件以上）
- **Docker 未起動による構文チェック失敗** — `php -l` で `service "php" is not running`、スキップして続行

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `prompt-to-impl` | 「prompt_N.md から実装して」「一気通貫で」「フルパイプラインで」 | 引数 `N` を受け取り `prompt_N.md` → `proposal_N.md` → `plan_N.md` → Codex レビューループ → implement-plans までを中断なしで実行。`propose-one` の完全版 | 高 |
| `numbered-file-workflow` | ユーザーが `prompt_1.md` のように連番ファイルを指定 | 連番 N を引数として受け取り、create-proposal / create-plan / implement-plans の Fixed Files を `_N` サフィックスで自動解決する共通ヘルパー | 中 |

---

## エージェント候補

現時点で特筆すべきエージェント候補はありません。

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PreToolUse (Bash) | `codex exec` コマンドが実行される直前 | 「`codex exec` は廃止済み。`mcp__codex__codex` ツールを使うよう変更してください」と警告し、実行をブロックする | 高 |
| PostToolUse (Bash) | `docker compose exec` の終了コードが 1 かつ `is not running` を含む | 「Docker が起動していません。`docker compose up -d` を実行してから再試行してください」と自動通知 | 中 |

---

## 観察事項

- **Edit 前の読み取り忘れ**: ルールとして「Edit の直前に Read を行う」は coding-principles に記載可能だが、フックでの強制は難しい。代わりに implement-plans の INSTRUCTIONS.md に「並列 Edit は必ず先に並列 Read してから」を明記する改善が有効
- **Codex レビュー 4 回**: blocking 指摘はどれも「影響ファイル漏れ」「テストコマンドの実行パス」など plan.md の記述品質の問題。plan_1.md テンプレートの影響ファイルセクションに「routes/web.php」「layouts/app.blade.php」を必須記載として明示すれば削減できる可能性がある

---

**ユーザーへの提案**

最優先は `codex exec` ブロックフックです。今回のセッションで再発しており、MEMORY.md 記録済みにもかかわらず同じ問題が起きています。フックでブロックすれば根絶できます。

フルパイプラインスキル (`prompt-to-impl`) は「`propose-one` の implement-plans 自動発火版」として既存スキルを統合する形が最もシンプルです。新規ファイルを作らず `propose-one` の INSTRUCTIONS.md を拡張することを推奨します。