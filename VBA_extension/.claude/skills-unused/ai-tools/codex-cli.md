---
name: codex-cli
description: Call Codex CLI (OpenAI) for design review. Must/Should/Could format for risk identification. GPT-5-Codex based.
---

# Codex CLI Skill

Skill for using OpenAI Codex CLI as a subagent. **Handles review** specialized for design validation and risk identification.

## Role in Workflow

```
Gemini (Analysis)
  -> Opus (Design)
  -> Codex (Design Review) <- HERE
  -> Gemini (Implementation)
  -> Codex (Implementation Review) <- HERE
  -> Opus (Final judgment, when needed)
```

**Why Codex handles review:**
- Strong diff review capability (issue identification, prioritization)
- Separating reviewer from implementer avoids "self-affirming reviews"
- Must/Should/Could format provides clear prioritization
- Familiar with GitHub-integrated PR reviews

## Model Characteristics

| Characteristic | Details |
|----------|---------|
| Base Model | GPT-5-Codex (specialized in software engineering) |
| Strength | Diff review and prioritization |
| GitHub Integration | Native integration (PR review, Issue creation) |
| Price | Included in ChatGPT Plus (no additional cost) |

## When to Use

### Primary Role: Review (Mid-Workflow)

Use Codex CLI for:

1. **Design Review**
   - Evaluate Opus design with Must/Should/Could
   - Risk identification and spec gap detection
   - Propose additional test perspectives

2. **Implementation Review**
   - Diff-based code review
   - Improvement suggestions
   - Security perspective verification

### Secondary Role: GitHub Integration and Prototyping

3. **GitHub Integration Tasks**
   - Auto-generate Issues/PRs
   - Create commit messages
   - GitHub Actions configuration

4. **Frontend Prototyping**
   - Quick UI/UX prototypes
   - React component scaffolding

## Usage

### Command Format

```bash
codex exec --full-auto --sandbox read-only --cd <project_directory> "<request>"
```

### Option Descriptions

| Option | Description |
|--------|-------------|
| `--full-auto` | Full auto (execute without confirmation) |
| `--sandbox read-only` | Read-only sandbox |
| `--sandbox write` | Writable sandbox |
| `--cd <dir>` | Specify working directory |

---

## Executing Design Review

### Input (What to pass to Codex)

- Opus DECISIONS + PATCH PLAN + TEST PLAN

**Important:** Don't pass full code for design review. **Plans only** are sufficient.

### Output Format (Fixed)

```markdown
## Must (Critical, required fixes)
- [Issue]: [Rationale] - [Acceptance criteria]

## Should (Recommended improvements)
- [Issue]: [Reason]

## Could (Preference, optional)
- [Issue]

## Additional Test Perspectives
- [Test perspective 1]
- [Test perspective 2]
```

**Rules:**
- **Must** items must include "rationale" and "acceptance criteria"
- This clarifies "how much to fix" and "fix completion criteria"

### Command Example

```bash
codex exec --full-auto --sandbox read-only --cd . "Review the following design and output in Must/Should/Could format. Must items require rationale and acceptance criteria:

## DECISIONS
- Auth method: Continue with JWT
- Session management: No changes
- Error handling: Fix

## PATCH PLAN
- auth.service.ts: Fix token validation logic
- error.handler.ts: Add
- user.controller.ts: Integrate error handling

## TEST PLAN
- auth.service.test.ts: Add token validation tests
- e2e/auth.test.ts: Update E2E tests"
```

---

## Executing Implementation Review

### Input

- Diff + spec + known constraints

### Command Example

```bash
codex exec --full-auto --sandbox read-only --cd . "Review the following diff and output in Must/Should/Could format:

## diff
[unified diff]

## Spec
[Purpose of changes]

## Constraints
[Known constraints]"
```

---

## Other Uses

### GitHub Issue Creation

```bash
codex exec --full-auto --sandbox write --cd "C:\project" "Create a GitHub Issue for this bug: Error occurs during login"
```

### React Component Prototype

```bash
codex exec --full-auto --sandbox write --cd "C:\project" "Create a React component to display user list. Match existing code style"
```

## Use Cases

### Example 1: GitHub Issue Creation

**Request:**
```
Create a GitHub Issue for this bug
```

**Execute:**
```bash
codex exec --full-auto --sandbox write --cd "C:\project" "Create a GitHub Issue for this bug: Error occurs during login"
```

### Example 2: React Component Prototype

**Request:**
```
Quickly create a React component to display user list
```

**Execute:**
```bash
codex exec --full-auto --sandbox write --cd "C:\project" "Create a React component to display user list. Match existing code style"
```

### Example 3: Code Review Support

**Request:**
```
Review recent changes
```

**Execute:**
```bash
codex exec --full-auto --sandbox read-only --cd "C:\project" "Review recent commits and identify improvements"
```

## Tasks Codex Excels At

| Category | Specific Tasks |
|----------|----------------|
| GitHub | Issue creation, PR descriptions, review comments |
| Frontend | React/Vue/Angular component creation |
| Prototype | Quick working mock implementations |
| Documentation | README, API documentation generation |
| Testing | Unit test scaffolding |

## When to Use Claude Code Instead

Use Claude Code for:
- Complex edits spanning multiple files
- Security-critical code
- Long-term investigation/analysis
- Final implementation for production

## Important Notes

- Monitor progress for long-running executions
- Don't pass sensitive information
- Always review results
- Choose appropriate sandbox mode

## Related Skills

- [ai-cli-selector](ai-cli-selector.md): Tool selection and overall flow
- [gemini-cli](gemini-cli.md): Analysis and implementation role
