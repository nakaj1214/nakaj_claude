# フックデバッグ — 詳細手順

Claude Code フックが期待通り動かないときに、体系的に問題を特定・解決する。

---

## 4ステップ診断フロー

```
Step 1: settings.json の登録確認
Step 2: スクリプト単体テスト（echo + pipe）
Step 3: Python import / 依存関係チェック
Step 4: 出力フォーマット検証
```

---

## Step 1: settings.json の登録確認

```bash
# settings.json を読んでフック登録を確認
cat .claude/settings.json | python3 -c "
import json, sys
settings = json.load(sys.stdin)
hooks = settings.get('hooks', {})
for event, entries in hooks.items():
    for entry in entries:
        matcher = entry.get('matcher', '(all)')
        for h in entry.get('hooks', []):
            cmd = h.get('command', '')
            timeout = h.get('timeout', 'default')
            print(f'  {event} [{matcher}] timeout={timeout}')
            print(f'    → {cmd}')
"
```

**確認ポイント:**
- フックが正しいイベント（`PreToolUse` / `PostToolUse` / `PreCompact` / `Stop`）に登録されているか
- `matcher` が対象ツール名に一致しているか（`Edit|Write`、`Bash` など）
- `command` のパスが正しいか（`$(git rev-parse --show-toplevel)` を使っていれば OK）
- `timeout` が十分か（重い処理は 30 秒以上必要な場合あり）

---

## Step 2: スクリプト単体テスト

フックは stdin から JSON を受け取り、stdout に JSON を出力する。手動で実行して確認する。

### PreToolUse フックのテスト

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"test.py","old_string":"a","new_string":"b"}}' | \
  python3 .claude/hooks/{対象スクリプト}.py
```

### PostToolUse フックのテスト

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"test.py","old_string":"a","new_string":"b"},"tool_result":{"success":true}}' | \
  python3 .claude/hooks/{対象スクリプト}.py
```

### PreCompact フックのテスト

```bash
echo '{}' | python3 .claude/hooks/{対象スクリプト}.py
```

**確認ポイント:**
- エラーなく終了するか（`echo $?` で終了コード確認）
- stdout に有効な JSON が出力されるか
- stderr にエラーメッセージがないか

---

## Step 3: Python import / 依存関係チェック

```bash
# import エラーの確認
python3 -c "import sys; sys.path.insert(0, '.claude/hooks'); exec(open('.claude/hooks/{対象スクリプト}.py').read())" 2>&1 | head -20

# lib/ のモジュールが import できるか
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from lib.jsonl_io import append_jsonl
from lib.claude_p import parse_hook_input
print('All imports OK')
"
```

**よくある import エラー:**

| エラー | 原因 | 対処 |
|--------|------|------|
| `ModuleNotFoundError: No module named 'lib'` | `sys.path` に hooks ディレクトリが含まれていない | スクリプト冒頭で `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` |
| `ModuleNotFoundError: No module named 'slack_sdk'` | 外部パッケージ未インストール | `pip install slack_sdk` |
| `ImportError: cannot import name 'xxx'` | lib/ のモジュールにその関数がない | lib/ のソースを確認 |

---

## Step 4: 出力フォーマット検証

フックの出力が正しい JSON フォーマットか確認する。

### PreToolUse フックの出力フォーマット

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "ユーザーに表示するメッセージ"
  }
}
```

ブロックする場合:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "decision": "block",
    "reason": "ブロック理由"
  }
}
```

### PostToolUse フックの出力フォーマット

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "追加コンテキスト情報"
  }
}
```

**確認ポイント:**
- `print()` で JSON 以外のテキストを stdout に出していないか（`stderr` を使うべき）
- `hookEventName` が正しいか
- JSON が valid か（`| python3 -m json.tool` でチェック）

---

## よくある問題と対処

### 1. フックが無視される（実行されない）

```bash
# matcher が一致しているか確認
# 例: "Edit|Write" は Edit と Write にマッチ
# 例: "" は全ツールにマッチ
# 例: "Bash" は Bash のみにマッチ
```

**対処:** settings.json の `matcher` を確認。ツール名は正確に一致させる。

### 2. タイムアウトで失敗する

```bash
# スクリプトの実行時間を計測
time echo '{}' | python3 .claude/hooks/{対象スクリプト}.py
```

**対処:** `timeout` 値を増やすか、スクリプトを高速化する。

### 3. 権限エラー

```bash
# 実行権限を確認
ls -la .claude/hooks/{対象スクリプト}.py

# 必要なら権限を付与
chmod +x .claude/hooks/{対象スクリプト}.py
```

### 4. stdout に JSON 以外が混ざる

```bash
# 出力が valid JSON か確認
echo '{"tool_name":"Edit","tool_input":{}}' | \
  python3 .claude/hooks/{対象スクリプト}.py | python3 -m json.tool
```

**対処:** デバッグ出力は `print(..., file=sys.stderr)` を使う。`stdout` は JSON 出力のみにする。

### 5. skill-execution ルールでスキップ対象

`.claude/rules/skill-execution.md` にスキップ対象として記載されているフックは実行されない:
- `notify-slack.py`
- `slack_approval.py`
- `edit-approval.py`
- `stop-notify.py`

---

## デバッグ完了チェックリスト

- [ ] settings.json にフックが正しく登録されている
- [ ] `echo '...' | python3 hook.py` で単体実行できる
- [ ] import エラーがない
- [ ] stdout に valid JSON のみ出力される
- [ ] timeout 内に処理が完了する
- [ ] matcher が正しいツール名に一致する
