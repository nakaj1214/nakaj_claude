# スキル候補レポート — 2026-03-05 00:12

## 検出されたパターン

- `create-plan` を2回実行し、毎回 proposal.md 品質チェック→コードベース調査→plan.md 作成の一連フローを繰り返した
- hooks/ フォルダ再編後、全スクリプトのパス参照（`sys.path.insert`, `_HOOKS_DIR`, `_BASE`）を手動で修正した（5ファイル×同一パターン）
- Windows環境で `fcntl`, `claude` PATH, コマンドライン長制限の問題が連続して発生し、その都度手動デバッグした
- settings.json のフックパス・パーミッション変更が複数回発生し、JSONパース検証を手動実行した
- ファイル参照更新（proposal.md → prompt.md）が10ファイル分発生し、Grep → 一括Edit のフローを繰り返した
- `File has not been read yet` エラーが3回発生（plan.md, ui-fix-verification.md, slack_approval.py）

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `hooks-path-update` | 「hooksのパスを更新して」「フックをフォルダ移動した後に更新」「hook内のsys.path修正」 | hooks/ 内の全Pythonスクリプトをスキャンし、`sys.path.insert(0, ...)` と `_BASE` パターンを新フォルダ構造に合わせて一括修正する。settings.jsonのフックパスも同時更新。 | 高 |
| `windows-compat-check` | 「Windowsで動かない」「WSLとの互換性」「fcntlエラー」「コマンドライン長」「PATHが通らない」 | Pythonスクリプトを走査し、`import fcntl` / `import resource` 等のUnix専用モジュールを検出し、`sys.platform` 分岐でWindowsフォールバックを追加する。`subprocess` でCLIを呼ぶ箇所でコマンドライン長問題がないか確認し、stdin経由への変換を提案する。 | 高 |
| `settings-hooks-register` | 「settings.jsonにフックを登録して」「hookを有効化して」「PreToolUseを追加して」 | settings.json を読み込み、指定したスクリプトを適切なフックイベント（PreToolUse/PostToolUse/Stop/PreCompact）とmatcherで登録する。JSONパース検証付き。 | 中 |
| `file-ref-rename` | 「〇〇.mdを読み込んでいるファイルを全部更新して」「ファイル名変更に伴う参照更新」 | Grep で対象ファイル名の参照を全文検索し、ヒットしたファイルをリストアップ後、一括置換する。SKILL.md, INSTRUCTIONS.md, registry/skills.yaml, rules/*.md, docs/ を優先的に確認。 | 中 |

---

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| `hook-tester` | フックスクリプトが実際に発火するか検証したいとき | hooks/ 内の指定スクリプトを、実際のClaude Codeフック入力JSONをstdinで渡して実行し、終了コード・stdout・stderrを確認する。Windows環境では `CLAUDECODE=` を除去してから実行する。 | 高 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse (Write/Edit) | `settings.json` が更新されたとき | `python3 -c "import json; json.load(open('settings.json'))"` でJSONパースを自動検証し、失敗時にエラーを出力する | 高 |
| PostToolUse (Bash) | `git mv` コマンド実行後 | 移動されたファイルが settings.json に登録されていれば警告（「パスが壊れます。settings.jsonを更新してください」） | 中 |

---

## 観察事項

- `create-plan` 実行時に Codex レビューの Task エージェントが `implement-plans` スキルを誤トリガーした（1回）。スキルの description に「Codex レビューループではなく計画書作成のみを担当」と明記して再発を防止済み。
- `File has not been read yet` エラーが3回発生。現状の自動化よりも、エラー発生後の自動リカバリ（Read → retry Edit）の方が効果的。
- `pre-compact-handover.py` のデバッグでWindowsのPATH, fcntl, stdin渡し問題が連鎖的に発生した。これらは独立した問題ではなく「Windows上でUnix向けスクリプトを動かす」という共通問題であるため、`windows-compat-check` スキルで包括的に対処するのが有効。