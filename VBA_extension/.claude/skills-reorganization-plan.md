# Skills整理計画

## 現状分析

### 現在のディレクトリ構成
```
.claude/
├── skills/              # 28ファイル (カスタムスキル)
├── skills-anthropics/   # Anthropic公式スキル
├── skills-new/          # ほぼ空 (README.mdのみ)
└── skills-superpowers/  # 別のスキルコレクション
```

### プロジェクトの技術スタック
- **PHP**: Laravel 12
- **JavaScript**: Vanilla JS (React未使用)
- **Python**: gcp_OCR, offline_OCR

---

## 追加予定のリポジトリ

### 1. awesome-claude-skills (5.5k★)
https://github.com/BehiSecc/awesome-claude-skills

**関連するスキル:**
- 📄 ドキュメント: docx, pdf, pptx, xlsx
- 🛡 セキュリティ: owasp-security, systematic-debugging, webapp-testing
- 🔧 開発: test-driven-development, using-git-worktrees
- 📊 データ: csv-data-summarizer, postgres
- 🔬 研究: deep-research

### 2. claude-code-best-practice (1.9k★)
https://github.com/shanraisshan/claude-code-best-practice

**関連するコンテンツ:**
- RPI (Research-Plan-Implement) ワークフロー
- Skills/Subagents/Hooks 設定ガイド
- MCP サーバー設定例
- 実装パターン例

---

## 重複スキル一覧

| スキル名 | skills/ | skills-superpowers/ | 推奨 |
|---------|---------|---------------------|------|
| brainstorming | 244行 | 54行 | skills/ |
| executing-plans | 287行 | 76行 | skills/ |
| writing-plans | 243行 | 116行 | skills/ |
| systematic-debugging | 228行 | 296行 | skills-superpowers/ |
| git-worktrees | 261行 | 217行 (using-git-worktrees) | skills/ |
| tdd-workflow | 409行 | 371行 (test-driven-development) | skills/ |

---

## 提案する新構成

```
.claude/
├── skills/                        # アクティブなスキル
│   ├── workflow/                  # ワークフロー系
│   │   ├── brainstorming.md
│   │   ├── writing-plans.md
│   │   ├── executing-plans.md
│   │   ├── planning-with-files.md
│   │   ├── code-review.md
│   │   ├── tdd-workflow.md
│   │   ├── systematic-debugging.md (superpowersから移動)
│   │   └── rpi-workflow/          [NEW: best-practice]
│   │
│   ├── git/                       # Git関連
│   │   ├── git-worktrees.md
│   │   └── finishing-a-development-branch/ (superpowersから)
│   │
│   ├── frontend/                  # フロントエンド (CSS, アクセシビリティ)
│   │   ├── css-features.md
│   │   ├── css-layout.md
│   │   ├── css-modern.md
│   │   ├── css-organization.md
│   │   ├── frontend-ui-ux.md
│   │   └── accessibility.md
│   │
│   ├── security/                  # セキュリティ [NEW]
│   │   ├── owasp-security/        [NEW: awesome-claude-skills]
│   │   └── webapp-testing/        [NEW: awesome-claude-skills]
│   │
│   ├── documents/                 # ドキュメント生成 [NEW]
│   │   ├── docx/                  (anthropicsにもあるが追加)
│   │   ├── pdf/                   [NEW: awesome-claude-skills]
│   │   ├── pptx/                  (anthropicsにもあるが追加)
│   │   └── xlsx/                  (anthropicsにもあるが追加)
│   │
│   ├── research/                  # 調査・分析 [NEW]
│   │   ├── deep-research/         [NEW: awesome-claude-skills]
│   │   └── csv-data-summarizer/   [NEW: awesome-claude-skills]
│   │
│   ├── ai-tools/                  # AI CLI ツール
│   │   ├── ai-cli-selector.md
│   │   ├── codex-cli.md
│   │   └── gemini-cli.md
│   │
│   ├── agents/                    # エージェント系 (superpowersから)
│   │   ├── dispatching-parallel-agents/
│   │   ├── subagent-driven-development/
│   │   ├── receiving-code-review/
│   │   ├── requesting-code-review/
│   │   ├── using-superpowers/
│   │   ├── verification-before-completion/
│   │   └── writing-skills/
│   │
│   └── _templates/                # テンプレート
│       └── SKILL_TEMPLATE.md
│
├── skills-anthropics/             # そのまま維持 (公式スキル)
│
├── skills-best-practice/          # [NEW] claude-code-best-practice
│   ├── workflow/                  # RPIワークフロー等
│   ├── examples/                  # 実装パターン例
│   └── guides/                    # 設定ガイド
│
└── skills-unused/                 # 未使用スキル (アーカイブ)
    ├── react/                     # React未使用のため
    │   ├── react-components.md
    │   ├── react-hooks.md
    │   ├── react-patterns.md
    │   ├── react-performance.md
    │   ├── react-state.md
    │   └── relay/
    │
    ├── vba/                       # VBA未使用のため
    │   ├── vba-core.md
    │   ├── vba-development.md
    │   ├── vba-excel.md
    │   └── vba-patterns.md
    │
    └── misc/                      # その他未使用
        └── _opencode-glm.md
```

