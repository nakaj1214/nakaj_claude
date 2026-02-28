# 各プロジェクト固有ファイル一覧

`_shared` フォルダに存在しない、各プロジェクト独自のファイルまとめ。

---

## blade_management/.claude/
**特徴**: Slack承認システム・設計追跡システム
> ⚠️ skills/rules/hooks/docs はすべて `_shared/` に移植済み。blade_management に固有ファイルなし。

### archive/docs/research/

| ファイル | 説明 | 備考 |
|---------|------|------|
| `order-request-ui-fixes.md` | blade_management プロジェクトの発注確認UI修正調査メモ（2026-02-02） | プロジェクト固有の調査結果。保存のみ |

---

## VBA_extension/.claude/

**特徴**: OCR Project（PHP/Laravel + Python OCR）プロジェクト固有設定のみ残存

> 更新: 2026-03-01 ― 全ての汎用ファイルを _shared に移植・重複削除完了

### トップレベル（固有ファイルのみ）

| ファイル | 説明 | 状態 |
|---------|------|------|
| `CLAUDE.md` | OCR Projectの技術スタック・プロジェクト構造・規約定義 | 維持（_shared と別内容） |
| `settings.local.json` | VBA_extension ローカル設定 | 維持 |
| `skills-reorganization-plan.md` | スキル整理計画ドキュメント | 参照用として維持 |

> `skills/` フォルダは全て _shared に移植済み。VBA_extension に独自スキルは存在しない。

---

## _shared/ 現在のスキル一覧

> **注意**: 全てフォルダ型（`スキル名/SKILL.md`）に統一済み
> 対象: Laravel / Python が動作する Docker プロジェクト共通設定

### エージェント系スキル（`skills/agents/`）

| スキル | 説明 |
|--------|------|
| `agents/dispatching-parallel-agents/` | 並列エージェント起動パターン |
| `agents/receiving-code-review/` | コードレビューを受け取るワークフロー |
| `agents/requesting-code-review/` | コードレビューを依頼するワークフロー |
| `agents/subagent-driven-development/` | サブエージェント駆動開発ワークフロー |
| `agents/using-superpowers/` | superpowers スキル使用ガイド |
| `agents/verification-before-completion/` | タスク完了前の検証プロセス |
| `agents/writing-skills/` | スキル作成ガイド（Anthropicベストプラクティス） |

### セキュリティ系スキル

| スキル | 説明 |
|--------|------|
| `security/owasp-security/` | OWASPセキュリティスキル |
| `security/varlock/` | Varlockセキュリティスキル |
| `security/OWASP-2025-2026-Report.md` | OWASP 2025-2026 レポート（参照用） |
| `advanced-security/insecure-defaults/` | 安全でないデフォルト設定の検出 |
| `advanced-security/codeql/` | CodeQL静的解析スキル |
| `advanced-security/sarif-parsing/` | SARIF解析スキル |
| `advanced-security/semgrep/` | Semgrep静的解析スキル |

### Git 系スキル

| スキル | 説明 |
|--------|------|
| `git/finishing-a-development-branch/` | 開発ブランチ完了スキル |
| `git/git-worktrees/` | Git Worktrees 並行作業スキル |

### フロントエンド系スキル

| スキル | 説明 |
|--------|------|
| `accessibility/` | アクセシビリティガイド |
| `css-features/` | CSS機能リファレンス |
| `css-layout/` | CSSレイアウトリファレンス |
| `css-modern/` | モダンCSSリファレンス |
| `css-organization/` | CSS構成ガイド |
| `frontend-design/` | フロントエンドデザインスキル |
| `frontend-ui-ux/` | フロントエンドUI/UXガイド |

### ワークフロー系スキル

| スキル | 説明 |
|--------|------|
| `brainstorming/` | ブレインストーミングワークフロー |
| `code-review/` | コードレビューガイド |
| `create-plan/` | 実装計画作成 |
| `executing-plans/` | 計画実行スキル |
| `planning-with-files/` | ファイルを使った計画 |
| `simplify/` | コード簡略化スキル |
| `systematic-debugging/` | 体系的デバッグ |
| `tdd-workflow/` | TDDワークフロー（旧） |
| `test-driven-development/` | TDDワークフロー |
| `writing-plans/` | 計画書作成スキル |

### ツール系スキル

