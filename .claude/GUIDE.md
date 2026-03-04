# .claude/ 詳細ガイド

各コンポーネントの「何か」「いつ使うか」「どんな効果があるか」を解説する。
ディレクトリ構造の一覧は [STRUCTURE.md](STRUCTURE.md) を参照。

---

## 1. agents/ — 専門エージェント（22ファイル）

### 何か
`Task` ツールで呼び出す**専門エージェントの役割定義**。
各エージェントは独自のコンテキストウィンドウで作業し、結果だけをメインに返す。

### 効果
- **コンテキスト節約**: 調査結果だけが返るため、メインウィンドウを圧迫しない
- **専門性**: 各エージェントが特化した指示を持つため、汎用指示より高品質
- **並列処理**: 複数エージェントを同時起動して調査を高速化できる

### カテゴリと使い分け
| カテゴリ            | エージェント             | いつ使うか |
| **planning/**      | `planner`               | 新機能の実装計画（要件分析→ステップ分解→リスク評価）
|                    | `architect`             | 設計判断・アーキテクチャ検討・コードパターン分析
| **review/**        | `code-reviewer`         | PRマージ前のコードレビュー（CRITICAL/HIGH/MEDIUM/LOW判定）
|                    | `security-reviewer`     | OWASPベースのセキュリティ監査
|                    | `python-reviewer`       | Python固有の品質チェック
|                    | `database-reviewer`     | DB設計・クエリのレビュー
|                    | `code-simplifier`       | コードの簡素化・可読性向上
|                    | `type-design-analyzer`  | 型設計の品質分析
|                    | `silent-failure-hunter` | try-catchの握り潰し等のサイレント障害検出
| **testing/**       | `tester`                | テスト戦略設計・テストコード記述
|                    | `tdd-guide`             | TDDサイクル（Red→Green→Refactor）のガイド
|                    | `e2e-runner`            | E2Eテストの設計・実行
|                    | `pr-test-analyzer`      | PRのテストカバレッジ分析
| **debugging/**     | `debugger`              | 科学的デバッグ（症状収集→仮説→検証→修正）
|                    | `performance`           | パフォーマンスボトルネックの特定・改善
|                    | `build-error-resolver`  | ビルドエラーの体系的解消
| **refactoring/**   | `refactorer`            | リファクタリング計画・実行・デッドコード除去
| **documentation/** | `documenter`            | ドキュメント生成・コードマップ・README同期
| **exploration/**   | `code-explorer`         | コードベースの調査・理解
| **tooling/**       | `agent-creator`         | 新しいエージェント定義の作成
|                    | `plugin-validator`      | プラグイン構造の検証
|                    | `skill-reviewer`        | スキル定義の品質レビュー
---

## 2. skills/ — 作業手順レシピ（38ディレクトリ）

### 何か
`/スキル名` やトリガーフレーズで呼び出せる**作業手順書**。
**二段階ロード設計**でコンテキストを節約する:


### 主要スキルの使い分け

#### 計画・設計系
| スキル             | トリガー            | いつ使うか                            | 効果 
| `brainstorming`   | ブレスト、要件整理   | 要件が曖昧な時、設計の方向性を決めたい時 | 4フェーズの要件整理を実行 
| `create-plan`     | 計画作成            | proposal.md → plan.md を作りたい時     | Codexレビューループで承認されるまで自動改善 
| `writing-plans`   | 実装計画、タスク分割 | 大きなタスクを分解したい時              | 2-5分単位の具体的ステップに分割 
| `implement-plans` | 計画実行            | 書かれた計画を別セッションで実行する時   | レビューチェックポイント付きで実行 
| `design-tracker`  | 設計記録            | アーキテクチャの決定があった時          | DESIGN.md に自動記録（+手動更新モード） 

#### 開発・デバッグ系
| スキル                  | トリガー             | いつ使うか                  | 効果 |
| `frontend-design`      | フロントエンド設計    | UIを構築する時               | プロダクショングレードのUI + UI/UX設計原則 
| `tdd-workflow`         | TDD、テストファースト | テスト駆動で機能を実装したい時 | Red→Green→Refactorのサイクルを厳密に実行 
| `systematic-debugging` | デバッグ、バグ        | 原因不明のバグに遭遇した時    | 証拠ベースの4段階デバッグ（症状→仮説→検証→修正）
| `code-review`          | コードレビュー        | コード品質を確認したい時      | 多角的レビュー（品質・セキュリティ・パフォーマンス）
| `simplify`             | シンプル化           | 複雑なコードを整理したい時     | 機能を保ったまま可読性を向上 

#### CSS系
| スキル             | トリガー       | いつ使うか                             | 効果 
| `css-features`     | モダンCSS     | ネスト、コンテナクエリ、:has() 等を使う時 | 2024+のモダンCSS機能のリファレンス 
| `css-layout`       | CSSレイアウト | Grid・Flexbox・レスポンシブデザイン      | レイアウトパターン集 
| `css-organization` | CSS設計、BEM  | CSS設計を整えたい時                     | ファイル構成・命名規則・変数・アニメーション 

#### ハードウェア系
| スキル          | トリガー                | いつ使うか             | 効果 
| `esp32`        | 「ESP32」「PlatformIO」 | ESP32ファームウェア開発 | WiFi/BLE・FreeRTOS・ディープスリープ・OTA
| `raspberry-pi` | 「ラズパイ」「GPIO」     | Raspberry Pi開発       | GPIO・I2C/SPI・カメラ・systemd常駐化 

#### VBA系
| スキル          | トリガー   | いつ使うか                             | 効果
| `vba-core`     | VBA基礎    | VBAプロジェクト開始・コーディング標準策定 | エラーハンドリング・変数宣言・メモリ管理 
| `vba-excel`    | VBA        | Excelワークシート操作・UserForm作成     | イベント処理・セキュリティパターン 
| `vba-patterns` | VBAパターン | 最終行取得・ループ・ファイル操作         | 共通ユーティリティパターン集 

#### セッション管理系
| スキル                | トリガー                | いつ使うか                     | 効果
| `handover`            | 引き継ぎ、セッション終了 | 次のセッションに作業を引き継ぐ時 | HANDOVER.md を docs/memory/ に生成
| `planning-with-files` | 長期タスク              | セッションをまたぐ大きなタスク   | 3つのMDファイルで文脈を永続化

#### ツール・設定系
| スキル                    | トリガー          | いつ使うか                            | 効果
| `hookify`                 | hookify          | フック設定を作りたい時                 | 対話的にフック設定を自動生成 
| `claude-code-setup`       | Claude Code設定  | オートメーションを最適化したい時        | フック・スキル・MCPの推薦 
| `claude-md-management`    | CLAUDE.md改善    | CLAUDE.mdを監査・改善したい時          | 品質ルーブリックで評価・ターゲット改善
| `init`                    | プロジェクト初期化 | 新プロジェクトの.claude/をセットアップ | 初期設定の生成
| `skill-creator`           | スキル作成        | 新しいスキルを作りたい時               | スキル定義の作成・テスト・改善
| `mcp-builder`             | MCPサーバー作成   | 外部API連携用のMCPサーバーを構築       | Python/Node両対応のMCPサーバーガイド
| `research-lib`            | ライブラリ調査    | ライブラリの調査ドキュメントを作成      | docs/libraries/に標準化されたドキュメントを生成 
| `wolfram-foundation-tool` | Wolfram          | 正確な計算・科学的事実が必要な時        | Wolfram Alphaによる検証済み計算

#### セキュリティ系

| スキル                     | トリガー        | いつ使うか                  | 効果 
| `security/owasp-security` | OWASP           | Webアプリのセキュリティ監査  | OWASP Top 10ベースのチェック
| `security/varlock`        | varlock         | 環境変数・シークレットの保護 | 変数ロック・漏洩防止
| `advanced-security/*`     | CodeQL, semgrep | 高度な静的解析              | CodeQL/Semgrep/SARIFを使った脆弱性検出

## 3. commands/ — スラッシュコマンド（26ファイル）
### 何か
`/コマンド名` で即座に実行できる**カスタムスラッシュコマンド**。

### 主要コマンドの使い分け
#### Git 操作
| コマンド | いつ使うか | 効果 |
| `/commit` | 変更をコミットしたい時 | git status/diff を確認して適切なメッセージでコミット |
| `/commit-push-pr` | コミット→プッシュ→PR作成を一括実行 | 3ステップをワンコマンドで完了 |
| `/clean-gone` | リモートで削除されたブランチのローカル掃除 | [gone] ブランチを一括削除 |

#### コード品質
| コマンド           | いつ使うか             | 効果 |
| `/verify`         | デプロイ前の最終チェック | ビルド→型チェック→Lint→テスト→console文監査 を一括実行 |
| `/code-review`    | コードの品質確認        | code-reviewerエージェントに委譲 |
| `/review-pr`      | PRの包括的レビュー      | 複数専門エージェントが並列レビュー |
| `/test-coverage`  | テストカバレッジの確認   | 80%+ を目指したカバレッジ分析 |
| `/refactor-clean` | リファクタリング        | refactorerエージェントに委譲 |
| `/build-fix`      | ビルドエラーの修正      | ビルドシステム自動検出→エラー分類→修正 |

#### 開発フロー
| コマンド        | いつ使うか                        | 効果 |
| `/feature-dev` | 新機能の開発を開始する時            | 7フェーズの開発フロー（Discovery→実装→レビュー）
| `/orchestrate` | 複数エージェントを順番に実行したい時 | エージェントパイプライン構築（例: planner→tdd-guide→reviewer）
| `/e2e`         | E2Eテストを実行したい時             | e2e-runnerエージェントに委譲 

#### ドキュメント・設定
| コマンド             | いつ使うか                 | 効果 |
| `/update-docs`      | ドキュメントを最新化したい時 | ソースからドキュメントを同期 |
| `/revise-claude-md` | CLAUDE.mdを改善したい時     | セッション中の学びを反映 |
| `/checkpoint`       | 作業の途中経過を記録したい時 | チェックポイントのスナップショット |

#### hookify 関連
| コマンド              | いつ使うか                     | 効果 |
| `/hookify`           | フック設定を生成したい時         | 会話分析または指示からフック設定を自動生成 |
| `/hookify-list`      | 登録済みフック一覧を見たい時     | 全hookifyルールの表示 |
| `/hookify-configure` | フックの有効/無効を切り替えたい時 | 対話的なフック設定変更 |

#### 学習・改善系
| コマンド          | いつ使うか                         | 効果 |
| `/learn-edits`   | 編集パターンを分析したい時           | 編集ログからパターン抽出→hook/skill候補提案 |
| `/materialize`   | 提案されたskill/hook候補をドラフト化 | staging/ にファイル生成 |
| `/review-staged` | staging/ のドラフトを確認・承認      | 候補の承認または却下 |

### コマンドの特殊機能
- `!`` `` `` ` 構文: コマンド定義内でシェルコマンドを埋め込み可能（実行時に結果が注入される）
- 例: `Current branch: !`git branch --show-current``
- `allowed-tools`: コマンドが使えるツールを制限できる（安全性向上）
- `argument-hint`: コマンドの引数のヒントを定義可能

## 4. contexts/ — 作業モード切り替え（3ファイル）
### 何か
Claudeの振る舞いを作業内容に応じて最適化する**モード設定**。
| モード         | いつ使うか             | Claudeの振る舞い                                    
| `dev.md`      | 新機能実装・バグ修正     | コードを先に書く。テスト実行。atomicコミット。**速度優先**
| `research.md` | 技術調査・ライブラリ選定 | コードを書く前に理解する。仮説→検証。**理解優先**     
| `review.md`   | コードレビュー・品質確認 | 深刻度順に問題指摘+修正案。チェックリスト実行。**品質優先**

### 効果
同じ「このコードを見て」という依頼でも:
- `dev` → 改善コードを即座に書く
- `research` → 構造を分析して説明する
- `review` → 問題点を深刻度順にリストアップする

## 5. hooks/ — 自動実行スクリプト
### 何か
特定のイベントで**自動的に実行されるPythonスクリプト**。
`settings.json` の `hooks` セクションで登録する。

### 登録フック一覧
| フック                           | トリガー                     | 効果 |
| `pre-compact-handover.py`       | 自動コンパクション直前         | HANDOVER + SKILL-SUGGESTIONS + EDIT-PATTERNS を自動生成。セッション切れても文脈を失わない
| `lint-on-save.py`               | .pyファイルのEdit/Write後     | ruff format→ruff check --fix→ty check を自動実行。保存するだけでコード品質が保たれる |
| `post-test-analysis.py`         | pytest/npm test等のBash実行後 | エラー3件以上で「Codexに相談を推奨」を表示。メインコンテキスト節約を促す |
| `post-implementation-review.py` | コードファイルのEdit/Write後   | 3ファイル以上または100行以上の変更でレビューを促す |
| `edit-tracker.py`               | Edit/Write後                  | 編集ログを蓄積しlearn-editsで分析に使う |

### 補助ファイル
| ファイル | 役割 |
| `edit-approval.py` | ファイル編集時の承認制御 |
| `approval_skip_patterns.txt` | 承認不要なパターンの定義 |
| `notify-slack.py` / `slack_approval.py` / `slack_socket_daemon.py` | Slack連携（通知・承認） |
| `stop-notify.py` | 停止通知 |
| `lib/transcript.py` | JSONLトランスクリプト読み込みユーティリティ |
| `lib/claude_p.py` | claude -p 呼び出しユーティリティ |

### 効果

- **ゼロコストの品質維持**: ファイル保存のたびにlintが自動実行
- **コンテキスト自動保存**: 会話圧縮前に引き継ぎ情報が自動生成
- **自己改善**: 編集パターンからskill/hook候補が自動提案される

---

## 6. rules/ — 常時適用ルール（16ファイル）

### 何か

Claudeが**常に従うべきコーディングルール**。
`.claude/rules/` に置くだけで Claude Code が自動検出しセッションに注入する。

### ルール構成と適用タイミング

| ルール | いつ適用されるか | 主な効果 |

| `coding-principles.md` | 常時 | シンプル第一・単一責任・早期リターン・型ヒント必須 |
| `security-rules.md` | 常時 | シークレット禁止・SQL注入防止・XSS防止（10項目） |
| `language.md` | 常時 | コードは英語、返答は日本語 |
| `common/coding-style.md` | 常時 | 不変性・ファイルサイズ上限・エラー処理 |
| `common/git-workflow.md` | 常時 | コミットメッセージ形式・PR手順・ブランチ命名 |
| `common/testing.md` | 常時 | カバレッジ80%以上・TDDサイクル |
| `python/*.md` (3ファイル) | 常時 | PEP 8・uv使用・pytest・ruff |
| `php/coding-style.md` | 常時 | PHP 8.x・PSR-12・match式 |
| `laravel/conventions.md` | 常時 | 命名規則・Eloquent・FormRequest |
| `javascript/jquery-style.md` | 常時 | セレクタキャッシュ・イベント委譲・CSRF |
| `hardware/*.md` (3ファイル) | 常時 | 組み込みC・Raspberry Pi・ESP32 |

### `paths:` フロントマターによる条件付きロード

```yaml
---
paths:
  - "src/api/**/*.ts"
