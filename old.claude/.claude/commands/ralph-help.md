---
description: "Ralph Loop プラグインと利用可能なコマンドの説明"
---

# Ralph Loop プラグインヘルプ

以下の内容をユーザーに説明してください:

## Ralph Loop とは？

Ralph Loop は Ralph Wiggum テクニックを実装したもので、Geoffrey Huntley によって提唱された、継続的な AI ループに基づく反復的な開発手法です。

**基本コンセプト:**
```bash
while :; do
  cat PROMPT.md | claude-code --continue
done
```

同じプロンプトが Claude に繰り返し提供されます。「自己参照的」な側面は、出力を入力にフィードバックするのではなく、Claude がファイルや git 履歴にある自身の過去の作業を参照することで生まれます。

**各イテレーション:**
1. Claude が同じプロンプトを受け取る
2. タスクに取り組み、ファイルを修正
3. 終了を試みる
4. stop フックがインターセプトし、同じプロンプトを再度提供
5. Claude がファイル内の過去の作業を参照
6. 完了まで反復的に改善

このテクニックは「非決定論的な世界における決定論的な失敗」と表現されています。失敗が予測可能であるため、プロンプトのチューニングによる体系的な改善が可能になります。

## 利用可能なコマンド

### /ralph-loop <PROMPT> [OPTIONS]

現在のセッションで Ralph ループを開始します。

**使い方:**
```
/ralph-loop "Refactor the cache layer" --max-iterations 20
/ralph-loop "Add tests" --completion-promise "TESTS COMPLETE"
```

**オプション:**
- `--max-iterations <n>` - 自動停止までの最大イテレーション数
- `--completion-promise <text>` - 完了を示すプロミスフレーズ

**動作の仕組み:**
1. `.claude/.ralph-loop.local.md` 状態ファイルを作成
2. タスクに取り組む
3. 終了しようとすると stop フックがインターセプト
4. 同じプロンプトが再度提供される
5. 過去の作業を参照
6. プロミスが検出されるか最大イテレーションに達するまで継続

---

### /ralph-cancel

アクティブな Ralph ループをキャンセル（ループ状態ファイルを削除）します。

**使い方:**
```
/ralph-cancel
```

**動作の仕組み:**
- アクティブなループ状態ファイルを確認
- `.claude/.ralph-loop.local.md` を削除
- イテレーション数とともにキャンセルを報告

---

## 主要な概念

### 完了プロミス

完了を知らせるには、Claude は `<promise>` タグを出力する必要があります:

```
<promise>TASK COMPLETE</promise>
```

stop フックがこの特定のタグを探します。これ（または `--max-iterations`）がないと、Ralph は無限に実行されます。

### 自己参照メカニズム

「ループ」は Claude が自分自身と対話することを意味するのではなく、以下を意味します:
- 同じプロンプトが繰り返される
- Claude の作業がファイルに永続化される
- 各イテレーションで前回の試行が参照できる
- 目標に向かって段階的に構築される

## 例

### インタラクティブなバグ修正

```
/ralph-loop "Fix the token refresh logic in auth.ts. Output <promise>FIXED</promise> when all tests pass." --completion-promise "FIXED" --max-iterations 10
```

Ralph の動作:
- 修正を試みる
- テストを実行
- 失敗を確認
- 解決策を反復
- 現在のセッション内で実行

## Ralph を使うべき場面

**適している場合:**
- 明確な成功基準がある明確に定義されたタスク
- 反復と改善が必要なタスク
- 自己修正を伴う反復的な開発
- グリーンフィールドプロジェクト

**適していない場合:**
- 人間の判断やデザイン上の決定が必要なタスク
- ワンショット操作
- 成功基準が不明確なタスク
- 本番環境のデバッグ（代わりにターゲットを絞ったデバッグを使用）

## 詳細情報

- オリジナルテクニック: https://ghuntley.com/ralph/
- Ralph Orchestrator: https://github.com/mikeyobrien/ralph-orchestrator
