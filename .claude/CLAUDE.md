## ルール自動ロード

`.claude/rules/` 内の `.md` ファイルは Claude Code が自動検出しセッションに注入する。
パス指定ルール（`paths:` フロントマター）を使えばファイル種別ごとの条件付きロードも可能。
詳細: `.claude/docs/path-rules-guide.md`

### 現在のルール構成

- **常時ロード（共通）**: coding-principles, language, security-rules, skill-execution, work-modes, common/ (coding-style, git-workflow, testing)
- **条件付きロード（`paths:` 指定）**:
  - Python (`**/*.py`): python/ (coding-style, dev-environment, testing)
  - PHP/Laravel (`**/*.php`): php/coding-style, laravel/conventions
  - JavaScript (`**/*.js,*.ts`): javascript/jquery-style
  - Hardware (`**/*.ino,*.c,*.cpp`): hardware/ (embedded-c-style, raspberry-pi, esp32)
  - Frontend (`**/*.js,*.css,*.html,*.blade.php`): ui-fix-verification

---

## ワークフロー設計

詳細: `.claude/docs/workflow-guide.md`

1. **Planモード基本**: 3ステップ以上のタスクは必ずPlanモード。行き詰まったら再計画
2. **サブエージェント活用**: リサーチ・並列分析はサブエージェントに委譲。1エージェント=1タスク
3. **自己改善ループ**: 修正 → `lessons.md` に記録 → ルール改善
4. **完了前検証**: 動作証明まで完了としない。テスト実行・ログ確認
5. **エレガントさ**: 重要な変更前に「もっと良い方法は？」。シンプルな修正は過剰設計しない
6. **自律バグ修正**: バグレポートを受けたら自分で解決。ユーザーのコンテキスト切替ゼロ
7. **研究と実装分離**: 調査で方針確定 → 新コンテキストで実装。混ぜない
8. **セッション分割**: 1セッション = 1コントラクト。終了時 `/handover`
9. **完了契約**: `docs/contracts/` に完了条件を事前定義。全条件達成まで未完了
10. **挙動改善**: 気に入らない挙動 → `rules/`、繰り返し手順 → `skills/`

---

## タスク管理

1. **まず計画を立てる**：チェック可能な項目として `tasks/todo.md` に計画を書く
2. **計画を確認する**：実装を開始する前に確認する
3. **進捗を記録する**：完了した項目を随時マークしていく
4. **変更を説明する**：各ステップで高レベルのサマリーを提供する
5. **結果をドキュメント化する**：`tasks/todo.md` にレビューセクションを追加する
6. **学びを記録する**：修正を受けた後に `.claude/docs/lessons.md` を更新する

---

## コア原則

- **シンプル第一**：すべての変更をできる限りシンプルにする。影響するコードを最小限にする。
- **手を抜かない**：根本原因を見つける。一時的な修正は避ける。シニアエンジニアの水準を保つ。
- **影響を最小化する**：変更は必要な箇所のみにとどめる。バグを新たに引き込まない。
- **人間が最終責任者**：エージェントの成果物はすべて人間がレビュー・承認する。完璧なエージェントは存在しない。

---

## スキル設計原則

参考: [skill-creatorとOrchestration Skillsの設計パターン](https://nyosegawa.github.io/posts/skill-creator-and-orchestration-skill/)

1. **SKILL.md はフロー制御に徹する**: 専門処理は `agents/` サブプロンプトに分離。Progressive Disclosure
2. **確定的処理 → スクリプト**: ループ・計算・ファイル操作は `scripts/`、判断・分析・生成は Agent
3. **スキーマ契約を先に設計**: `references/schemas.md` に JSON スキーマを定義
4. **Why-driven なプロンプト**: 理由を説明して柔軟性確保。クリティカルな箇所のみ Must-driven
5. **description 最適化に注力**: システムプロンプトに注入されるのは name + description のみ。押し強めに
6. **オーケストレーション選択**: 並列性 → Sub-agent 型、順序性 → Skill Chain 型

---

## 定期メンテナンス（月次）

ルール/スキルの肥大化を防ぐため、月1回の棚卸しを行う:

- [ ] 矛盾するルールがないか
- [ ] 重複するスキル/ルールがないか
- [ ] 使われていないスキル/エージェントがないか
- [ ] 常時ロードのルール行数が1,000行以内か
- [ ] `paths:` 指定で条件付きロードにできるルールがないか

---

## セッション開始チェック

以下の順序で確認する（Read のみ、全文注入しない）:

1. `.claude/docs/PROJECT-PROFILE.md` — プロジェクト全体像の把握
2. `.claude/docs/user-preferences.md` — ユーザースタイルの確認
3. `.claude/docs/memory/HANDOVER-*.md`（最新）— 前セッションの状態把握
4. `.claude/docs/lessons.md`（直近3件）— 同じミスの防止
5. `.claude/docs/memory/AUTO-MATERIALIZE-QUEUE.jsonl` — pending があれば通知:
   「前セッションから N 件の skill/hook 候補があります。`/materialize` で staging に生成できます」
6. QUEUE ファイルが存在しない場合は何もしない

---

## フィードバック記録

ユーザーから修正を受けたら feedback-loop スキルの手順に従い3ファイルを更新する。
同一カテゴリ3件で自動対策候補を QUEUE に追加。詳細: `.claude/skills/feedback-loop/INSTRUCTIONS.md`

## トラブルシューティング

問題に遭遇したら `.claude/docs/playbooks.md` を参照。