---
```

この記法で「特定ファイルを開いた時だけ」ルールを注入できる（コンテキスト節約）。

---

## 7. docs/ — 設計ドキュメント・メモリ

### 何か

プロジェクトの**設計情報と会話メモリの保存先**。

| ファイル/フォルダ | いつ使われるか | 効果 |

| `DESIGN.md` | `design-tracker` スキルが設計決定を自動記録 | 設計の経緯（なぜ・いつ・代替案は何だったか）が蓄積される |
| `memory/HANDOVER-*.md` | PreCompactフックで自動生成 | セッション切れても作業文脈を引き継げる |
| `memory/SKILL-SUGGESTIONS-*.md` | PreCompactフックで自動生成 | 会話パターンからスキル/フック候補が提案される |
| `memory/AUTO-MATERIALIZE-QUEUE.jsonl` | EDIT-PATTERNS生成時 | `/materialize` で候補をドラフト化するためのキュー |
| `libraries/` | `research-lib` スキルで生成 | ライブラリ調査結果の標準化されたドキュメント |

---

## 8. meta/ — 品質管理スクリプト

### 何か

`.claude/` 自体を管理する**品質チェック・自動生成スクリプト**。

| スクリプト | いつ使うか | 効果 |

| `generate-registry.py` | スキルを追加・変更した後 | `registry/skills.yaml` を再生成。Claudeが全SKILL.mdを読まずにルーティング可能に |
| `health-check.py` | 定期的な品質チェック | evals.json欠損・SKILL.md肥大化・registry未登録・重複候補を検出 |

```bash
python .claude/meta/generate-registry.py       # registry再生成
python .claude/meta/health-check.py             # 品質レポート（コンソール）
python .claude/meta/health-check.py --save      # 品質レポート（ファイル保存）
```

---

## 9. mcp/ — MCPサーバー設定テンプレート

### 何か

**MCP（Model Context Protocol）** サーバーの設定テンプレート集。
MCPはSkillsと異なり、**外部プロセスとして実行**されリアルタイムでデータを取得・操作できる。

| 比較 | Skills | MCP |

| 実行場所 | Claude内で解釈 | 外部サーバープロセス |
| データアクセス | なし（知識のみ） | リアルタイム取得可能 |
| API/DB連携 | 不可 | 可能 |

### テンプレート一覧

| ファイル | いつ使うか |
|---|---|
| `mcp-guide.md` | MCPの概要・導入方法を知りたい時 |
| `settings-python.json` | Pythonプロジェクトに最適なMCPを設定する時 |
| `settings-javascript.json` | JS/TSプロジェクト向け |
| `settings-laravel-php.json` | Laravel/PHP向け |
| `settings-hardware.json` | ハードウェア開発向け |
| `settings-universal.json` | 言語横断の汎用設定 |
| `context7-setup.md` | Context7（ライブラリドキュメント取得MCP）の導入 |

### 注意

MCPサーバーはツール定義がコンテキストを消費する。プロジェクトあたり10個以下、ツール数80個以下を推奨。

---

## 10. その他のファイル

| ファイル | いつ使うか | 効果 |

| `CLAUDE.md` | 常時（自動ロード） | ワークフロー設計・タスク管理・コア原則の定義 |
| `settings.json` | 常時（自動ロード） | フック登録・パーミッション設定（deny で機密ファイル保護） |
| `.claudeignore` | 常時（自動ロード） | Claudeに読ませないファイルパターン（node_modules等） |
| `context-management.md` | コンテキスト圧迫時に参照 | 20万トークンの効率的な使い方ガイド |
| `agent_usage_guide.md` | エージェント使い分けに迷った時 | Task ツールの各タイプの使い分け解説 |
| `prompt_templates.md` | プロンプト作成時に参照 | よく使うプロンプトのテンプレート集 |
| `quick_start.md` | 初めて使う時に参照 | Claude Codeの使い始めガイド |
| `registry/skills.yaml` | Claudeが自動参照 | 全スキルのルーティングインデックス（手動編集不要） |
| `resources/awesome-claude-code.md` | ツール・リソース探しに参照 | Claude Codeの便利ツール・リソース集 |

---

## 逆引き早見表（実用度順）

`.claude/` の中身を知らなくても、以下の「やりたいこと」から逆引きできます。
上にあるものほど**日常の開発で使う頻度が高い**ものです。

### 毎日使うもの（コーディングの基本動作）
やり方 | 何が起きるか |
| コードを書いたらコミットしたい | `/commit` と入力 | git diff を見てコミットメッセージを自動生成。手動でメッセージを考える手間がなくなる |
| コミット→プッシュ→PR作成を一発でやりたい | `/commit-push-pr` と入力 | 3つの手順がワンコマンドで完了。PR本文も自動生成される |
| 書いたコードが正しいか確認したい | `/verify` と入力 | ビルド→型チェック→Lint→テストを一括実行。デプロイ前にこれだけ叩けば安心 |


### 機能開発（新しいものを作るとき）
やり方 | 何が起きるか |
| 要件がぼんやりしていて整理したい | 「ブレスト」と言う | ソクラテス式の質問で要件が具体化される。proposal.md に書く前にやると効果的 |
| やることリストを計画書にしたい | proposal.md に要件を書いて `/create-plan` | 計画書（plan.md）を自動作成。Codex がレビューして品質を担保する |
| 計画書に沿って実装を進めたい | `/implement-plans` と入力 | plan.md の各ステップを順番に実装。途中で止まったら報告してくれる |
| 新機能をゼロから開発したい | `/feature-dev` と入力 | 調査→設計→実装→レビューの7段階を順にガイドしてくれる |


### バグ修正・トラブル対応
やり方 | 何が起きるか |
| バグの原因がわからない | 「このバグを調査して」と伝える | 自動的にログ・コード・動作を調査して修正まで行う |
| 何度修正しても直らないバグがある | `/systematic-debugging` と入力 | 症状収集→仮説→検証→修正の4段階で科学的にデバッグ。当てずっぽうな修正を防ぐ |
| ビルドエラーが出て進めない | `/build-fix` と入力 | エラーを分類して、影響の少ない順に1つずつ解消してくれる |

> **ポイント**: 「改善されていない（N回目）」の状態になったら `/systematic-debugging` を使ってください。

### コードレビュー・品質改善

やり方 | 何が起きるか |

| 自分のコードをレビューしたい | `/code-review` と入力 | CRITICAL→HIGH→MEDIUM→LOW の順で問題点を指摘。修正案も提示される |
| PRをレビューしたい | `/review-pr` と入力 | セキュリティ・パフォーマンス・品質を複数の専門エージェントが並列チェック |
| テストが足りているか確認したい | `/test-coverage` と入力 | カバレッジを分析して、足りないテストを生成してくれる |
| 複雑なコードをシンプルにしたい | `/refactor-clean` と入力 | デッドコードの除去・冗長な実装の簡素化を安全に実行 |

---

### セッション管理（長い作業・翌日への引き継ぎ）

やり方 | 何が起きるか |

| 今日の作業を明日に引き継ぎたい | `/handover` と入力 | HANDOVER.md が生成される。次のセッションで読めば即座に作業再開できる |
| 会話が長くなって重くなった | `/clear` と入力 | 会話をリセット。ただし HANDOVER は自動保存されるので文脈は失われない |
| 大きなタスクを複数日に分けたい | `planning-with-files` スキルを使う | 3つのファイル（計画/調査/進捗）でセッションをまたいで文脈を保持 |

> **ポイント**: 会話が重くなる前に `/handover` → `/clear` するのがコツ。自動コンパクション時にも HANDOVER は自動生成されます。

---

### 自動化の設定（一度やれば毎回効く）

やり方 | 何が起きるか |

| コードを保存するたびに自動Lintしたい | 設定済み（`hooks/lint-on-save.py`） | .py ファイルの Edit/Write 後に ruff が自動実行。何もしなくてOK |
| 編集パターンから改善点を見つけたい | `/learn-edits` と入力 | 編集ログを分析して「毎回同じ修正をしている」等のパターンを検出 |
| 検出されたパターンをスキル化したい | `/materialize` → `/review-staged` | 候補をドラフト生成→確認→承認の流れでスキルやフックを追加 |
| 新しいフックを作りたい | `/hookify` と入力 | 対話的にフック設定を生成。Python スクリプトの雛形も作ってくれる |

> **ポイント**: `/learn-edits` → `/materialize` → `/review-staged` のサイクルを回すと、Claude が自分自身を改善していきます。

---

### 設定・メンテナンス（たまにやること）

やり方 | 何が起きるか |

| 新しいスキルを作りたい | `/skill-creator` と入力 | SKILL.md + INSTRUCTIONS.md + evals.json をガイド付きで作成 |
| スキルを追加・変更した後 | `python .claude/meta/generate-registry.py` | レジストリを更新。これをやらないと新スキルがルーティングされない |
| `.claude/` 全体の健康状態を確認 | `python .claude/meta/health-check.py` | evals.json 欠損・SKILL.md 肥大化・未登録スキル等を検出 |
| CLAUDE.md のルールを改善したい | `/revise-claude-md` と入力 | このセッションでの学びを CLAUDE.md に反映 |
| 外部API/DBとリアルタイム連携したい | `mcp/` のテンプレートを参照 | MCP サーバーを設定すると、Claude が直接 API やDBにアクセスできる |
