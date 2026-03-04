# Skill / Hook Execution Rules

Skills and hooks must be executed faithfully and context-aware.

## Never Alter Skill Instructions

- Commands, model names, and parameters in INSTRUCTIONS.md must be used verbatim
- "I don't recognize this value" is never a valid reason to change it
- If something seems wrong, ask the user — do not silently substitute

```
# ❌ Bad: changing model name because it's unfamiliar
codex exec --model o4-mini  # was gpt-5.3-codex in instructions

# ✅ Good: use exactly what's written
codex exec --model gpt-5.3-codex
```

## Skip Disabled Hooks

Before executing hook commands referenced in skill instructions:

1. Check `settings.json` for the hook configuration
2. If the hook is commented out or disabled, **skip the step silently**
3. Do not prompt the user for approval on disabled hooks

Disabled hook commands to skip:
- `notify-slack.py`
- `slack_approval.py`
- `edit-approval.py`
- `stop-notify.py`
