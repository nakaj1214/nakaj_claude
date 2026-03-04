# スキル候補レポート — 2026-03-03 16:52

## 検出されたパターン

- **Codex レビューループの反復実行**: `design.md` に対して Codex レビューを起動 → CHANGES_REQUIRED → Claude が Blocking 修正 → 再レビュー → APPROVED の流れが2イテレーション発生。同パターンは `create-plan` スキルにも埋め込まれていた（計3回の同一ループ構造）
- **APPROVED 後に Non-blocking 推奨を設計書へ反映**: APPROVED 判定後も「Non-blocking recommendations を設計書に取り込む」作業が毎回発生し、複数 Edit 操作が続く
- **Slack 通知の定型呼び出し**: `notify-slack.py` がレビューループ内で「開始・修正完了・APPROVED/CHANGES_REQUIRED」の3タイミングで繰り返し呼ばれた
- **テストスイートの雛形生成**: `conftest.py + unit/integration` の5ファイル構成が毎回同じ手順（mkdir → Write × 5 → pytest 実行）で作成される
- **Plan モード→ユーザー承認→実装開始** の3段階サイクルが2回（codex-review 抽出計画、Edit Self-Learning 実装計画）繰り返された

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `apply-nonblocking` | 「Non-blocking を反映して」「推奨事項を取り込んで」「レビューの提案を設計書に入れて」 | `review.md` から Non-blocking Recommendations を読み取り、対象ドキュメントへ自動 Edit するループ。APPROVED 後の後処理として `codex-review` の末尾から呼べるよう設計 | 高 |
| `scaffold-tests` | 「テストを作って」「テストスイートを作成」「pytest の雛形を用意」 | `conftest.py`・`tests/unit/__init__.py`・`tests/integration/__init__.py` の骨格を生成し、指定モジュールに対して `test_normal / test_error / test_edge` の AAA パターンテンプレートを出力。`importlib.util` による `.py` ハイフン名対応も含む | 高 |

---

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| `codex-reviewer` | `codex-review` スキルの内部 Task 呼び出しで毎回起動。「設計書を Codex でレビューして」 | 対象ファイル・チェックリスト・既存 `review.md` を受け取り、APPROVED / CHANGES_REQUIRED / BLOCKED の3判定と Blocking/Non-blocking 分類を構造化 JSON で返す。現状は自由文返却のためパース処理が Claude 側に依存している | 高 |
| `test-runner` | テスト作成後に自動起動。「テストを実行して」「pytest を走らせて」 | `uv run pytest tests/ -v` を実行し、失敗テストの差分と修正提案を返す。今回はテストデータが実装の正規表現と不一致で5件失敗し手動修正が必要だった。修正提案の自動化で手戻りを削減 | 中 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| `PostToolUse` | `Task` ツール呼び出し後、返答に `判定: APPROVED` が含まれる場合 | Slack に `✅ APPROVED — {target_file}` を通知し、`review.md` に最終判定タイムスタンプを書き込む。現在は Claude が毎回手動で `notify-slack.py` を呼んでいる | 中 |
| `PostToolUse` | `Write` ツールで `tests/unit/test_*.py` または `tests/integration/test_*.py` が作成された場合 | `uv run pytest {作成ファイル} -v` を自動実行して結果を `additionalContext` で返す。テスト作成直後に失敗があれば即座にフィードバック | 中 |

---

## 観察事項

- **Plan モード 2 回呼び出しパターン**: タスクが明確でも「小さな設計変更（スキル抽出）」と「大きな実装タスク」の両方でほぼ同じ Plan → 承認 → 実装 の流れを踏んでいる。頻度は高いが既に CLAUDE.md のワークフロー定義に組み込まれているため、追加の自動化は不要。
- **`edit-tracker.py` の正規表現とテストデータの不一致**: `sk-proj-...` のハイフン、`ghp_` の文字数など実装側の regex を参照せずにテストデータを書いたため5件失敗した。`scaffold-tests` スキルが実装ファイルを静的解析して正規表現定数を取り込む設計にすれば防げる。