# Claude Codeプラグインのスキル開発

このスキルはClaude Codeプラグインのための効果的なスキルを作成するためのガイダンスを提供する。

## スキルについて

スキルは特殊な知識、ワークフロー、ツールを提供することでClaudeの能力を拡張するモジュール式で自己完結型のパッケージです。スキルはClaudeを汎用エージェントから、どのモデルも完全には持てない手続き的知識を持つ特殊エージェントに変換する「オンボーディングガイド」と考えてください。

### スキルが提供するもの

1. 特殊ワークフロー — 特定のドメインのための複数ステップの手順
2. ツール統合 — 特定のファイル形式やAPIを扱うための指示
3. ドメイン専門知識 — 企業固有の知識、スキーマ、ビジネスロジック
4. バンドルリソース — 複雑で反復的なタスクのためのスクリプト、リファレンス、アセット

### スキルの構造

各スキルは必須のSKILL.mdファイルとオプションのバンドルリソースで構成される:

```
skill-name/
├── SKILL.md (必須)
│   ├── YAMLフロントマターメタデータ（必須）
│   │   ├── name: (必須)
│   │   └── description: (必須)
│   └── Markdownの指示（必須）
└── バンドルリソース（オプション）
    ├── scripts/          - 実行可能コード（Python/Bashなど）
    ├── references/       - 必要に応じてコンテキストに読み込まれるドキュメント
    └── assets/           - 出力で使用するファイル（テンプレート、アイコン、フォントなど）
```

#### SKILL.md（必須）

**メタデータの品質:** YAMLフロントマターの`name`と`description`は、Claudeがスキルをいつ使用するかを決定する。スキルが何をするか、いつ使用するかについて具体的に書く。3人称を使用する（例: 「Use this skill when...」の代わりに「This skill should be used when...」）。

#### バンドルリソース（オプション）

##### スクリプト（`scripts/`）

決定論的な信頼性が必要なタスクや繰り返し書き直されるタスクのための実行可能コード（Python/Bashなど）。

- **含める時**: 同じコードが繰り返し書き直されている場合や決定論的な信頼性が必要な場合
- **例**: PDFローテーションタスクの`scripts/rotate_pdf.py`
- **メリット**: トークン効率的、決定論的、コンテキストに読み込まずに実行可能

##### リファレンス（`references/`）

ClaudeのプロセスとThinkingを情報提供するために必要に応じてコンテキストにロードするドキュメントとリファレンス資料。

- **含める時**: Claudeが作業中に参照すべきドキュメントがある場合
- **例**: 財務スキーマの`references/finance.md`、会社のNDAテンプレートの`references/mnda.md`
- **ベストプラクティス**: SKILL.mdをリーンに保つため詳細情報はreferecesファイルに置く

##### アセット（`assets/`）

コンテキストにロードすることを意図せず、Claudeが生成する出力内で使用するファイル。

- **含める時**: スキルが最終出力で使用するファイルが必要な場合
- **例**: ブランドアセットの`assets/logo.png`、テンプレートの`assets/slides.pptx`

### プログレッシブディスクロージャーの設計原則

スキルはコンテキストを効率的に管理するための3レベルのローディングシステムを使用する:

1. **メタデータ（name + description）** - 常にコンテキストに（約100ワード）
2. **SKILL.md本文** - スキルがトリガーされた時（5,000ワード以下）
3. **バンドルリソース** - Claudeが必要に応じて（無制限*）

*スクリプトはコンテキストウィンドウに読み込まずに実行できるため無制限。

## スキル作成プロセス

スキルを作成するには、「スキル作成プロセス」を順番に従い、適用されない明確な理由がある場合のみステップをスキップする。

### ステップ1: 具体的な例でスキルを理解する

スキルの使用パターンがすでに明確に理解されている場合のみこのステップをスキップする。

効果的なスキルを作成するには、スキルがどのように使用されるかの具体的な例を明確に理解する。例えば、image-editorスキルを構築する際の関連質問:

