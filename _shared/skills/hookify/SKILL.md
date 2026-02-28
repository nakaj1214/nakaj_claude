---
name: writing-hookify-rules
description: ユーザーが「hookifyルールを作成したい」「フックルールを書きたい」「hookifyを設定したい」「hookifyルールを追加したい」と言った場合、またはhookifyルールの構文とパターンについてガイダンスが必要な場合に使用するスキル。
version: 0.1.0
---

# Hookifyルールの書き方

## 概要

Hookifyルールは、監視するパターンと、そのパターンがマッチした際に表示するメッセージを定義するYAMLフロントマター付きのMarkdownファイルである。ルールは `.claude/hookify.{rule-name}.local.md` ファイルに保存される。

## ルールファイルフォーマット

### 基本構造

```markdown
---
name: rule-identifier
enabled: true
event: bash|file|stop|prompt|all
pattern: regex-pattern-here
---

このルールがトリガーされた際にClaudeに表示するメッセージ。
Markdownのフォーマット、警告、提案などを含めることができる。
```

### フロントマターフィールド

**name**（必須）: ルールの一意識別子
- kebab-caseを使用: `warn-dangerous-rm`、`block-console-log`
- 説明的でアクション指向にする
- 動詞で始める: warn、prevent、block、require、check

**enabled**（必須）: 有効/無効を切り替えるBoolean
- `true`: ルールが有効
- `false`: ルールが無効（トリガーしない）
- ルールを削除せずに切り替え可能

**event**（必須）: トリガーするフックイベント
- `bash`: Bashツールコマンド
- `file`: Edit、Write、MultiEditツール
- `stop`: エージェントが停止しようとする時
- `prompt`: ユーザーがプロンプトを送信する時
- `all`: 全イベント

**action**（オプション）: ルールがマッチした際の動作
- `warn`: メッセージを表示するが操作を許可する（デフォルト）
- `block`: 操作を防ぐ（PreToolUse）またはセッションを停止（Stopイベント）
- 省略した場合は `warn` がデフォルト

**pattern**（シンプルフォーマット）: マッチさせるRegexパターン
- シンプルな単一条件ルールに使用
- コマンド（bash）またはnew_text（file）に対してマッチ
- PythonのRegex構文

**例:**
```yaml
event: bash
pattern: rm\s+-rf
```

### 高度なフォーマット（複数条件）

複数条件の複雑なルールの場合:

```markdown
---
name: warn-env-file-edits
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
---

.envファイルにAPIキーを追加しようとしています。このファイルが.gitignoreにあることを確認してください！
```

**条件フィールド:**
- `field`: チェックするフィールド
  - bashの場合: `command`
  - fileの場合: `file_path`、`new_text`、`old_text`、`content`
- `operator`: マッチ方法
  - `regex_match`: Regexパターンマッチング
  - `contains`: 部分文字列チェック
  - `equals`: 完全一致
  - `not_contains`: 部分文字列が存在しないこと
  - `starts_with`: プレフィックスチェック
  - `ends_with`: サフィックスチェック
- `pattern`: マッチさせるパターンまたは文字列

**全条件がマッチした場合にルールがトリガーされる。**

## メッセージ本文

フロントマター後のMarkdownコンテンツが、ルールがトリガーされた際にClaudeに表示される。

**良いメッセージ:**
- 何が検出されたかを説明する
- なぜ問題なのかを説明する
- 代替手段やベストプラクティスを提案する
- 明確さのためフォーマットを使用する（太字、リストなど）

**例:**
```markdown
⚠️ **Console.logが検出されました！**

本番コードにconsole.logを追加しようとしています。

**なぜ問題なのか:**
- デバッグログは本番環境に含めるべきでない
- Console.logは機密データを露出させる可能性がある
- ブラウザのパフォーマンスに影響する

**代替手段:**
- 適切なロギングライブラリを使用する
- コミット前に削除する
- 条件付きデバッグビルドを使用する
```

## イベントタイプガイド

### bashイベント

Bashコマンドパターンをマッチさせる:

```markdown
---
event: bash
pattern: sudo\s+|rm\s+-rf|chmod\s+777
---

危険なコマンドが検出されました！
```

**よくあるパターン:**
- 危険なコマンド: `rm\s+-rf`、`dd\s+if=`、`mkfs`
- 権限昇格: `sudo\s+`、`su\s+`
- 権限の問題: `chmod\s+777`、`chown\s+root`

### fileイベント

Edit/Write/MultiEdit操作をマッチさせる:

```markdown
---
event: file
pattern: console\.log\(|eval\(|innerHTML\s*=
---

問題のある可能性があるコードパターンが検出されました！
```

**異なるフィールドでマッチさせる:**
```markdown
---
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.tsx?$
  - field: new_text
    operator: regex_match
    pattern: console\.log\(
---

TypeScriptファイルにConsole.logがあります！
```

**よくあるパターン:**
- デバッグコード: `console\.log\(`、`debugger`、`print\(`
- セキュリティリスク: `eval\(`、`innerHTML\s*=`、`dangerouslySetInnerHTML`
- 機密ファイル: `\.env$`、`credentials`、`\.pem$`
- 生成ファイル: `node_modules/`、`dist/`、`build/`

