---
name: gemini-cli
description: Call Gemini CLI (Google) for analysis and implementation. 1M token large-scale context processing. Apache-2.0 license.
---

# Gemini CLI Skill

Skill for using Google Gemini CLI as a subagent. **Handles analysis and implementation** for problem identification and code generation.

## Role in Workflow

```
Gemini (Analysis) <- HERE
  -> Opus (Design)
  -> Codex (Review)
  -> Gemini (Implementation) <- HERE
  -> Codex (Review)
  -> Opus (Final judgment, when needed)
```

**Why Gemini handles analysis and implementation:**
- **Analysis**: Can focus on investigation and problem identification. Incorrect evaluation leads to workflow-wide rework, making dedicated analysis highly valuable
- **Implementation**: Handles iterative fixes to avoid Opus rate limits. Opus focuses only on "judgment-required parts"
- 1M token capacity allows understanding large codebases at once

## Model Characteristics

| Characteristic | Details |
|----------|---------|
| Base Model | Gemini 2.5 Pro |
| Context | **1M tokens** (10x+ other tools) |
| License | Apache-2.0 (Open Source) |
| GCP Integration | Vertex AI, BigQuery, Cloud Functions, etc. |
| Price | Free tier available / Google Cloud billing |

## When to Use

### Primary Role 1: Analysis (Workflow Start)

Use Gemini CLI for:

1. **Problem Analysis and Root Cause Identification**
   - Bug root cause identification
   - Error log analysis
   - Organizing reproduction conditions
   - Identifying impact scope

2. **Codebase Understanding**
   - Large codebase (entire monorepo) structure understanding
   - Multi-file relationship analysis
   - Dependency mapping
   - Investigating existing architecture

### Primary Role 2: Implementation (Workflow Middle/End)

3. **Code Implementation**
   - Implement based on finalized PATCH PLAN
   - Output in unified diff format
   - Minimal diff approach

4. **Implementation Fixes**
   - Fix Codex Must items only
   - Minimal changes, no unrelated formatting
   - Iterative fixes until Must = 0

### Secondary Role: Design Modification Support

5. **Design Modification Instructions** (when Must items remain after Codex review)
   - Create edit instructions based on Codex feedback
   - Organize before passing to Opus
   - KEEP/CHANGE/OPEN format

### Other Uses

6. **Large-Scale Refactoring**
   - Changes spanning many files
   - Legacy code renewal
   - Framework/language migration

7. **Google Cloud Integration**
   - Vertex AI, Cloud Functions
   - BigQuery, Google Sheets

## Usage

### Command Format

```bash
gemini "<request>"
```

### Main Options

| Option | Description |
|--------|-------------|
| `-m`, `--model` | Specify model (default: gemini-2.5-pro) |
| `--sandbox` | Sandbox mode |
| `-y`, `--yes` | Auto-approval mode |

---

## Analysis Tasks

### Input (What to pass to Gemini)

- Reproduction steps
- Error logs
- Related code (extract only relevant parts)
- Constraints (unchangeable scope, impact range, deadlines, etc.)

### Output Format (Fixed)

```markdown
## FACTS (Observed Facts)
- [Observed fact 1]
- [Observed fact 2]

## ROOT CAUSE candidates (up to 3 candidates)
1. [Candidate 1]: [Evidence]
2. [Candidate 2]: [Evidence]
3. [Candidate 3]: [Evidence]

## MIN TESTS (Minimal identification steps)
1. [Test 1]: [Expected result]
2. [Test 2]: [Expected result]

## RECOMMENDED FIX (Single recommended approach)
- [Recommended fix approach]
```

### Command Example

```bash
gemini "Analyze the following and output in FACTS/ROOT CAUSE/MIN TESTS/RECOMMENDED FIX format:

## Reproduction Steps
1. Open login screen
2. Enter correct credentials
3. Click login button
4. Error occurs

## Error Log
TypeError: Cannot read property 'token' of undefined

## Related Code
[Related code excerpt]

## Constraints
- Cannot change auth library
- Must fix this week"
```

---

## Implementation Tasks

### Input

- Finalized PATCH PLAN
- Codex Must items (if any)

### Output

- unified diff (recommended)
- Execution commands (test/static analysis)

### Implementation Rules

- **Minimal diff only**
- No unrelated formatting or renaming
- Leave TODO comments for unclear points
- Focus only on specified changes

### Command Example

