# Claude Template Sync — Instructions

## Overview

`.claude_remote/` (template repository) から `.claude/` (project config) へファイルを同期する。
改行コード差分・空白のみの変更を自動フィルタし、実質的な差分だけを適用する。

## Prerequisites

- `.claude_remote/` ディレクトリが存在すること
- `.claude/` ディレクトリが存在すること

## Sync Flow

### Step 1: Discover Changes

```bash
# List all files in template that differ from project
diff -rq .claude_remote/ .claude/ --exclude="*.jsonl" --exclude="memory" --exclude="plans" --exclude="settings.*"
```

除外対象:
- `memory/` — プロジェクト固有のセッション履歴
- `plans/` — 進行中の計画ファイル
- `settings.json` / `settings.local.json` — プロジェクト固有の設定
- `*.jsonl` — ログファイル

### Step 2: Filter Whitespace-Only Diffs

Each differing file must be checked for substantive changes:

```bash
# Normalize line endings and compare
diff <(tr -d '\r' < .claude_remote/path/to/file) <(tr -d '\r' < .claude/path/to/file)
```

- If the only differences are `\r\n` vs `\n` or trailing whitespace → **SKIP**
- If there are content differences → **INCLUDE** in sync list

### Step 3: Present Diff Summary

Show the user a summary table:

| File | Status | Action |
|------|--------|--------|
| `rules/coding-principles.md` | Modified | Update |
| `skills/new-skill/SKILL.md` | New | Add |
| `agents/old-agent.md` | Deleted in template | Confirm removal |

### Step 4: Apply Changes

For each file to sync:

1. **New files**: Copy from `.claude_remote/` to `.claude/`
2. **Modified files**: Replace `.claude/` version with `.claude_remote/` version
3. **Deleted files**: Ask user for confirmation before removing

### Step 5: Conflict Resolution

If a file has been modified in both `.claude_remote/` and `.claude/`:

1. Show both versions side by side
2. Ask user which to keep, or merge manually
3. Never silently overwrite local changes

## Rules

- **Never sync** `memory/`, `plans/`, `settings.json`, `settings.local.json`
- **Always ask** before deleting files that exist in `.claude/` but not in `.claude_remote/`
- **Report** the number of files synced, skipped (whitespace-only), and skipped (excluded)
