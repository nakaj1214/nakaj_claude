---
description: "アクティブな Ralph ループをキャンセルする"
allowed-tools: ["Bash(test -f .claude/ralph-loop.local.md:*)", "Bash(rm .claude/ralph-loop.local.md)", "Read(.claude/ralph-loop.local.md)"]
hide-from-slash-command-tool: "true"
---

# Ralph のキャンセル

Ralph ループをキャンセルするには:

1. `.claude/ralph-loop.local.md` が存在するか Bash で確認する: `test -f .claude/ralph-loop.local.md && echo "EXISTS" || echo "NOT_FOUND"`

2. **NOT_FOUND の場合**: 「アクティブな Ralph ループは見つかりませんでした。」と表示する

3. **EXISTS の場合**:
   - `.claude/ralph-loop.local.md` を読み取り、`iteration:` フィールドから現在のイテレーション番号を取得する
   - Bash でファイルを削除する: `rm .claude/ralph-loop.local.md`
   - 報告する: 「Ralph ループをキャンセルしました（イテレーション N 回目でした）」（N はイテレーションの値）
