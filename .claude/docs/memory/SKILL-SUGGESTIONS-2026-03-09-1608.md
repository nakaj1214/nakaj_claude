---
tags: ['session', 'automation']
scope: session
date: 2026-03-09
---

# スキル候補レポート — 2026-03-09 16:08

## 検出されたパターン

- `create-proposal → create-plan → implement-plans` の連続実行フロー（毎回同じ順序で起動）
- `proposal.md` 作成後に要件の誤記を発見し手動修正するパターン（「列と行を間違えてました」→ Edit → 再確認）
- 実装完了後にブラウザ確認が必要な項目が手動リスト化される（「手動確認が必要な項目」セクション）
- `fix-escalation` 起動時に引数なし → 中断 → 引数付きで再起動する操作
- `excel_range_select_copy.js` の CSS specificity 競合問題（`!important` vs `#stock` 前置き）

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `quick-fix` | 「〜だけ直して」「実装完了した内容に追加で〜」「既存実装を〜に変更して」 | proposal/plan を省略し、変更箇所・Before/After・受入条件をその場で宣言してから即実装する軽量フロー。create-proposal→create-plan の省略版 | 高 |
| `verify-checklist` | 実装完了後、「確認してください」「動作確認お願い」「チェックリスト生成して」 | 実装したファイルの変更内容を走査し、ブラウザ/手動確認が必要な操作をチェックリスト形式で出力。antigravity でのスクリーンショット取得手順も付記 | 中 |
| `css-specificity-check` | 「背景色が上書きされる」「`!important` が効かない」「CSSが競合している」 | 対象セレクタの specificity を計算し、競合するルールを Grep で特定、勝てるセレクタを提案する | 中 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse (Write/Edit) | `docs/implement/proposal.md` が更新された直後 | proposal.md の品質チェック7項目を自動実行し、PASSなら「proposal.md 更新済 ✅」をコンソールに出力、FAILなら警告を表示する | 中 |
| PreToolUse (Skill:fix-escalation) | fix-escalation スキルが引数なしで起動されようとした場合 | 「どのバグについてですか？バグ名を引数で指定してください（例: `/fix-escalation セル選択の outline 問題`）」とインタラクティブに問い返す | 低 |

---

## 観察事項

- **`create-proposal` 中断・再実行**: ユーザーが proposal.md を IDE で開いてから要件訂正を口頭で伝えるパターンが2回発生。IDE のファイル開閉イベントに連動した「proposal.md レビューモード」への自動切替は有効かもしれないが、頻度が少ないため保留。
- **`selectColumn` の残骸**: 無効化後も関数が残存。`refactor-clean` スキルで未使用コードを除去する候補だが、「将来的に再有効化する可能性」との注記があるためスキル化より `TODO` コメント追加で対応するのが適切。
- **fix-escalation の新 issue 記録**: 「tr クリックの挙動が反映されない」は outline 問題とは別の新規 issue であり、fix-attempts.md に新セクションで記録する必要がある。自動的に分離記録するフックは有用だが、単発事象のため保留。