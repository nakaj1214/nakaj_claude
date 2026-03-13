---
tags: ['session', 'automation']
scope: session
date: 2026-03-10
---

# スキル候補レポート — 2026-03-10 08:32

## 検出されたパターン

- `/learn-edits` と `/materialize` が毎回セットで順番に実行されている（2ステップを手動で繰り返す）
- `materialize` 後にユーザーが「skillsのみ」と手動フィルタを指定した（Hook を意図的に除外）
- キューに 14件中 7件の「欠損ソースファイル参照」が蓄積しており、毎回スキップ処理が走っている
- `staging/` 配置後に別途 `.claude/skills/` へのコピーを手動実行している（approve → install が分離）
- 大容量の `edit-history.jsonl`（53KB/85件）を毎回全件読み込みしており、処理が重い

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `learn-and-materialize` | 「パターン分析して」「スキルを提案して」「編集ログからスキル作って」 | `/learn-edits` → `/materialize` を1コマンドで連続実行するラッパー。`--skills-only` / `--hooks-only` オプションで種別フィルタを指定可能にする | 高 |
| `install-staged` | 「stagingを適用して」「スキルをインストール」「staging から本番へ移動して」 | `staging/` の指定ディレクトリを `.claude/skills/` または `.claude/hooks/` に自動コピーし、STAGING-MANIFEST の status を `installed` に更新する | 中 |
| `queue-gc` | 「キューを整理して」「古い提案を削除して」「stale な QUEUE エントリをクリア」 | `AUTO-MATERIALIZE-QUEUE.jsonl` をスキャンし、source ファイルが存在しない `pending` エントリを `orphaned` に更新してキューを清潔に保つ | 中 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse | `materialize` スキル完了時 | ユーザーの過去の「skillsのみ」指定をメモリに保存し、次回 materialize 実行時に自動でスキルのみ生成するよう提案する | 低 |

---

## 観察事項

- **edit-history.jsonl の肥大化**: 85件/53KB に達しており、分析精度より読み込みコストが課題になりつつある。定期的なアーカイブ（例: 30日超のエントリをローテーション）が将来必要になる可能性があるが、現時点では自動化優先度は低い。
- **affected_files 欠落**: セッション `a15a2663`（全体の79%）で影響推定が完全に機能していない。これはツール側の問題であり、スキル/フックで解決できる範囲を超えている。
- **plan-rewrite-alert / large-delete-guard** の staging 残留: ユーザーが今回スキップを選択したが、将来的に有効化されると `same-file-edit-warn.py`（閾値3）と組み合わせて多段防御になる。