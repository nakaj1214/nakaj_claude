---
name: init
description: プロジェクト構造を分析し、検出した技術スタック・コマンド・設定でAGENTS.mdを更新する。
disable-model-invocation: true
---

# プロジェクト設定を初期化する

このプロジェクトを分析して、AGENTS.md の**プロジェクト固有のセクションのみ**を更新する。

## 重要

- 既存のAGENTS.mdの「Extensions」セクション以降は**変更しない**
- 先頭のプロジェクト固有セクションのみ更新する

## ステップ

### 1. プロジェクトを分析する

技術スタックを特定するために以下のファイルを探す:

- `package.json` → Node.js/TypeScriptプロジェクト
- `pyproject.toml` / `setup.py` / `requirements.txt` → Pythonプロジェクト
- `Cargo.toml` → Rustプロジェクト
- `go.mod` → Goプロジェクト
- `Makefile` / `Dockerfile` → ビルド/デプロイ設定
- `.github/workflows/` → CI/CD設定

また以下も検出する:

- npmスクリプト / poeタスク / makeターゲット → よく使うコマンド
- 主要ライブラリ/フレームワーク

### 2. ユーザーに質問する

AskUserQuestionツールを使って以下を質問する:

1. **プロジェクト概要**: このプロジェクトは何をするか？（1〜2文で）
2. **コード言語**: コメント/変数名は英語か日本語か？
3. **追加ルール**: 他に従うべきコーディング規約はあるか？

### 3. AGENTS.mdを部分的に更新する

Editツールを使って先頭セクション（最初の `---` まで）のみを以下の形式で更新する:

```markdown
# Project Overview

{ユーザーの回答}

## Language Settings

- **Thinking/Reasoning**: English
- **Code**: {分析に基づく - 英語または日本語}
- **User Communication**: Japanese

## Tech Stack

- **Language**: {検出した言語}
- **Package Manager**: {検出したツール}
- **Dev Tools**: {検出したツール}
- **Main Libraries**: {検出したライブラリ}
```

### 4. よく使うコマンドを更新する

`## Common Commands` セクションを検出したコマンドで更新する:

```markdown
## Common Commands

```bash
# 検出したコマンド（例）
{npm run dev / poe test / make build など}
```
```

### 5. 不要なルールを確認する

`.claude/rules/` のルールを確認して、不要なものを提案する:

- Pythonでないプロジェクト → `dev-environment.md`（uv/ruff/ty）が不要な可能性あり
- テストなしプロジェクト → `testing.md` が不要な可能性あり

### 6. 完了を報告する

ユーザーに日本語で報告する:

- 検出した技術スタック
- 更新したセクション
- 削除を推奨するルール（あれば）