| スキル | 説明 |
|--------|------|
| `claude-code-setup/` | Claude Code セットアップガイド |
| `claude-md-management/` | CLAUDE.md 管理スキル |
| `design-tracker/` | デザイン追跡スキル |
| `hookify/` | Hookifyルール作成ガイド |
| `init/` | プロジェクト初期化スキル |
| `mcp-builder/` | MCPサーバー構築ガイド |
| `research-lib/` | ライブラリ調査スキル |
| `skill-creator/` | スキル作成評価ツール |
| `update-design/` | デザイン更新スキル |
| `update-lib-docs/` | ライブラリドキュメント更新スキル |
| `wolfram-foundation-tool/` | Wolfram Foundationツールスキル |

### プラグイン開発スキル

| スキル | 説明 |
|--------|------|
| `plugin-dev/agent-development/` | エージェント開発スキル |
| `plugin-dev/command-development/` | コマンド開発スキル |
| `plugin-dev/hook-development/` | フック開発スキル |
| `plugin-dev/mcp-integration/` | MCP統合スキル |
| `plugin-dev/plugin-structure/` | プラグイン構造スキル |
| `plugin-dev/skill-development/` | スキル開発スキル |

### VBA 系スキル

| スキル | 説明 |
|--------|------|
| `vba-core/` | VBA基礎スキル |
| `vba-development/` | VBA開発スキル |
| `vba-excel/` | VBA/Excelスキル |
| `vba-patterns/` | VBAパターンガイド |

---

## hooks 現在の一覧（_shared/hooks/）

| ファイル | 用途 | イベント |
|---------|------|---------|
| `notify-slack.py` | ユーザー質問時にSlack通知 | PreToolUse: AskUserQuestion |
| `slack_approval.py` | Bashコマンド実行前にSlack承認 | PreToolUse: Bash |
| `edit-approval.py` | ファイル編集前にSlack承認（EDIT_APPROVAL_ENABLED=1 で有効） | PreToolUse: Edit\|Write\|NotebookEdit |
| `stop-notify.py` | Claude応答完了時にSlack通知 | Stop |
| `lint-on-save.py` | ファイル保存時にlint実行 | PostToolUse: Edit/Write |
| `post-implementation-review.py` | 実装後レビュー | PostToolUse: Edit/Write |
| `post-test-analysis.py` | テスト実行後の分析 | PostToolUse: Bash |
| `slack_socket_daemon.py` | Slack Socket Mode デーモン | - |

---

## superpowers（obra/superpowers）との対応状況

| superpowers スキル | _shared での対応 | 状態 |
|------------------|----------------|------|
| `test-driven-development` | `test-driven-development/` | ✅ |
| `systematic-debugging` | `systematic-debugging/` | ✅ |
| `brainstorming` | `brainstorming/` | ✅ |
| `writing-plans` | `writing-plans/` | ✅ |
| `executing-plans` | `executing-plans/` | ✅ |
| `finishing-a-development-branch` | `git/finishing-a-development-branch/` | ✅ |
| `using-git-worktrees` | `git/git-worktrees/` | ✅ |
| `subagent-driven-development` | `agents/subagent-driven-development/` | ✅ |
| `dispatching-parallel-agents` | `agents/dispatching-parallel-agents/` | ✅ |
| `verification-before-completion` | `agents/verification-before-completion/` | ✅ |
| `requesting-code-review` | `agents/requesting-code-review/` | ✅ |
| `receiving-code-review` | `agents/receiving-code-review/` | ✅ |
| `writing-skills` | `agents/writing-skills/` | ✅ |
| `using-superpowers` | `agents/using-superpowers/` | ✅ |

---

## サマリー

| プロジェクト | 状態 |
|------------|------|
| **blade_management** | `docs/research/order-request-ui-fixes.md` のみ残存（保存用） |
| **VBA_extension** | `CLAUDE.md`・`settings.local.json`・`skills-reorganization-plan.md` の3ファイルのみ。スキルは全て _shared に移植済み |
| **_shared** | 計50+スキル。全プロジェクト共通の設定・スキル・hooks を一元管理 |

---

## バックグラウンドエージェント Edit/Write 承認フロー

`edit-approval.py` を新規作成（2026-03-01）。

### 有効化方法

`setting.json` の `env` セクションに追加：
```json
"EDIT_APPROVAL_ENABLED": "1"
```

### 動作

1. バックグラウンドエージェントが Edit/Write/NotebookEdit を実行しようとすると Slack 通知
2. 承認者が ✅ リアクションまたはスレッド返信「allow」→ 編集を許可
3. ❌ リアクションまたは「deny」→ 編集をブロック
4. 5分タイムアウト → 編集をブロック（フェイルクローズ）

デフォルトは**無効**（EDIT_APPROVAL_ENABLED=0）。必要なプロジェクトの `settings.local.json` で有効化。