---

## 削除対象

| ディレクトリ/ファイル | 理由 |
|----------------------|------|
| `skills-new/` | 空のディレクトリ (README.mdのみ) |
| `skills-superpowers/` | 必要なものをskillsに統合後削除 |
| 重複スキル (superpowers側) | skills/側の方が充実 |

---

## 実行手順

### Phase 1: 新リポジトリのクローン
1. `awesome-claude-skills` をクローン (一時ディレクトリ)
2. `claude-code-best-practice` をクローン (一時ディレクトリ)

### Phase 2: 既存スキルの整理
3. `skills-unused/` ディレクトリを作成
4. 未使用スキル (React, VBA等) を `skills-unused/` へ移動
5. `skills/` にカテゴリ別サブディレクトリを作成
6. 既存スキルをカテゴリ別に移動

### Phase 3: 外部スキルの統合
7. `skills-superpowers/` から有用なスキルを `skills/agents/` へ統合
8. `awesome-claude-skills` から必要なスキルをコピー
   - security/, documents/, research/ 等
9. `skills-best-practice/` を作成し `claude-code-best-practice` からコピー

### Phase 4: クリーンアップ
10. 重複スキルを削除 (内容が薄い方)
11. `skills-new/` を削除
12. 空になった `skills-superpowers/` を削除
13. 一時クローンディレクトリを削除

---

## 注意事項

- `skills-anthropics/` は公式スキルなので変更しない
- 移動後、必要に応じてパスの参照を更新する必要があるかも
- 外部リポジトリからコピーする際はライセンスを確認
- 不要なファイル (.git, README.md等) は除外してコピー

---

## 実行結果 (2026-02-09)

### 最終構成
```
.claude/
├── skills/                        # アクティブなスキル
│   ├── workflow/                  # ワークフロー (7ファイル)
│   ├── git/                       # Git関連 (2項目)
│   ├── frontend/                  # フロントエンド (6ファイル)
│   ├── security/                  # セキュリティ [NEW]
│   │   ├── owasp-security/        # OWASP Top 10
│   │   ├── varlock/               # 環境変数保護
│   │   ├── static-analysis/       # 静的解析
│   │   └── insecure-defaults/     # 安全でないデフォルト検出
│   ├── ai-tools/                  # AI CLIツール (3ファイル)
│   ├── agents/                    # エージェント系 (7項目)
│   └── _templates/                # テンプレート
│
├── skills-anthropics/             # 公式スキル (変更なし)
├── skills-best-practice/          # [NEW] ベストプラクティス
│   ├── skills/                    # 例: weather-fetcher
│   ├── workflow/                  # RPIワークフロー
│   └── hooks/                     # Hooks設定例
│
└── skills-unused/                 # 未使用スキル (12ファイル)
    ├── react/                     # React関連
    ├── vba/                       # VBA関連
    └── misc/                      # その他
```

### 削除済み
- `skills-new/` (空)
- `skills-superpowers/` (統合済み)
- 一時クローンディレクトリ

### 統合したスキル
- OWASP Security (claude-code-owasp)
- Trail of Bits Security Skills (static-analysis, insecure-defaults)
- Varlock (環境変数保護)
- Best Practice (claude-code-best-practice)
