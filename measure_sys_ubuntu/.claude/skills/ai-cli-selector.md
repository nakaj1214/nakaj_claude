---
name: ai-cli-selector
description: Guide for selecting optimal AI CLI tools. Role distribution for Analysis/Design/Review/Implementation to minimize calls and maximize results.
---

# AI CLI Tool Selection Guide

Guide for optimal use of AI CLI tools through **Analysis → Design → Design Review → Implementation → Implementation Review** workflow with minimal calls and maximum results.

**Premise:** Operate with **Gemini / Codex / Opus** only (OpenCode NOT used).

---

## Recommended Role Distribution

| Phase | Tool | Purpose |
|-------|------|---------|
| **Analysis** | Gemini CLI | Investigation and identification. Incorrect evaluation causes rework |
| **Design** | Claude Code (Opus) | Decision-making, minimal diff planning |
| **Design Review** | Codex CLI | Risk identification, spec gaps, test perspectives |
| **Implementation** | Gemini CLI | Code implementation based on finalized plan |
| **Implementation Review** | Codex CLI | Diff review, improvement suggestions |
| **Final Judgment** | Claude Code (Opus) | Only when needed for design reconstruction |

**Goal:** Focus **Opus on "judgment-required parts"**, handle iterative fixes with **Gemini** to avoid rate limits.

---

## Key Rules (Core of Operations)

### Rule 1: Pass only "3-piece set"

Avoid sharing full text. Share only these 3 items between phases:

- **FACTS**: Observed facts (logs/reproduction/relevant code)
- **DECISIONS**: Decisions made (change/no-change, assumptions)
- **PLAN**: Diff plan (PATCH PLAN for design, diff for implementation)

### Rule 2: Codex review must use "Must/Should/Could" + "Rationale" + "Acceptance Criteria"

Enforce the following output from Codex:

- **Must**: Critical/dangerous if left unfixed (required)
- **Should**: Recommended improvements
- **Could**: Optional preferences
- Must items must include:
  - **Rationale** (what breaks and how)
  - **Acceptance Criteria** (what needs to be satisfied)

---

## Minimal Round-Trip Flow (Recommended)

### 0) Gemini: Analysis (1 call)

**Output Format (Fixed):**
```markdown
## FACTS
- ...

## ROOT CAUSE candidates (max 3)
1. ...
2. ...
3. ...

## MIN TESTS (Identification steps)
1. ...

## RECOMMENDED FIX (Single approach)
- ...
```

**Command:**
```bash
gemini "Analyze the following and output in FACTS/ROOT CAUSE/MIN TESTS/RECOMMENDED FIX format:
[Problem description]"
```

---

## Design Phase (Loop until Must = 0)

### 1) Opus: Design (1 call)

**Output Format (Fixed):**
```markdown
## DECISIONS
- ...

## PATCH PLAN (By file)
- file1.ts: [Changes]
- file2.ts: [Changes]

## TEST PLAN
- ...

## RISKS (Max 5)
1. [Risk] - [Mitigation]

## Acceptance Criteria
- [ ] ...
```

### 2) Codex: Design Review (1 call)

**Input:** DECISIONS + PATCH PLAN + TEST PLAN (full code NOT needed)

**Output Format:**
```markdown
## Must (Critical, required fixes)
- [Issue]: [Rationale] - [Acceptance criteria]

## Should (Recommended improvements)
- ...

## Could (Optional)
- ...

## Additional Test Perspectives
- ...
```

**Command:**
```bash
codex exec --full-auto --sandbox read-only --cd . "Review the following design and output in Must/Should/Could format. Must items require rationale and acceptance criteria:

## DECISIONS
[...]

## PATCH PLAN
[...]

## TEST PLAN
[...]"
```

### 3) Loop "Opus fix → Codex re-review" until Must = 0

- **Opus fix**: Reflect Codex **Must only**, update design parts (DECISIONS/PATCH PLAN/TEST PLAN) with minimal diff
- **Codex re-review**: Re-review updated design only (design phase complete when Must = 0)

#### Gate: When to use Opus for design phase fixes

Use Opus only when any of these apply:

- Must items **remain after 2 rounds**
- Feedback requires "approach change" or "requirement reinterpretation"
- Impact scope expands, requiring full design reconstruction
- High-risk judgment needed (security/data corruption/permissions)

---

## Implementation Phase

### 4) Gemini: Implementation (1 call)

**Input:**
- Finalized PATCH PLAN
- Codex design review Must items (if any)

**Output:**
- unified diff (recommended) + execution commands (test/static analysis)

**Command:**
```bash
gemini "Implement according to the following PATCH PLAN. Output in unified diff format:

## PATCH PLAN
[...]

## Must items (from design review)
[...]

Rules:
- Minimal diff only
- No unrelated formatting
- Leave TODO for unclear points"
```

### 5) Codex: Implementation Review (1 call)

**Input:**
- diff + requirements + constraints

**Output:**
- Must/Should/Could (Must includes rationale + acceptance criteria)

**Command:**
```bash
codex exec --full-auto --sandbox read-only --cd . "Review the following diff and output in Must/Should/Could format:

## diff
[unified diff]

## Requirements
[...]

## Constraints
[...]"
```

### 6) Loop "Gemini fix → Codex re-review" until Must = 0

- **Gemini fix**: Fix Must only (minimal diff, no unrelated formatting)
- **Codex re-review**: Re-review diff (complete when Must = 0)

#### Gate: When to use Opus for implementation fixes

- Must items **remain after 2 rounds**
- Fix requires changing design DECISIONS itself
- High-risk judgment involved (security/destructive changes)

---

## Copy-Paste Templates

### Gemini (Analysis)
```
INPUT: Reproduction steps + error logs + related code + constraints
OUTPUT: FACTS / ROOT CAUSE / MIN TESTS / RECOMMENDED FIX
```

### Opus (Design)
```
INPUT: Gemini analysis (FACTS + RECOMMENDED FIX)
OUTPUT: DECISIONS / PATCH PLAN / TEST PLAN / RISKS / Acceptance Criteria
```

### Codex (Design Review)
```
INPUT: DECISIONS + PATCH PLAN + TEST PLAN
OUTPUT: Must/Should/Could + (Must requires rationale and acceptance criteria)
```

### Gemini (Design Fix)
```
INPUT: Codex Must only
OUTPUT: Updated DECISIONS/PATCH PLAN/TEST PLAN (minimal edits)
```

### Gemini (Implementation)
```
INPUT: Final PATCH PLAN + Must only
OUTPUT: unified diff + commands
```

### Codex (Implementation Review)
```
INPUT: diff + requirements + constraints
OUTPUT: Must/Should/Could + acceptance criteria
```

### Gemini (Implementation Fix)
```
INPUT: Codex Must only + failing logs (if any)
OUTPUT: minimal diff fix
```

---

## Checkpoints (Completion Criteria)

- Design review **Must = 0**
- Implementation review **Must = 0**
- Acceptance Criteria satisfied

---

## Command Reference

| Tool | Command |
|------|---------|
| Claude Code (Opus) | Current session |
| Gemini CLI | `gemini "<request>"` |
| Codex CLI | `codex exec --full-auto --sandbox read-only --cd . "<request>"` |

## Related Skills

- [gemini-cli](gemini-cli.md): Analysis and implementation tool details
- [codex-cli](codex-cli.md): Review tool details
