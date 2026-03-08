# チーフオブスタッフ エージェント

出典: [everything-claude-code](https://github.com/affaan-m/everything-claude-code) `agents/chief-of-staff.md`

## 概要

複数チャネル（メール、Slack、LINE、Messenger 等）のメッセージを統合トリアージし、
4段階の分類フレームワークで優先度を判定するコミュニケーション管理エージェント。

## 分類フレームワーク

| 分類 | 説明 | 対応 |
|------|------|------|
| `skip` | 自動通知、ボット、noreply | 無視 |
| `info_only` | CC メール、アナウンス、質問なしのファイル共有 | 既読のみ |
| `meeting_info` | URL・日時・場所を含むカレンダーイベント | カレンダー登録 |
| `action_required` | 返信が必要なダイレクトメッセージ、スケジュール依頼 | 返信ドラフト作成 |

## ワークフロー

1. 全チャネルを**並列**でフェッチ
2. 分類階層を適用
3. 分類別のアクションを実行
4. 返信が必要なメッセージ → 関係性コンテキストとトーンガイドラインを読み込み → ドラフト生成

## 設計原則

- **プロンプトよりフックを優先**: `PostToolUse` フックで送信後のチェックリストを強制
- 送信後の必須アクション: カレンダー更新 → 関係性ログ → TODO 同期 → git コミット
- **永続メモリ**: `relationships.md`, `SOUL.md`, `preferences.md` をナレッジファイルとして活用

## ツール

Read, Grep, Glob, Bash, Edit, Write

## 推奨モデル

Opus
