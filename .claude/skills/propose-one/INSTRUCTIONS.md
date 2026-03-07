# 単一課題の計画実行 — 詳細手順

複数課題が prompt.md に並んでいるとき、1つだけ選んで確実に計画を立てる。
複数課題を同時進行させると混乱が生じるため、このスキルで1課題=1計画を強制する。

---

## Step 1: prompt.md を読んで課題を選択する

```
docs/implement/prompt.md を読む
```

- 課題が複数ある場合: リストアップして**どれを実施するかユーザーに確認する**（自動選択しない）
- 課題が1つのみの場合: そのまま進む
- ファイルが存在しない場合: 「prompt.md が見つかりません」と報告して終了

---

## Step 2: 選択課題のみで create-proposal を実行する

`create-proposal` スキルの INSTRUCTIONS.md を読み、以下の条件で実行する:

- **入力**: prompt.md の中から選択した1課題のみを対象にする
- **出力**: `docs/implement/proposal.md`（REQ-001 テンプレート形式）
- **品質チェック**: 7項目を通常通り実施する

### 重要なルール

- 選択した課題以外の要件を proposal.md に含めない
- 「ついでに〜も直す」は禁止
- prompt.md の他の課題は prompt.md に残したまま手をつけない

---

## Step 3: create-plan を実行する

`create-plan` スキルの INSTRUCTIONS.md を読み、通常通り実行する:

- **入力**: Step 2 で生成した `docs/implement/proposal.md`
- **品質ゲート**: proposal-quality-gate を通常通り実施
- **Codex レビュー**: 通常通り実施
- **出力**: `docs/implement/plan.md`

---

## Step 4: 停止してユーザーに確認

plan.md 生成後に**停止する**。実装は開始しない。

```
plan.md を作成しました。確認後、`/implement-plans` で実装を開始してください。
```

---

## ルール

- 選択した課題以外の変更を plan に含めない
- 「ついでに〜も直す」は禁止
- prompt.md の他の課題は `docs/implement/prompt.md` に残したまま手をつけない
- plan 生成後は自動実行しない（`/implement-plans` で明示的に実行）
- create-proposal と create-plan のテンプレート・品質チェックを省略しない