### stopイベント

エージェントが停止しようとする際にマッチさせる（完了チェック）:

```markdown
---
event: stop
pattern: .*
---

停止前に確認する:
- [ ] テストを実行した
- [ ] ビルドが成功した
- [ ] ドキュメントを更新した
```

**使用目的:**
- 必要なステップのリマインダー
- 完了チェックリスト
- プロセスの強制

### promptイベント

ユーザープロンプトの内容をマッチさせる（高度）:

```markdown
---
event: prompt
conditions:
  - field: user_prompt
    operator: contains
    pattern: deploy to production
---

本番デプロイチェックリスト:
- [ ] テストは通過しているか？
- [ ] チームのレビューを受けたか？
- [ ] モニタリングは準備できているか？
```

## パターン記述のコツ

### Regex基礎

**リテラル文字:** ほとんどの文字はそのままマッチする
- `rm` は "rm" にマッチ
- `console.log` は "console.log" にマッチ

**特殊文字はエスケープが必要:**
- `.`（任意文字）→ `\.`（リテラルのドット）
- `(` `)` → `\(` `\)`（リテラルの括弧）
- `[` `]` → `\[` `\]`（リテラルのブラケット）

**よく使うメタ文字:**
- `\s` - 空白（スペース、タブ、改行）
- `\d` - 数字（0-9）
- `\w` - 単語文字（a-z、A-Z、0-9、_）
- `.` - 任意の文字
- `+` - 1回以上
- `*` - 0回以上
- `?` - 0回または1回
- `|` - OR

**例:**
```
rm\s+-rf         マッチ: rm -rf, rm  -rf
console\.log\(   マッチ: console.log(
(eval|exec)\(    マッチ: eval( または exec(
chmod\s+777      マッチ: chmod 777, chmod  777
API_KEY\s*=      マッチ: API_KEY=, API_KEY =
```

### パターンのテスト

使用前にRegexパターンをテストする:

```bash
python3 -c "import re; print(re.search(r'your_pattern', 'test text'))"
```

またはオンラインのRegexテスター（regex101.com、Pythonフレーバー）を使用する。

### よくある落とし穴

**広すぎる:**
```yaml
pattern: log    # "log"、"login"、"dialog"、"catalog"にマッチ
```
改善: `console\.log\(|logger\.`

**狭すぎる:**
```yaml
pattern: rm -rf /tmp  # 正確なパスにのみマッチ
```
改善: `rm\s+-rf`

**エスケープの問題:**
- YAMLの引用符付き文字列: `"pattern"` はダブルバックスラッシュ `\\s` が必要
- YAMLの引用符なし: `pattern: \s` はそのまま動作
- **推奨**: YAMLでは引用符なしのパターンを使用する

## ファイルの整理

**場所:** 全ルールは `.claude/` ディレクトリに
**命名:** `.claude/hookify.{説明的な名前}.local.md`
**Gitignore:** `.gitignore` に `.claude/*.local.md` を追加

**良い名前:**
- `hookify.dangerous-rm.local.md`
- `hookify.console-log.local.md`
- `hookify.require-tests.local.md`
- `hookify.sensitive-files.local.md`

**悪い名前:**
- `hookify.rule1.local.md`（説明的でない）
- `hookify.md`（.localがない）
- `danger.local.md`（hookifyプレフィックスがない）

## ワークフロー

### ルールの作成

1. 望ましくない動作を特定する
2. 関係するツールを特定する（Bash、Editなど）
3. イベントタイプを選択する（bash、file、stopなど）
4. Regexパターンを書く
5. プロジェクトルートに `.claude/hookify.{name}.local.md` ファイルを作成する
6. すぐにテストする - ルールは次のツール使用時に動的に読み込まれる

### ルールの改善

1. `.local.md` ファイルを編集する
2. パターンまたはメッセージを調整する
3. すぐにテストする - 変更は次のツール使用時に有効になる

### ルールの無効化

**一時的に:** フロントマターで `enabled: false` を設定する
**永続的に:** `.local.md` ファイルを削除する

## 例

完全な例は `${CLAUDE_PLUGIN_ROOT}/examples/` を参照:
- `dangerous-rm.local.md` - 危険なrmコマンドをブロック
- `console-log-warning.local.md` - console.logについて警告
- `sensitive-files-warning.local.md` - .envファイル編集について警告

## クイックリファレンス

**最小限のルール:**
```markdown
---
name: my-rule
enabled: true
event: bash
pattern: dangerous_command
---

警告メッセージをここに
```

**条件付きルール:**
```markdown
---
name: my-rule
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.ts$
  - field: new_text
    operator: contains
    pattern: any
---

警告メッセージ
```

**イベントタイプ:**
- `bash` - Bashコマンド
- `file` - ファイル編集
- `stop` - 完了チェック
- `prompt` - ユーザー入力
- `all` - 全イベント

**フィールドオプション:**
- Bash: `command`
- File: `file_path`、`new_text`、`old_text`、`content`
- Prompt: `user_prompt`

**オペレーター:**
- `regex_match`、`contains`、`equals`、`not_contains`、`starts_with`、`ends_with`
