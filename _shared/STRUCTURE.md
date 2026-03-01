# _shared/ 構造ガイド

各プロジェクトの `.claude/` フォルダに重複していたファイルを集約した共有フォルダ。

---

```
_shared/
│
│  # ===== ドキュメント類 =====
│
├── README.md                # このテンプレートの概要・使い方
├── INSTALLATION.md          # 導入手順
├── STRUCTURE.md             # フォルダ構造の説明
├── CLAUDE.md                # Claude Code に読み込ませるメインの指示ファイル
│
│  # ===== Claude Code の動作設定 =====
│
├── .claudeignore            # Claude に読ませないファイルのパターン (gitignore と同じ書式)
├── claude_settings.json     # Claude Code の推奨設定値 (モデル・権限・表示など)
├── custom_instructions.md   # Claude への恒久的な振る舞い指示 (「実装前に読め」「セキュリティ優先」等)
│
│  # ===== 参照ドキュメント =====
│
├── context-management.md    # コンテキストウィンドウの管理方法・注意事項
├── prompt_templates.md      # よく使うプロンプトのテンプレート集
├── quick_start.md           # Claude Code を使い始めるためのクイックガイド
├── agent_usage_guide.md     # サブエージェント (Task tool) の使い方ガイド
│
│  # ===== agents/ =====
│  # Claude Code の /agent コマンドで呼び出せる専門エージェント定義
│  # 各ファイルが「役割・使い方・出力フォーマット」を定義する
│
├── agents/
│   ├── agent-creator.md         # エージェント定義ファイル作成エージェント
│   ├── architect.md             # 設計・アーキテクチャ検討エージェント
│   ├── build-error-resolver.md  # ビルドエラー解消エージェント
│   ├── code-architect.md        # コード設計レビューエージェント
│   ├── code-explorer.md         # コードベース探索エージェント
│   ├── code-reviewer.md         # コードレビューエージェント
│   ├── code-simplifier.md       # コード簡素化エージェント
│   ├── comment-analyzer.md      # コメント品質分析エージェント
│   ├── conversation-analyzer.md # 会話・要件分析エージェント
│   ├── database-reviewer.md     # DB 設計レビューエージェント
│   ├── debugger.md              # デバッグ・原因調査エージェント
│   ├── doc-updater.md           # ドキュメント更新エージェント
│   ├── documenter.md            # ドキュメント生成エージェント
│   ├── e2e-runner.md            # E2E テスト実行エージェント
│   ├── performance.md           # パフォーマンス改善エージェント
│   ├── planner.md               # タスク分解・実装計画エージェント
│   ├── plugin-validator.md      # プラグイン検証エージェント
│   ├── pr-test-analyzer.md      # PR テスト分析エージェント
│   ├── python-reviewer.md       # Python コードレビューエージェント
│   ├── refactor-cleaner.md      # リファクタリング整理エージェント
│   ├── refactorer.md            # リファクタリングエージェント
│   ├── reviewer.md              # 汎用レビューエージェント
│   ├── security-reviewer.md     # セキュリティレビューエージェント
│   ├── silent-failure-hunter.md # サイレント障害検出エージェント
│   ├── skill-reviewer.md        # スキル定義レビューエージェント
│   ├── tdd-guide.md             # TDD ガイドエージェント
│   ├── tester.md                # テスト設計・TDD エージェント
│   └── type-design-analyzer.md  # 型設計分析エージェント
│
│  # ===== commands/ =====
│  # /コマンド名 で呼び出せるカスタムスラッシュコマンドの定義
│
├── commands/
│   ├── build-fix.md         # /build-fix      → ビルドエラーの修正
│   ├── cancel-ralph.md      # /cancel-ralph   → ralph ループのキャンセル
│   ├── checkpoint.md        # /checkpoint     → 作業チェックポイントの記録
│   ├── clean_gone.md        # /clean-gone     → 削除済みブランチの掃除
│   ├── code-review.md       # /code-review    → コードレビューの実行
│   ├── commit.md            # /commit         → コミットの作成
│   ├── commit-push-pr.md    # /commit-push-pr → コミット・プッシュ・PR 作成
│   ├── create-plugin.md     # /create-plugin  → プラグインの雛形生成
│   ├── e2e.md               # /e2e            → E2E テストの実行
│   ├── feature-dev.md       # /feature-dev    → 機能開発フロー
│   ├── hookify.md           # /hookify        → フック設定の生成
│   ├── hookify-configure.md # /hookify-configure → フックの設定変更
│   ├── hookify-help.md      # /hookify-help   → フックのヘルプ
│   ├── hookify-list.md      # /hookify-list   → フック一覧表示
│   ├── orchestrate.md       # /orchestrate    → 複数エージェントの協調実行
│   ├── plan.json            # /plan           → 機能実装計画の作成
│   ├── ralph-help.md        # /ralph-help     → ralph のヘルプ
│   ├── ralph-loop.md        # /ralph-loop     → ralph による反復実行
│   ├── refactor-clean.md    # /refactor-clean → リファクタリングと整理
│   ├── review.json          # /review         → コードレビューの実行
│   ├── review-pr.md         # /review-pr      → PR のレビュー
│   ├── revise-claude-md.md  # /revise-claude-md → CLAUDE.md の改訂
│   ├── tdd.json             # /tdd            → TDD サイクルの実行
│   ├── test-coverage.md     # /test-coverage  → テストカバレッジの確認
│   ├── update-docs.md       # /update-docs    → ドキュメントの更新
│   └── verify.md            # /verify         → 実装の検証
│
│  # ===== contexts/ =====
│  # 作業モード別のコンテキスト設定
│
├── contexts/
│   ├── dev.md               # 開発モード用コンテキスト設定
│   ├── research.md          # 調査モード用コンテキスト設定
│   └── review.md            # レビューモード用コンテキスト設定
│
│  # ===== docs/ =====
│  # プロジェクト共通の設計ドキュメント
│
├── docs/
│   └── DESIGN.md            # システム設計ドキュメント
│
│  # ===== hooks/ =====
│  # Pre/Post ToolUse 等のイベントで自動実行されるフックスクリプト
│
├── hooks/
│   ├── pre-compact-handover.py      # PreCompact フック: 自動コンパクション前に HANDOVER + SKILL-SUGGESTIONS を生成
│   ├── edit-approval.py             # ファイル編集時の承認フック
│   ├── lint-on-save.py              # 保存時の自動 Lint フック
│   ├── notify-slack.py              # Slack 通知フック
│   ├── post-implementation-review.py # 実装後レビューフック
│   ├── post-test-analysis.py        # テスト後分析フック
│   ├── slack_approval.py            # Slack 経由の承認フック
│   ├── slack_socket_daemon.py       # Slack ソケット接続デーモン
│   ├── stop-notify.py               # 停止通知フック
│   ├── approval_skip_patterns.txt   # 承認スキップ対象パターン一覧
│   ├── lib/                         # フック共通ライブラリ（複数フックで再利用）
│   │   ├── transcript.py            # JSONL トランスクリプト読み込み・テキスト変換
│   │   └── claude_p.py              # claude -p 呼び出しユーティリティ
│   └── tests/
│       └── test_slack_approval.py   # slack_approval.py のテスト
│
│  # ===== meta/ =====
│  # _shared 自体の品質管理・自動生成スクリプト
│
├── meta/
│   ├── generate-registry.py         # 全スキルの SKILL.md を読んで registry/skills.yaml を生成
│   └── health-check.py              # スキル品質監査（evals 欠損・SKILL.md 肥大化・未登録・重複検出）
│
│  # ===== registry/ =====
│  # スキルルーティングインデックス（meta/generate-registry.py で自動生成）
│
├── registry/
│   └── skills.yaml                  # 全スキルの name / path / description / tags / triggers 一覧
│
│  # ===== mcp/ =====
│  # MCP (Model Context Protocol) サーバー設定のテンプレート集
│  # Claude Code に外部ツール連携を追加するための設定
│
├── mcp/
│   ├── mcp-guide.md             # MCP とは何か・導入方法のガイド
│   ├── mcp-by-technology.md     # 技術スタック別おすすめ MCP サーバー一覧
│   ├── universal-mcp-servers.md # 言語問わず汎用的に使える MCP サーバー
│   ├── context7-setup.md        # Context7 (ライブラリドキュメント取得) の設定手順
│   ├── mcp-settings-example.json    # settings.json への MCP 記述サンプル
│   ├── settings-javascript.json     # JS/TS プロジェクト向け MCP 設定
│   ├── settings-laravel-php.json    # Laravel/PHP プロジェクト向け MCP 設定
│   ├── settings-linux.json          # Linux サーバー向け MCP 設定
│   ├── settings-python.json         # Python プロジェクト向け MCP 設定
│   ├── settings-vba.json            # VBA プロジェクト向け MCP 設定
│   ├── settings-hardware.json       # ハードウェア開発（Raspberry Pi / ESP32）向け MCP 設定
│   └── settings-universal.json      # 言語横断の汎用 MCP 設定
│
│  # ===== resources/ =====
│  # 外部参考資料・リンク集
│
├── resources/
│   └── awesome-claude-code.md   # Claude Code の便利ツール・リソース集
│
│  # ===== rules/ =====
│  # Claude が常に従うべきルール定義 (CLAUDE.md から参照される)
│
├── rules/
│   ├── coding-principles.md     # コーディング原則 (汎用)
│   ├── language.md              # 言語・コミュニケーションルール
│   ├── security-rules.md        # セキュリティルール (XSS・SQLi・認証・インシデント対応等)
│   ├── common/                  # 言語共通ルール
│   │   ├── coding-style.md      # コーディングスタイル
│   │   ├── git-workflow.md      # Git ワークフロー
│   │   └── testing.md           # テストルール
│   ├── python/                  # Python 固有ルール
│   │   ├── coding-style.md      # Python コーディングスタイル
│   │   ├── dev-environment.md   # Python 開発環境設定
│   │   └── testing.md           # Python テストルール
│   ├── php/                     # PHP 固有ルール
│   │   └── coding-style.md      # PHP コーディングスタイル（PHP 8.x）
│   ├── laravel/                 # Laravel 固有ルール
│   │   └── conventions.md       # Laravel 命名規則・Eloquent・Controller 規約
│   ├── javascript/              # JavaScript 固有ルール
│   │   └── jquery-style.md      # jQuery コーディングスタイル
│   └── hardware/                # ハードウェア開発ルール
│       ├── embedded-c-style.md  # 組み込み C/C++ スタイル（型・volatile・割り込み）
│       ├── raspberry-pi.md      # Raspberry Pi 開発規約（gpiozero・I2C/SPI・systemd）
│       └── esp32.md             # ESP32 開発規約（PlatformIO・FreeRTOS・ディープスリープ）
│
│  # ===== skills/ =====
│  # /スキル名 で呼び出せる作業手順書 (ワークフロー系・汎用)
│  # 各サブディレクトリが 1 スキルを構成し SKILL.md がエントリポイント
│
└── skills/
    ├── SKILL_TEMPLATE.md            # スキル定義のテンプレート
    ├── accessibility/               # アクセシビリティ対応
    ├── advanced-security/           # 高度なセキュリティ分析
    │   ├── codeql/                  # CodeQL による静的解析
    │   ├── insecure-defaults/       # 安全でないデフォルト設定の検出
    │   └── sarif-parsing/           # SARIF 結果の解析
    │   └── semgrep/                 # Semgrep による静的解析
    ├── agents/                      # エージェント活用パターン
    │   ├── dispatching-parallel-agents/   # 並列エージェント実行
    │   ├── receiving-code-review/         # コードレビューの受け取り方
    │   ├── requesting-code-review/        # コードレビューの依頼方法
    │   ├── subagent-driven-development/   # サブエージェント駆動開発
    │   ├── using-superpowers/             # Claude の高度機能活用
    │   ├── verification-before-completion/ # 完了前の検証
    │   └── writing-skills/                # スキル定義の書き方
    ├── brainstorming/               # ソクラテス式ブレスト → 要件・設計を問いかけで整理
    ├── claude-code-setup/           # Claude Code 環境セットアップ
    ├── claude-md-management/        # CLAUDE.md の管理・改訂
    ├── code-review/                 # コードレビューの進め方
    ├── create-plan/                 # 実装計画の作成
    ├── css-features/                # CSS 機能の活用
    ├── css-layout/                  # CSS レイアウト
    ├── css-modern/                  # モダン CSS
    ├── css-organization/            # CSS の整理・設計
    ├── design-tracker/              # 設計変更の追跡
    ├── executing-plans/             # 計画を実行に移すときの手順
    ├── frontend-design/             # フロントエンド設計
    ├── frontend-ui-ux/              # UI/UX 実装
    ├── git/                         # Git 操作
    │   ├── finishing-a-development-branch/ # 開発ブランチの完了処理
    │   └── git-worktrees/                  # Git Worktree の活用
    ├── handover/                    # セッション引き継ぎドキュメントの手動生成
    ├── hookify/                     # フック設定の自動生成
    ├── init/                        # プロジェクト初期化
    ├── mcp-builder/                 # MCP サーバーの構築
    ├── planning-with-files/         # ファイルに計画を書きながら進める実装フロー
    ├── plugin-dev/                  # プラグイン開発
    │   ├── agent-development/       # エージェント開発
    │   ├── command-development/     # コマンド開発
    │   ├── hook-development/        # フック開発
    │   ├── mcp-integration/         # MCP 統合
    │   ├── plugin-settings/         # プラグイン設定管理
    │   ├── plugin-structure/        # プラグイン構造設計
    │   └── skill-development/       # スキル開発
    ├── research-lib/                # ライブラリ調査
    ├── security/                    # セキュリティ
    │   ├── owasp-security/          # OWASP セキュリティチェック
    │   └── varlock/                 # 変数・シークレット保護
    ├── simplify/                    # コード簡素化
    ├── skill-creator/               # スキル定義の作成・評価
    ├── systematic-debugging/        # 体系的なデバッグ手順
    ├── tdd-workflow/                # TDD (テスト駆動開発) のサイクル
    ├── test-driven-development/     # テスト駆動開発
    ├── update-design/               # 設計ドキュメントの更新
    ├── update-lib-docs/             # ライブラリドキュメントの更新
    ├── vba-core/                    # VBA コア機能
    ├── vba-development/             # VBA 開発全般
    ├── vba-excel/                   # Excel VBA
    ├── vba-patterns/                # VBA パターン集
    ├── wolfram-foundation-tool/     # Wolfram 基盤ツール
    ├── writing-plans/               # 実装計画ドキュメントの書き方
    ├── writing-skills/ → agents/writing-skills/ 参照
    ├── raspberry-pi/                # Raspberry Pi 開発ガイド（GPIO・センサー・カメラ・systemd）
    └── esp32/                       # ESP32 開発ガイド（PlatformIO・WiFi・FreeRTOS・OTA）
```