- 「image-editorスキルはどんな機能をサポートすべきですか？編集、ローテーション、他に何か？」
- 「このスキルがどのように使われるかの例を教えてもらえますか？」
- 「'この画像の赤目を除去して'や'この画像をローテートして'のような操作が考えられます。他にはどんな使い方が考えられますか？」

### ステップ2: 再利用可能なスキルコンテンツの計画

具体的な例を効果的なスキルに変換するには、各例を分析する:

1. その例をゼロから実行する方法を考える
2. これらのワークフローを繰り返し実行する際に役立つスクリプト、リファレンス、アセットを特定する

**例: `pdf-editor`スキル**
- PDFのローテーションは毎回同じコードを書き直す必要がある
- スキルに保存する`scripts/rotate_pdf.py`スクリプトが役立つ

**例: `big-query`スキル**
- BigQueryのクエリは毎回テーブルスキーマと関係を再発見する必要がある
- スキルに保存するテーブルスキーマを文書化した`references/schema.md`が役立つ

**Claude Codeプラグインの場合（hooksスキル）:**
1. 開発者は繰り返しhooks.jsonを検証しフックスクリプトをテストする必要がある
2. `scripts/validate-hook-schema.sh`と`scripts/test-hook.sh`ユーティリティが役立つ
3. SKILL.mdを肥大化させないための詳細なフックパターンの`references/patterns.md`が役立つ

### ステップ3: スキル構造の作成

Claude Codeプラグインのために、スキルディレクトリ構造を作成する:

```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

**注意:** 汎用的なskill-creatorとは異なり、プラグインスキルはプラグインの`skills/`ディレクトリに直接作成する。

### ステップ4: スキルを編集する

SKILL.mdを編集する際、スキルは別のClaudeインスタンスが使用するために作成されていることを覚えておく。Claudeにとって有益で明白でない情報を含めることに集中する。

#### SKILL.mdの更新

**文章スタイル:** 2人称ではなく**命令形/不定詞形**（動詞始まりの指示）を使用してスキル全体を書く。客観的で指示的な言葉を使う（「あなたはXをすべき」の代わりに「XをするにはYをする」）。

**Description（フロントマター）:** 特定のトリガーフレーズを含む3人称フォーマットを使用:

```yaml
---
name: Skill Name
description: This skill should be used when the user asks to "specific phrase 1", "specific phrase 2", "specific phrase 3". Include exact phrases users would say that should trigger this skill. Be concrete and specific.
version: 0.1.0
---
```

**良いdescriptionの例:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks", or mentions hook events (PreToolUse, PostToolUse, Stop).
```

**悪いdescriptionの例:**
```yaml
description: Use this skill when working with hooks.  # 間違った人称、曖昧
description: Load when user needs hook help.  # 3人称でない
description: Provides hook guidance.  # トリガーフレーズなし
```

SKILL.md本文を完成させるために以下の質問に答える:

1. スキルの目的は何か（数文で）？
2. スキルはいつ使用すべきか？（特定のトリガーを含むフロントマターのdescriptionに含める）
3. 実際には、Claudeはスキルをどのように使用すべきか？

**SKILL.mdをリーンに保つ:** 本文は1,500〜2,000ワードを目標にする。詳細コンテンツはreferences/に移動:
- 詳細なパターン → `references/patterns.md`
- 高度なテクニック → `references/advanced.md`
- 移行ガイド → `references/migration.md`

### ステップ5: 検証とテスト

**プラグインスキルの検証:**

1. **構造を確認**: `plugin-name/skills/skill-name/`にスキルディレクトリがある
2. **SKILL.mdを検証**: nameとdescriptionを持つフロントマターがある
3. **トリガーフレーズを確認**: descriptionにユーザーが言いそうな具体的なクエリが含まれている
4. **文章スタイルを確認**: 本文が命令形/不定詞形を使用、2人称でない
5. **プログレッシブディスクロージャーをテスト**: SKILL.mdがリーン（1,500〜2,000ワード）、詳細コンテンツがreferences/にある
6. **リファレンスを確認**: 参照されたファイルが全て存在する
7. **例を検証**: 例が完全で正しい
8. **スクリプトをテスト**: スクリプトが実行可能で正しく機能する

