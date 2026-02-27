# Codex CLI + Claude Code マルチエージェント統合 ベストプラクティス

作成日: 2026-02-24

## ソース記事

1. https://note.com/hantani/n/na2a2dcae66c4 - "Claude CodeからSkillsでCodexを使う"
2. https://zenn.dev/owayo/articles/63d325934ba0de - MCP vs Skills比較・セッション管理
3. https://zenn.dev/foxytanuki/articles/9df8e0134ed412 - Codex MCP実行レイヤーパターン
4. https://zenn.dev/toshipon/articles/7eaddcae87944e - 分業モデル（設計・テスト・レビュー vs 実装）
5. https://qiita.com/Null_06/items/4c61176ed5f1bc236ac2 - オーケストレーター権限・ルーティング決定木

---

## 1. 役割分担：誰が何をするか

### 推奨モデル: Claude Code = オーケストレーター、Codex = 実装ワーカー + レビューワーカー（設計書/コード）

| タスク種別 | 担当 | 理由 |
|-----------|------|------|
| アーキテクチャ設計 | Claude Code | プロジェクト固有コンテキストが必要 |
| セキュリティ変更 | Claude Code | 境界・権限判断が必要 |
| テスト設計 / TDDサイクル | Claude Code | 反復的な分析が必要 |
| 設計書のレビュー（品質/抜け漏れ/矛盾） | Codex | 構造レビュー・論理矛盾検出が得意 |
| コードレビュー（品質/バグ/性能/指摘） | Codex | バグ/性能観点・網羅性の指摘が得意 |
| 単一モジュール実装 | Codex | 高速・集中的なコード生成 |
| テストコード生成 | Codex | 仕様→テスト変換の強み |
| 大規模リファクタリング | Codex | 10+ファイル、50+行が目安 |
| 定型コード (ボイラープレート) | Codex | 単純生成タスク |
| 最終確認（承認/マージ判断/リスク受容） | Claude Code | 全体整合・セキュリティ境界・運用判断の最終責任 |

**Codexへの委譲目安 (toshipon記事より):**
- 10+ ファイルのリファクタリング
- 複数ファイルにまたがる 50+ 行
- コンテキストウィンドウが 150K トークン超
- 大規模ボイラープレート生成
- 設計書/コードのレビュー（機械的に漏れを洗い出す用途）

**Claude Code内で処理すべきもの:**
- 20行以下の変更（委譲オーバーヘッドが勝つ）
- TDDサイクル（Red→Green→Refactorの回転）
- アーキテクチャ決定（対話的な反復が必要）
- セキュリティ境界の最終判断
- 最終確認（承認/マージ判断）

### 最大リトライ制限
- Codex が 2回失敗（またはレビュー指摘が収束しない）したら Claude Code が直接引き継ぐ (Qiita記事より)

---

## 2. 統合方式: MCP vs Skills

### MCP統合の問題点

- **ブラックボックス問題**: 実行中の進捗が見えない。長時間タスクに不向き
- **elicitationプロトコル未対応**: Codexが承認要求を出した際、Claude Codeが応答できず無限ハング
- **回避策**: `approval-policy: "never"` を設定してハングを防ぐ

```bash
claude mcp add -s user codex codex -- mcp-server -c 'approval_policy="never"'
```

### Skills統合の利点

- リアルタイム出力ストリーミング（進捗モニタリング・中断が可能）
- Slash コマンドまたは自然言語でトリガー可能
- MCPより透明性が高い

### セッション管理 (owayo記事より)

```bash
# セッション継続構文
codex exec --full-auto --sandbox read-only --cd <dir> "<request>" resume <session_id>
```

- Claude Code は異なるタスクで `session_id` を誤って再利用することがある
- Codex のほうがコンテキスト継続管理が安定している

---

## 3. コンテキストウィンドウ管理

### サブエージェント・パターン（最重要）

```
メインClaude Code (オーケストレーター)
  → 軽量に保つ
  → 重いタスクはサブエージェントに委譲

  ┌─── サブエージェント (review/implementation worker) ───┐
  │  → Codex CLIを呼び出し                                  │
  │  → 完全な出力を .claude/docs/ に保存                    │
  │  → 重要な知見のみをメインに返す                         │
  └─────────────────────────────────────────────────────────┘
```

### 実践ルール

1. **委譲**: 大きな出力が予想されるタスクは `run_in_background: true` でサブエージェントへ
2. **要約返却**: サブエージェントはCodexの全出力をそのまま返さず、「結論 + 主な理由2-3点 + リスク + 次アクション」に絞る
3. **ファイル出力**: 詳細な調査/レビュー結果は `.claude/docs/research/` や `.claude/docs/review/` に書き出し、メインは参照のみ

