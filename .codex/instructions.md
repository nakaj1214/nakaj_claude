# Codex Bridge Instructions

This file is generated from `.claude/` by `scripts/sync_claude_to_codex.py`.
The source of truth remains `.claude/`.

## Communication Defaults
- **Language**: Japanese for all user-facing communication
- **Detail level**: Concise — key points only, no verbose explanations
- **Confirmation**: Minimal — work autonomously and report results
- **Error reporting**: Always pair cause with proposed fix
- **Tech choices**: Prefer proven, stable technologies over bleeding-edge
- **Design approach**: Simplicity first — working solution before elegant solution
- **Risk tolerance**: Low — confirm before destructive or hard-to-reverse changes
- **Scope**: Do what was asked, no more — avoid over-engineering
- **Implementation**: Plan mode first → implement in separate session
- **Debugging**: Fix autonomously — no hand-holding needed
- **Review**: Show diff and confirm before applying
- **Session**: 1 session = 1 contract (clear completion condition)
- **Code explanation**: Comments in code are sufficient — skip long prose
- **Progress**: Summary on completion only — no mid-task updates unless blocked
- **Options**: Present 1 recommendation + brief rationale for alternatives
- **Questions**: Ask only when truly ambiguous — don't over-confirm
- Read `prompt.md` / `proposal.md` literally — "exists" means "remove it"
- "Not improved (Nth time)" = interpretation error, NOT complexity indicator
- APPROVED judgments are made by Codex only — Claude never self-approves
- Never change skill INSTRUCTIONS.md commands/models/params without asking

## Session Context Snapshot
### Project Profile
- **Repository**: nakaj_claude
- **Purpose**: Claude Code configuration and automation toolkit — skills, hooks, rules, agents を集約したメタプロジェクト
- **Owner**: nakashima
- **Windows**: `fcntl` unavailable — use `msvcrt` fallback
- **Windows**: Command line length limit ~32KB — use stdin for large payloads
- **Windows**: `claude -p` nesting — must unset `CLAUDECODE` env var

### Latest Handover
- file: `.claude/docs/memory/HANDOVER-2026-03-06-1613.md`
- **課題2** 列選択セル色分け / 修正済み、動作未確認 / ブラウザで列ヘッダークリックして `#e0e0e0` 確認
- **課題6** 入力セル背景色透明 / 未着手 / `/create-plan 課題6`

### Recent Lessons To Keep In Mind
- [2026-03-02] スキル指示のコマンド・モデル名を勝手に変えてはいけない
- [2026-03-04] 無効化されたフックのコマンドをスキルから実行してはいけない
- [2026-03-04] コード変更後に「改善されていない」と報告されたら実行パスを検証する
- [2026-03-04] prompt.md / proposal.md の日本語を文字通り読む

### Pending Materialize Queue
- pending entries: `8`
- if the user asks about Claude automation candidates, inspect `.claude/docs/memory/AUTO-MATERIALIZE-QUEUE.jsonl`

## Required Reading Order
1. `AGENTS.md`
2. `.claude/CLAUDE.md`
3. `.claude/docs/user-preferences.md`
4. `src/AGENTS.md` when touching `src/`
5. `.claude/docs/PROJECT-PROFILE.md` for non-trivial work
6. latest handover and recent lessons before large or risky edits

## Workflow Parity With Claude
- For tasks with 3 or more concrete steps, or when the scope is risky, write and maintain `tasks/todo.md`.
- Keep research/planning and implementation as separate phases when practical.
- Before claiming completion, run the relevant verification commands and inspect their output.
- If the user says the same issue still is not fixed, or says `N回目`, switch to the `fix-escalation` skill before another blind edit.
- Read `prompt.md` and `proposal.md` literally. Prefer the simplest direct fix before inventing deeper causes.
- Do not rewrite command names, model names, or parameters that are explicitly written in local skill instructions.
- Codex, not Claude, owns any `APPROVED` or `CHANGES_REQUIRED` judgment in this repository.

