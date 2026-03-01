# 改善提案

_shared の改善アイデアや未対応タスクを管理するファイル。
完了したものは「完了済み」セクションに移動する。

---

## 未対応

### 1. `docs/unique-files-inventory.md` の更新

移植・削除した状況を反映して最新化する。

---

## 完了済み

| 内容 | 詳細 |
|-----|------|
| 公式ドキュメントを調査して _shared に反映 | `https://code.claude.com/docs` を調査。claude_settings.json を実際のスキーマに修正、skill-creator に三人称ルール・gerund 命名・アンチパターンを追加、`.claude/rules/` パス指定ルールのガイドを追加、CLAUDE.md に `@` インポート構文を追加 |
| skill-creator を二段階ロード対応に更新 | Zenn記事を参考に SKILL.md 最小化 + INSTRUCTIONS.md 詳細化 |
| 全スキルを二段階ロード形式に変換 | Python スクリプトで 35 スキルを一括変換 |
| LiftKit を css-organization に統合 | ゴールデンレシオ・光学対称・WCAG コントラスト比パターンを追記 |
| handover スキル作成 | `/handover` でセッション引き継ぎドキュメントを手動生成 |
| PreCompact フック実装 | 自動コンパクション前に HANDOVER + SKILL-SUGGESTIONS を並列生成 |
| パターン学習 → スキル候補自動生成 | `pre-compact-handover.py` に分析機能を追加 |
| _shared 再設計案 | `docs/shared-redesign.md` に詳細設計を記録 |
| 重複ファイルの解消 | security・reviewer・TDD の重複を整理・統合 |
