# .claude/ フォルダ構成ガイド

## 全体マップ

```
.claude/
├── settings.json       # Claude Code 動作設定
├── rules/              # 常時適用ルール（全セッション自動読み込み）
├── skills/             # /コマンドで呼び出せるワークフロー
├── hooks/              # ツール実行時に自動発火するスクリプト
├── docs/               # 参照ドキュメント
├── agents/             # サブエージェント設定
├── logs/               # ログ
└── archive/            # 不要になったファイルの保管場所
```

---

## `settings.json`

Claude Code の動作設定（ツール許可・フック登録など）。

---

## `rules/` — 常時適用されるルール

セッションを問わず **すべての会話に自動で読み込まれる** 指示書。

| ファイル | 内容 |
|---------|------|
| `language.md` | 思考は英語・ユーザー返答は日本語・コードは英語 |
| `security.md` | 秘匿情報・SQLインジェクション・XSS防止などのセキュリティ指針 |
| `coding-principles.md` | 早期リターン・単一責任・型ヒントなどのコーディング規約 |
| `codex-delegation.md` | Codex CLI をいつ・どう呼ぶかのルール |
| `gemini-delegation.md` | Gemini CLI をいつ・どう呼ぶかのルール |

---

## `skills/` — `/コマンド` で呼び出せるワークフロー

各フォルダ = 1スキル。`SKILL.md` がスキルの手順書。

| スキル | 役割 |
|--------|------|
| `create-plan` | proposal.md → plan.md 作成 → Codex レビューループ |
| `startproject` | Gemini調査 → 要件整理 → Codexレビュー → タスク作成 |
| `plan` | 機能の実装計画を作成 |
| `codex-system` | Codex CLI の呼び出し方・パターン集 |
| `gemini-system` | Gemini CLI の呼び出し方・パターン集 |
| `design-tracker` | 設計決定を自動で `DESIGN.md` に記録 |
| `update-design` | 手動で `DESIGN.md` を更新 |
| `update-lib-docs` | ライブラリドキュメントを最新情報に更新 |
| `checkpointing` | セッションのチェックポイント保存 |
| `init` | プロジェクト初期設定（AGENTS.md 更新） |

---

## `hooks/` — ツール実行時に自動発火するスクリプト

Claude がツールを呼ぶ **前後** に自動実行される Python スクリプト。

| ファイル | タイミング・役割 |
|---------|----------------|
| `agent-router.py` | ユーザー入力時：キーワードで Gemini/Codex 呼び出しを提案 |
| `check-codex-after-plan.py` | 計画作成後：Codex レビューを提案 |
| `check-codex-before-write.py` | ファイル書き込み前：Codex 確認を提案 |
| `lint-on-save.py` | ファイル保存時：Lint 自動実行 |
| `log-cli-tools.py` | CLI ツール使用時：ログ記録 |
| `post-implementation-review.py` | 実装後：レビュー提案 |
| `post-test-analysis.py` | テスト後：失敗分析 |
| `suggest-gemini-research.py` | 特定キーワード検出時：Gemini リサーチを提案 |

---

## `docs/` — 参照ドキュメント

| パス | 内容 |
|-----|------|
| `DESIGN.md` | プロジェクトの設計決定の記録 |
| `libraries/_TEMPLATE.md` | ライブラリドキュメントのテンプレート |
| `libraries/{name}.md` | 各ライブラリの制約・使い方・注意点 |
| `research/{topic}.md` | Gemini/Codex によるリサーチ結果 |

---

## `agents/` — サブエージェントの設定

| ファイル | 内容 |
|---------|------|
| `general-purpose.md` | 汎用サブエージェントへの指示 |

---

## `logs/` — ログ

| ファイル | 内容 |
|---------|------|
| `cli-tools.jsonl` | CLI ツール（Codex/Gemini）の使用履歴 |

---

## `archive/` — 不要になったファイルの保管場所

削除はせず、ここに移動して保管する。
現在は Python 専用スキル・ルールと過去タスク固有のリサーチが格納されている。