## Rule Routing
- Always consider:
  - `.claude/rules/language.md`
  - `.claude/rules/coding-principles.md`
  - `.claude/rules/security-rules.md`
  - `.claude/rules/neutral-analysis.md`
  - `.claude/rules/work-modes.md`
  - `.claude/rules/skill-execution.md`
  - `.claude/rules/common/git-workflow.md`
  - `.claude/rules/common/testing.md`
- For PHP / Laravel work, read:
  - `.claude/rules/project-conventions.md`
  - `.claude/rules/php/coding-style.md`
  - `.claude/rules/php/comments.md`
  - `.claude/rules/laravel/conventions.md`
  - `.claude/rules/laravel/architecture.md`
  - `.claude/rules/laravel/database.md`
  - `.claude/rules/laravel/frontend-integration.md`
- For JavaScript / CSS / Blade work, read:
  - `.claude/rules/project-conventions.md`
  - `.claude/rules/javascript/jquery-style.md`
  - `.claude/rules/javascript/naming-and-comments.md`
  - `.claude/rules/ui-fix-verification.md`

## Skill Bridge
- Repo-scoped skills are exposed through `.codex/skills/*`.
- Linked `.claude/skills/*`: `45`
- Linked `.claude/docs/references/**/SKILL.md`: `20`
- Generated `.claude/agents/*/*.md` bridges: `23`
- Use `.claude/registry/skills.yaml` as the index when you need Claude-style skill routing.

## Agent Bridge
- Use `claude-agent-router` when the user wants Claude-like subagent behavior or multi-role delegation.
- Planning agents: `architect`, `planner`
- Review agents: `code-reviewer`, `code-simplifier`, `database-reviewer`, `python-reviewer`, `security-reviewer`, `silent-failure-hunter`, `type-design-analyzer`
- Testing agents: `e2e-runner`, `pr-test-analyzer`, `tdd-guide`, `tester`
- Debugging agents: `build-error-resolver`, `debugger`, `performance`
- Codex native multi-agent is experimental. Default to role emulation plus parallel tool use unless native multi-agent is already available in the session.

## Command Bridge
- Claude slash commands are not native Codex commands.
- If the user mentions one of these command recipes, read the matching file under `.claude/commands/` and treat it as a workflow guide:
  `/build-fix`, `/cancel-ralph`, `/checkpoint`, `/clean_gone`, `/code-review`, `/commit-push-pr`, `/commit`, `/create-plugin`, `/e2e`, `/feature-dev`, `/hookify-configure`, `/hookify-help`, `/hookify-list`, `/hookify`, `/learn-edits`, `/materialize`, `/orchestrate`, `/ralph-help`, `/ralph-loop`, `/refactor-clean`, `/review-pr`, `/review-staged`, `/revise-claude-md`, `/test-coverage`, `/update-docs`, `/verify`
- The generic bridge skill is `claude-command-bridge`.
- Translate Claude-only concepts such as hooks, slash commands, `Task`, or `AskUserQuestion` into native Codex behavior.

## Hook Parity
- `.claude/hooks/*` do not auto-run in Codex. Emulate the important effects manually.
- After meaningful edits, consider whether `.claude/hooks/quality/post-implementation-review.py` would have asked for a review.
- After test failures, inspect output and summarize the failure pattern instead of claiming success.
- Before ending a long session, consider the `handover` skill and latest memory files.
- Disabled or commented-out hook workflows stay disabled. Do not execute Slack notification or approval helpers unless the user explicitly asks.

## MCP Bridge
- Default Codex MCP configuration lives in `.codex/config.toml`.
- It is generated from:
  - `.claude/mcp/settings-universal.json`
  - `.claude/mcp/settings-laravel-php.json`
  - `.claude/mcp/settings-javascript.json`
- Only enabled servers with repo-safe defaults are turned on by default.

## Unsupported Claude-only Features
- Slack approval / notification hooks remain documentation only.
- `.claude/commands/*` remain playbooks, not native CLI subcommands.
- Native Claude subagents are approximated with repo skills generated from `.claude/agents/*/*.md`.
