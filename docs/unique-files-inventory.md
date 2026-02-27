# 各プロジェクト固有ファイル一覧

`_shared` フォルダに存在しない、各プロジェクト独自のファイルまとめ。

---

## blade_management/.claude/
**特徴**: Slack承認システム・設計追跡システム（create-planスキルのみエージェント連携）
> ⚠️ skills/rules/hooks/docs はすべて `_shared/` に移植済み。blade_management に固有ファイルなし。

### archive/docs/research/

| ファイル | 説明 | 備考 |
|---------|------|------|
| `order-request-ui-fixes.md` | blade_management プロジェクトの発注確認UI修正調査メモ（2026-02-02） | プロジェクト固有の調査結果。保存のみ |

---

## VBA_extension/.claude/

**特徴**: セキュリティ重視・コードレビューワークフロー・大規模スキルライブラリ

### skills/（要確認）

| ファイル | 説明 | 状態 |
|---------|------|------|
| `skills/agents/receiving-code-review/SKILL.md` | コードレビューを受け入れる際のワークフロー | **削除候補** |
| `skills/agents/requesting-code-review/SKILL.md` | コードレビューを依頼する際のワークフロー | **削除候補** |
| `skills/agents/requesting-code-review/code-reviewer.md` | コードレビュアーエージェント定義 | **削除候補** |
| `skills/agents/verification-before-completion/SKILL.md` | タスク完了前の検証プロセス | **削除候補** |

### skills-unused/（実験的・未使用スキル置き場）

#### advanced-security/

| ディレクトリ | 内容 | 備考 |
|------------|------|------|
| `insecure-defaults/` | 安全でないデフォルト設定の検出スキル | GitHub Advanced Security 連携 |
| `static-analysis/` | CodeQL・Semgrep・SARIF解析スキル群 | GHAS静的解析ワークフロー一式 |

#### agents/

| ディレクトリ | 内容 | 備考 |
|------------|------|------|
| `dispatching-parallel-agents/` | 並列エージェント起動パターン | `_shared/skills/` への移植候補 |
| `subagent-driven-development/` | サブエージェント駆動開発ワークフロー（実装・レビュー・仕様確認の3エージェント構成） | `requesting-code-review` スキルと関連 |
| `using-superpowers/` | superpowers エージェントタイプの使い方 | `_shared/skills/` への移植候補 |
| `writing-skills/` | スキル作成ガイド（Anthropicベストプラクティス・説得原則） | `_shared/skills/` への移植候補 |

#### anthropics/

Anthropic公式スキルパッケージ群。用途別に独立しており、必要なものだけ個別に活用可能。

| ディレクトリ | 内容 |
|------------|------|
| `algorithmic-art/` | アルゴリズム生成アート（JS + HTML viewer） |
| `brand-guidelines/` | Anthropicブランドガイドライン |
| `canvas-design/` | Canvas APIデザイン（多数のフォント同梱） |
| `doc-coauthoring/` | ドキュメント共同作成ワークフロー |
| `internal-comms/` | 社内コミュニケーション文書テンプレート |
| `mcp-builder/` | MCPサーバー構築スキル（Node/Python対応） |
| `pptx/` | PowerPoint生成スキル（OOXML スキーマ同梱） |
| `skill-creator/` | スキル作成・パッケージングスキル |
| `slack-gif-creator/` | Slack用GIF作成スキル（Python） |
| `theme-factory/` | デザインテーマ生成スキル |
| `web-artifacts-builder/` | Webアーティファクト構築スキル（shadcn同梱） |

#### skills-best-practice/

スキル・エージェント・フック・ワークフローの実装例集。

| ディレクトリ | 内容 |
|------------|------|
| `agents/` | エージェント定義例 |
| `commands/` | コマンド定義例 |
| `hooks/` | フック設定例（音声通知付き完全実装） |
| `skills/` | スキル定義例（weather-fetcher、weather-transformer） |
| `workflow/rpi/` | RPI（Research→Plan→Implement）ワークフロー一式 |

### その他

| ファイル | 説明 |
|---------|------|
| `skills-anthropics/` | Anthropic公式スキル配置用プレースホルダ（空フォルダ） |

---

## サマリー

| プロジェクト | 状態 |
|------------|------|
| **blade_management** | `docs/research/order-request-ui-fixes.md` のみ残存（保存用） |
| **VBA_extension** | `skills/agents/` 4ファイルが移植予定（superpowers リポジトリ確認後に実行）。`skills-unused/` は未使用スキル倉庫として維持 |
