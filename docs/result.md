## .claude/ 評価結果: 72点 / 100点

### 評価項目別スコア

| カテゴリ | 配点 | 得点 | 評価 |
|---|---|---|---|
| **CLAUDE.md (メイン指示)** | 15 | 10 | rules の `@` 参照が例示のみで実際にインポートされていない |
| **rules/ (ルール定義)** | 15 | 14 | 充実。16ファイル、多言語対応。hardware まで網羅 |
| **skills/ (スキル定義)** | 15 | 11 | 52スキル。evals.json が5件のみ (52件中)。重複が残存 |
| **agents/ (エージェント)** | 10 | 7 | 27件。カテゴリ分けは良いが `_shared/` 整理が未反映 |
| **commands/ (コマンド)** | 10 | 9 | 26件。十分な網羅性 |
| **hooks/ (フック)** | 10 | 6 | パスバグ、ipc残骸、__pycache__ コミット |
| **settings.json (設定)** | 5 | 4 | permissions は充実。model が sonnet 固定 |
| **docs/ (ドキュメント)** | 5 | 3 | DESIGN.md が別プロジェクトの内容。memory/ が乱雑 |
| **構造・衛生 (全体)** | 10 | 5 | `_shared/` との二重管理。STRUCTURE.md が実態と不一致 |
| **自動化・品質管理** | 5 | 3 | meta/ あり。registry あり。だが health-check 未活用 |

---

### 減点理由の詳細

#### 1. CLAUDE.md が弱い (-5)
- `@.claude/rules/security-rules.md` 等の参照が**コードブロック内の例示**にすぎず、実際のインポートとして機能していない
- ルールのインライン展開が起きないため、rules/ の内容がセッションに自動ロードされない
- 80行と短く、プロジェクト固有の技術スタック・アーキテクチャ情報がない

#### 2. `_shared/` と `.claude/` の二重管理 (-5)
- `.claude/agents/` にはまだ `comment-analyzer.md`, `conversation-analyzer.md`, `doc-updater.md`, `code-architect.md`, `refactor-cleaner.md` 等の**削除・統合済みファイル**が残存
- `.claude/skills/` にも `test-driven-development/`, `css-modern/`, `frontend-ui-ux/`, `update-design/`, `update-lib-docs/`, `vba-development/` が残存
- `_shared/` で実施した整理が `.claude/` に反映されていない

#### 3. hooks/ に問題あり (-4)
- **パスバグ**: `settings.json` の hook が `python3 .claude/hooks/...` だが、cwd が `.claude/` のときに `.claude/.claude/hooks/...` になり 404 エラー
- `hooks/ipc/` に 12 個の一時ファイル（`.pending`, `.decision`, `daemon.pid`）が残存
- `hooks/__pycache__/` に 9 個の `.pyc` ファイルが残存

#### 4. evals.json がほぼ皆無 (-4)
- 52スキル中わずか **5件** しか evals.json がない（9.6%）
- スキルの品質評価・回帰テストができない状態

#### 5. docs/memory/ が乱雑 (-2)
- HANDOVER ファイルが 9 個（重複タイムスタンプも含む）
- SKILL-SUGGESTIONS が 7 個、EDIT-PATTERNS が 3 個
- 古い memory ファイルの整理がされていない（計22ファイル）

#### 6. STRUCTURE.md が実態と不一致 (-3)
- 削除済みスキル（css-modern, vba-development 等）がまだ記載
- 新規スキル（codex-review, create-plan）が未記載
- 新規コマンド（learn-edits, materialize, review-staged）が未記載

#### 7. DESIGN.md が別プロジェクトの内容 (-2)
- 「`/manager/confirm` fix」「`x_ordered` schema」等、このリポジトリと無関係な内容
- テンプレートのまま放置されたセクションがある

---

### 高評価ポイント

- **rules/ の充実度**: Python / PHP / Laravel / JS / Hardware (ESP32, RPi) まで多言語カバー
- **skills の二段階ロード設計**: SKILL.md (軽量) + INSTRUCTIONS.md (詳細) の分離が一貫
- **agents のカテゴリ分け**: 8カテゴリに整理済み（planning / review / testing / debugging / refactoring / documentation / exploration / tooling）
- **hooks の設計思想**: pre-compact-handover, edit-tracker, post-test-analysis 等の自動化
- **meta/ の存在**: generate-registry.py と health-check.py による自己管理機能
- **settings.json の permissions**: deny ルールで機密ファイルを適切に保護

---

### 改善の優先度

| 優先度 | 項目 | 効果 |
|---|---|---|
| **高** | `_shared/` 整理を `.claude/` に反映（重複削除・統合済み反映） | 二重管理解消 |
| **高** | CLAUDE.md に `@` 参照を実際に記述 | ルールが自動ロードされる |
| **高** | hooks パスバグ修正 | hook エラー解消 |
| **中** | `__pycache__/`, `ipc/`, `logs/` の除外 | リポジトリ衛生改善 |
| **中** | docs/memory/ の古いファイル整理 | 22 → 必要なもののみ |
| **中** | STRUCTURE.md を実態に合わせて更新 | ドキュメント信頼性 |
| **低** | evals.json の追加 | スキル品質の定量評価 |
| **低** | DESIGN.md のリセット | 別プロジェクト内容を除去 |