```bash
gemini "Implement according to the following PATCH PLAN. Output in unified diff format:

## PATCH PLAN
- auth.service.ts: Fix token validation logic
  - Add error handling to validateToken()
  - Fix return type of refreshToken()
- error.handler.ts: Create new file
  - Define AuthError class
  - Implement handleAuthError()

## Must items (from design review)
- Return clear error message on token expiration

Rules:
- Minimal diff only
- No unrelated formatting
- Leave TODO for unclear points"
```

---

## Implementation Fix Loop

When Codex review returns Must items, use Gemini to fix iteratively:

### Input

- Codex Must items only
- Failing logs (if any)

### Output

- Minimal diff fix

### Command Example

```bash
gemini "Fix the following Must items from code review. Minimal diff only, no unrelated formatting:

## Must Items
1. [Must issue 1]: [Rationale] - [Acceptance criteria]
2. [Must issue 2]: [Rationale] - [Acceptance criteria]

## Failing Logs (if any)
[Test failure logs]

Output minimal diff to fix these issues only"
```

---

## Design Modification Support

When Must items remain after design review, have Gemini create edit instructions for Opus.

### Input

- Codex review results (Must/Should/Could)
- Current design (relevant parts only)

### Output Format

```markdown
## KEEP (Design elements to maintain)
- [Element to keep 1]

## CHANGE (Changes to make)
- [Specific diff instruction 1]
- [Specific diff instruction 2]

## OPEN (Points requiring additional information)
- [Question 1]

## Acceptance Criteria
- [ ] [Criteria 1]
- [ ] [Criteria 2]
```

### Command Example

```bash
gemini "Based on the following Codex review results, create design edit instructions:

## Codex Review Results
### Must
- [Issue content]

## Current Design
[DECISIONS + PATCH PLAN]

Output in KEEP/CHANGE/OPEN/Acceptance Criteria format"
```

---

## Use Cases

### Example 1: Analysis Phase

**Request:**
```
Analyze this authentication bug
```

**Execute:**
```bash
gemini "Analyze the following and output in FACTS/ROOT CAUSE/MIN TESTS/RECOMMENDED FIX format:
[Problem details with reproduction steps and error logs]"
```

### Example 2: Implementation Phase

**Request:**
```
Implement the approved design
```

**Execute:**
```bash
gemini "Implement according to the following PATCH PLAN. Output in unified diff format:
[Finalized PATCH PLAN]

Rules:
- Minimal diff only
- No unrelated formatting
- Leave TODO for unclear points"
```

### Example 3: Implementation Fix

**Request:**
```
Fix the issues from code review
```

**Execute:**
```bash
gemini "Fix the following Must items from code review. Minimal diff only:
[Codex Must items]"
```

### Example 4: Large-Scale Refactoring

**Request:**
```
Migrate entire project from CommonJS to ESModules
```

**Execute:**
```bash
gemini "Migrate this project from CommonJS to ESModules. Convert require() to import and update package.json"
```

## Tasks Gemini Excels At

| Category | Specific Tasks |
|----------|----------------|
| Analysis | Problem identification, root cause analysis, codebase understanding |
| Implementation | PATCH PLAN-based code generation, iterative fixes |
| Refactoring | Large-scale structural changes, code style unification |
| Migration | Language version updates, framework migration |
| GCP | Cloud Functions, Vertex AI, BigQuery |

## Leveraging 1M Token Context

Gemini's greatest strength is its 1M token super-large context:

```bash
# Batch process all files
gemini "Analyze dependencies across this entire monorepo (100+ files)"

# Analyze lengthy logs
gemini "Analyze past week's logs and identify error patterns"

# Implement across many files
gemini "Implement this feature across all affected files in the monorepo"
```

## When to Use Claude Code (Opus) Instead

Use Claude Code for:
- **Design phase**: Creating DECISIONS, PATCH PLAN, TEST PLAN
- **Final judgment**: When Must items persist after 2 rounds
- **Design reconstruction**: When approach change or requirement reinterpretation needed
- **High-risk decisions**: Security, data corruption, permissions

## Important Notes

- Focus on minimal diffs for implementation
- No unrelated formatting or renaming
- Leave TODO comments for uncertainties
- Apply large-scale changes incrementally
- Always run tests after changes

## Related Skills

- [ai-cli-selector](ai-cli-selector.md): Tool selection and overall flow
- [codex-cli](codex-cli.md): Review role
