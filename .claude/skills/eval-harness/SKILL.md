---
name: eval-harness
description: Formal evaluation framework for Claude Code sessions implementing eval-driven development (EDD) principles. Claude Code セッションの正式な評価フレームワーク。eval 駆動開発（EDD）の原則を実装する。
tools: Read, Write, Edit, Bash, Grep, Glob
origin: everything-claude-code
---

# 評価ハーネス

出典: [everything-claude-code](https://github.com/affaan-m/everything-claude-code) `skills/eval-harness`

## 概要

「eval は AI 開発のユニットテストである」という原則に基づく包括的な評価フレームワーク。
実装前に期待される動作を定義し、eval を継続的に実行し、リグレッションを追跡し、
pass@k メトリクスで信頼性を測定する。

## eval の種類

| 種類 | 目的 |
|------|------|
| **ケイパビリティ eval** | 新機能が正しく動作するかテスト |
| **リグレッション eval** | 既存機能が壊れていないことを確認 |

## グレーダーのカテゴリ

| カテゴリ | 方法 | 用途 |
|---------|------|------|
| **コードベースグレーダー** | 決定論的チェック | 正確な出力マッチング |
| **モデルベースグレーダー** | Claude による評価 | オープンエンドな品質評価 |
| **ヒューマングレーダー** | 手動レビューフラグ | 主観的判断が必要なケース |

## メトリクス

- **pass@k**: k 回の試行のうち少なくとも1回成功
- **pass^k**: k 回の全試行が成功

## ワークフロー（4フェーズ）

### 1. Define（定義）
コードを書く前に成功基準を確立する。

```json
{
  "eval_id": "auth-login-001",
  "description": "ユーザーログインが正しく動作する",
  "input": {"email": "test@example.com", "password": "valid"},
  "expected": {"status": 200, "has_token": true},
  "grader": "code"
}
```

### 2. Implement（実装）
eval を満たすコードを実装する。

### 3. Evaluate（評価）
テストを実行し、結果を記録する。

### 4. Report（報告）
発見事項とステータスをドキュメント化する。

## ベストプラクティス

- 実装前に eval を定義する
- 頻繁に eval を実行する
- 信頼性のトレンドを時系列で追跡する
- 確率的メソッドよりコードグレーダーを優先する
- eval をプロジェクトの第一級成果物として維持する