---

## 分類早見表

| フォルダ / ファイル | 役割 |
|---|---|
| `CLAUDE.md`        | Claude Code に読み込ませるメイン指示ファイル |
| `agents/`          | 専門作業を担う名前付きエージェント |
| `commands/`        | スラッシュコマンドのショートカット定義 |
| `contexts/`        | 作業モード別のコンテキスト切り替え設定 |
| `docs/`            | 設計ドキュメント |
| `hooks/`           | Pre/Post ToolUse 等で自動実行されるスクリプト |
| `hooks/lib/`       | フック共通ライブラリ（transcript 解析・claude -p 呼び出し） |
| `mcp/`             | 外部ツール連携 (DB・ブラウザ・ファイル等) の設定テンプレ |
| `meta/`            | _shared 自体の品質管理・自動生成スクリプト |
| `registry/`        | スキルルーティングインデックス（generate-registry.py が生成） |
| `resources/`       | 外部参考資料・便利ツール集 |
| `rules/`           | 常時適用されるルール (セキュリティ・コーディング規約等) |
| `skills/`          | 作業手順のレシピ集 (呼び出して使う) |
| `*.md` (ルート直下) | 人間向けのドキュメント・参考資料 |
| `claude_settings.json` / `.claudeignore` | Claude Code の動作そのものを制御 |
| `custom_instructions.md` | Claude の思考・振る舞いの方針を指示 |
