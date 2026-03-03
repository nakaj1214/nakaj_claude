# コーディング原則

常に従うべきコーディングの基本ルール。

## シンプルさ優先

- 複雑なコードよりも読みやすいコードを選ぶ
- 過度な抽象化を避ける
- 「動く」よりも「理解しやすい」を優先する

## 単一責任

- 1つの関数は1つのことだけを行う
- 1つのクラスは1つの責任だけを持つ
- 1ファイルあたり200〜400行を目標とする（最大800行）

## 早期リターン

```python
# 悪い例: 深いネスト
def process(value):
    if value is not None:
        if value > 0:
            return do_something(value)
    return None

# 良い例: 早期リターン
def process(value):
    if value is None:
        return None
    if value <= 0:
        return None
    return do_something(value)
```

## 型ヒント必須

すべての関数に型アノテーションを付けること:

```python
def call_llm(
    prompt: str,
    model: str = "gpt-4",
    max_tokens: int = 1000
) -> str:
    ...
```

## イミュータビリティ

詳細なパターンは [common/coding-style.md](common/coding-style.md#immutability-critical) を参照。

## 命名規則

- **変数/関数**: snake_case（英語）
- **クラス**: PascalCase（英語）
- **定数**: UPPER_SNAKE_CASE（英語）
- **意味のある名前**: `x` ではなく `user_count`

## マジックナンバー禁止

```python
# 悪い例
if retry_count > 3:
    ...

# 良い例
MAX_RETRIES = 3
if retry_count > MAX_RETRIES:
    ...
```
