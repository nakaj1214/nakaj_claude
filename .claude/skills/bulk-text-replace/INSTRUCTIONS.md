# 一括テキスト置換 — 詳細手順

複数ファイルにまたがる同一テキストを、確認を挟みながら安全に一括置換する。

---

## 3ステップワークフロー

### Step 1: 対象ファイルの特定

```bash
# 置換対象のテキストを含むファイルを検索
grep -rl "置換前テキスト" .claude/ --include="*.md"

# 件数も確認
grep -r "置換前テキスト" .claude/ --include="*.md" | wc -l
```

結果をユーザーに提示し、置換範囲に問題ないか確認する。

### Step 2: 一括置換の実行

```bash
# macOS / GNU sed 両対応の一括置換
grep -rl "置換前テキスト" .claude/ --include="*.md" | \
  xargs sed -i 's/置換前テキスト/置換後テキスト/g'
```

**注意点:**
- 特殊文字（`/`, `&`, `\`）はエスケープが必要
- 大文字小文字を区別しない場合は `s/.../...../gI`
- 正規表現が必要な場合は `-E` フラグを追加

**Python を使う場合（特殊文字が多い場合に安全）:**
```bash
python3 -c "
import os, glob
pattern = '置換前テキスト'
replacement = '置換後テキスト'
for path in glob.glob('.claude/**/*.md', recursive=True):
    with open(path, 'r') as f:
        content = f.read()
    if pattern in content:
        with open(path, 'w') as f:
            f.write(content.replace(pattern, replacement))
        print(f'  Updated: {path}')
"
```

### Step 3: 差分確認

```bash
# git diff で置換結果を確認
git diff --stat
git diff
```

置換結果をユーザーに提示して完了。

---

## よくあるパターン

### ルール・スキルファイルの用語変更

```bash
# antigravity → ブラウザエージェント の例
grep -rl "antigravity" .claude/ --include="*.md" | \
  xargs sed -i 's/antigravity IDE/ブラウザエージェント/g'
```

### 設定値の一括更新

```bash
# ポート番号の変更
grep -rl "localhost:8080" . --include="*.md" --include="*.json" | \
  xargs sed -i 's/localhost:8080/localhost:28001/g'
```

### 複数パターンの同時置換

```bash
# sed で複数パターンを連続適用
grep -rl "旧テキスト1\|旧テキスト2" . --include="*.md" | \
  xargs sed -i -e 's/旧テキスト1/新テキスト1/g' -e 's/旧テキスト2/新テキスト2/g'
```

---

## 中止条件

- 置換対象が100ファイルを超える場合 → ユーザーに確認してから実行
- バイナリファイルが混在する場合 → `--include` で拡張子を絞る
- 正規表現が複雑で意図しない置換が起きる可能性がある場合 → Python スクリプトを使用