### Codexのコンテキスト制約

**重要**: Codex は Claude Code のファイル読み取りにアクセスできない（コンテキスト分離）

Codex へのプロンプトには必ず明示的に含めること:
- 技術スタック詳細
- 対象ファイルパス
- 参照パターン例
- 変更スコープの制約
- レビュー観点（設計書レビュー/コードレビューで何を見たいか）

---

## 4. スキル/Slashコマンドパターン

### Codex呼び出しのSlashコマンド例

```bash
# /codex トリガー
# または自然言語: "codexと相談して" / "レビューして"
codex exec --model gpt-5.2-codex --sandbox read-only --full-auto "{question}" 2>/dev/null
codex exec --model gpt-5.2-codex --sandbox workspace-write --full-auto "{task}" 2>/dev/null
```

### レビューループのためのスキル設計（Codexレビュー → Claude最終確認）

**品質ゲートとして機能させる設計原則:**

1. **明確なトリガーと入出力の固定**
   - トリガー: `/design_review` `/code_review` など
   - 入力ファイル: `docs/plan.md` / `docs/design.md` / `docs/implement/plan.md` など（固定化推奨）
   - 出力ファイル: `docs/review/design_review.md` / `docs/review/code_review.md`（固定化推奨）

2. **チェックリストの組み込み（Codex側）**
   - 設計書レビュー:
     - スコープの明確性
     - 前提条件・依存関係
     - 影響範囲 (DB・ルート・フロントエンド等)
     - 例外系・エラーハンドリング方針
     - テスト/検証の具体性
     - リスクと対策
   - コードレビュー:
     - バグ/エッジケース
     - 性能/計算量/クエリ回数
     - 型/例外/境界条件
     - 影響範囲・副作用
     - セキュリティ観点（ただし最終判断はClaude）

3. **判定トークンの強制（Codex側）**
   - レビュー結果の最終行に必ず判定トークンを出力:
   ```
   APPROVED  または  CHANGES_REQUIRED
   ```
   - これによりオーケストレーター（Claude）が次ステップを自動判断可能

### Multi-Turn実装パターン (toshipon記事より)

```
# フェーズ1: 型定義
mcp__codex__codex(prompt="型定義を実装...")

# フェーズ2: サービス層 (フェーズ1完了後)
mcp__codex__codex-reply(thread_id=..., prompt="サービス層を実装...")

# フェーズ3: ルートハンドラ
mcp__codex__codex-reply(thread_id=..., prompt="ルートハンドラを実装...")
```

---

## 5. セキュリティ上の注意

- Claude Code の deny-list は MCP サーバー内部には適用されない
- `developer-instructions` でルールを注入しても技術的強制力ではなく運用的担保に過ぎない
- セキュリティ要件の高いタスクはCodexに委譲しない（または read-only レビューに限定）
- Codexへのプロンプトに明示的にセキュリティ制約を記述する
- 最終確認（リスク受容）は必ずClaude Codeが行う

---

## 6. 実装品質を担保するガード

- 常にフィーチャーブランチで作業
- `git diff` でCodexの出力を検証
- コミット前にテスト実行
- エラーハンドリング要件をプロンプトに必ず含める
- **設計書レビュー（Codex）→設計の最終確認（Claude）**
- **コードレビュー（Codex）→マージ可否の最終確認（Claude）**

---

## まとめ: 推奨アーキテクチャ

```
ユーザー
  ↓
Claude Code (オーケストレーター)
  ├── 設計・計画・セキュリティ → 直接処理
  ├── 設計書レビュー → Codex (サブエージェント経由 / sandbox: read-only)
  ├── 実装・デバッグ → Codex (サブエージェント経由 / sandbox: workspace-write)
  ├── コードレビュー → Codex (サブエージェント経由 / sandbox: read-only)
  └── 最終確認（承認/マージ判断/リスク受容） → Claude Code
```

**判断フロー:**
- 「設計・計画が必要か？」→ YES: Claude Code で直接処理
- 「設計書/コードのレビューか？」→ YES: Codexでレビュー → Claudeが最終確認
- 「大きな出力が予想されるか？」→ YES: サブエージェント経由
- 「Codexが2回失敗したか？」→ YES: Claude Code が直接引き継ぐ
- 「最終判断（承認/マージ/運用リスク）は必要か？」→ 常に Claude Code