### ステップ6: 反復する

スキルをテストした後、ユーザーが改善を要求することがある。

**反復ワークフロー:**
1. 実際のタスクでスキルを使用する
2. 苦労や非効率に気づく
3. SKILL.mdやバンドルリソースをどのように更新すべきか特定する
4. 変更を実施して再度テストする

**一般的な改善:**
- descriptionのトリガーフレーズを強化する
- SKILL.mdの長いセクションをreferences/に移動する
- 欠落している例やスクリプトを追加する
- 曖昧な指示を明確にする
- エッジケース処理を追加する

## プラグイン固有の考慮事項

### プラグイン内のスキルの場所

プラグインスキルはプラグインの`skills/`ディレクトリに置く:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── agents/
└── skills/
    └── my-skill/
        ├── SKILL.md
        ├── references/
        ├── examples/
        └── scripts/
```

### 自動検出

Claude Codeはスキルを自動的に検出する:
- `skills/`ディレクトリをスキャン
- `SKILL.md`を含むサブディレクトリを検出
- スキルメタデータ（name + description）を常にロード
- スキルがトリガーされた時にSKILL.md本文をロード
- 必要に応じてreferences/examplesをロード

## プログレッシブディスクロージャーの実践

### SKILL.mdに含めるもの

**含める（スキルがトリガーされた時に常にロード）:**
- コアコンセプトと概要
- 必須の手順とワークフロー
- クイックリファレンステーブル
- references/examples/scriptsへのポインター
- 最も一般的なユースケース

**3,000ワード以下、理想は1,500〜2,000ワード**

### references/に含めるもの

**references/に移動（必要に応じてロード）:**
- 詳細なパターンと高度なテクニック
- 包括的なAPIドキュメント
- 移行ガイド
- エッジケースとトラブルシューティング
- 広範な例とウォークスルー

### examples/に含めるもの

**動作するコード例:**
- 完全で実行可能なスクリプト
- 設定ファイル
- テンプレートファイル
- 実際の使用例

### scripts/に含めるもの

**ユーティリティスクリプト:**
- 検証ツール
- テストヘルパー
- パースユーティリティ
- 自動化スクリプト

## 文章スタイルの要件

### 命令形/不定詞形

2人称ではなく動詞始まりの指示を書く:

**正しい（命令形）:**
```
フックを作成するには、イベントタイプを定義する。
認証でMCPサーバーを設定する。
使用前に設定を検証する。
```

**間違い（2人称）:**
```
フックを作成するためにイベントタイプを定義すべきです。
MCPサーバーを設定する必要があります。
使用前に設定を検証しなければなりません。
```

### Descriptionで3人称を使用

フロントマターのdescriptionは3人称を使用すること:

**正しい:**
```yaml
description: This skill should be used when the user asks to "create X", "configure Y"...
```

**間違い:**
```yaml
description: Use this skill when you want to create X...
description: Load this skill when user asks...
```

## バリデーションチェックリスト

スキルを最終確認する前に:

**構造:**
- [ ] 有効なYAMLフロントマターを持つSKILL.mdファイルが存在する
- [ ] フロントマターに`name`と`description`フィールドがある
- [ ] Markdown本文が存在して実質的な内容がある
- [ ] 参照されたファイルが実際に存在する

**Descriptionの品質:**
- [ ] 3人称を使用している（「This skill should be used when...」）
- [ ] ユーザーが言いそうな具体的なトリガーフレーズが含まれている
- [ ] 具体的なシナリオが一覧されている（「create X」「configure Y」）
- [ ] 曖昧または汎用的でない

**コンテンツの品質:**
- [ ] SKILL.md本文が命令形/不定詞形を使用している
- [ ] 本文がフォーカスされリーン（理想1,500〜2,000ワード、最大5,000）
- [ ] 詳細コンテンツがreferences/に移動されている
- [ ] 例が完全で機能している
- [ ] スクリプトが実行可能で文書化されている

**プログレッシブディスクロージャー:**
- [ ] コアコンセプトがSKILL.mdに
- [ ] 詳細ドキュメントがreferences/に
- [ ] 動作コードがexamples/に
- [ ] ユーティリティがscripts/に
- [ ] SKILL.mdがこれらのリソースを参照している

## よくある間違い

### 間違い1: 弱いトリガーdescription

❌ **悪い:**
```yaml
description: フックの操作に関するガイダンスを提供します。
```
曖昧、具体的なトリガーフレーズなし、3人称でない

✅ **良い:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events. Provides comprehensive hooks API guidance.
```

