ビルド、型チェック、リンティング、テスト、コード衛生にわたる包括的なデプロイ前検証を実行します。

## 実行モード

```
/verify           - 完全な検証（デフォルト）
/verify quick     - ビルド + 型チェックのみ
/verify pre-commit - コミットに関連するチェック
/verify pre-pr    - 完全 + セキュリティスキャン
```

## 検証ステップ

順番に実行 — 各ステップは次に進む前にパスする必要があります:

### 1. ビルド検証
```bash
npm run build     # または cargo build, go build 等
```

### 2. 型チェック
```bash
tsc --noEmit      # TypeScript
mypy .            # Python
```

### 3. リンティング
```bash
eslint . --max-warnings 0
ruff check .
```

### 4. テスト実行
```bash
npm test -- --coverage
pytest --cov=. --cov-report=term-missing
```

### 5. コンソール文の監査
```bash
grep -r "console\.log\|debugger\|print(" src/ --include="*.ts" --include="*.js"
```

### 6. Git ステータスの確認
```bash
git status
git diff --stat
```

## レポート形式

```
## 検証レポート

| チェック     | ステータス | 詳細                        |
|-------------|------------|----------------------------|
| ビルド       | ✅ 成功    |                            |
| 型          | ✅ 成功    | エラー 0 件                 |
| リント       | ⚠️ 警告   | 警告 3 件                   |
| テスト       | ✅ 成功    | 142/142 | カバレッジ: 87%   |
| コンソール   | ❌ 失敗    | src/auth.ts に 2 箇所       |
| Git ステータス | ✅ 成功  | 5 ファイル変更               |

**PR 準備完了:** いいえ — まずコンソール文を修正してください
```

いずれかの失敗に対して、詳細な修正ガイダンスを提供します。