### 間違い2: SKILL.mdに内容を詰め込みすぎる

❌ **悪い:**
```
skill-name/
└── SKILL.md  (8,000ワード - 全てを1ファイルに)
```
スキルがロードされた時にコンテキストを肥大化させ、詳細コンテンツが常にロードされる

✅ **良い:**
```
skill-name/
├── SKILL.md  (1,800ワード - コアの本質)
└── references/
    ├── patterns.md (2,500ワード)
    └── advanced.md (3,700ワード)
```

### 間違い3: 2人称での文章

❌ **悪い:**
```markdown
まず設定ファイルを読む必要があります。
入力を検証すべきです。
grepツールを使って検索できます。
```

✅ **良い:**
```markdown
設定ファイルを読むことから始める。
処理前に入力を検証する。
パターンを検索するためにgrepツールを使用する。
```

## クイックリファレンス

### 最小限スキル

```
skill-name/
└── SKILL.md
```

### 標準スキル（推奨）

```
skill-name/
├── SKILL.md
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```

### 完全スキル

```
skill-name/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
├── examples/
│   ├── example1.sh
│   └── example2.json
└── scripts/
    └── validate.sh
```

## ベストプラクティスのまとめ

✅ **すること:**
- descriptionで3人称を使用する（「This skill should be used when...」）
- 具体的なトリガーフレーズを含める
- SKILL.mdをリーンに保つ（1,500〜2,000ワード）
- プログレッシブディスクロージャーを使用する（詳細はreferences/に）
- 命令形/不定詞形で書く
- サポートファイルを明確に参照する
- 動作する例を提供する
- 一般的な操作のためのユーティリティスクリプトを作成する

❌ **しないこと:**
- どこでも2人称を使用する
- 曖昧なトリガー条件を持つ
- 全てをSKILL.mdに入れる（references/なしで3,000ワード超）
- 2人称で書く（「You should...」）
- リソースを参照せずに放置する
- 壊れたまたは不完全な例を含める
- 検証をスキップする

## 実装ワークフロー

プラグインのスキルを作成するには:

1. **ユースケースを理解する**: スキル使用の具体的な例を特定する
2. **リソースを計画する**: 必要なスクリプト/references/examplesを決定する
3. **構造を作成する**: `mkdir -p skills/skill-name/{references,examples,scripts}`
4. **SKILL.mdを書く**:
   - トリガーフレーズを含む3人称descriptionのフロントマター
   - リーンな本文（1,500〜2,000ワード）を命令形で
   - サポートファイルを参照する
5. **リソースを追加する**: 必要に応じてreferences/、examples/、scripts/を作成
6. **検証する**: description、文章スタイル、整理を確認
7. **テストする**: 期待されるトリガーでスキルがロードされることを確認
8. **反復する**: 使用状況に基づいて改善する

強力なトリガーdescription、プログレッシブディスクロージャー、命令形の文章スタイルに集中して、必要な時にロードされ対象を絞ったガイダンスを提供する効果的なスキルを作成する。
