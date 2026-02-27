---
name: opencode-glm
description: Call OpenCode + GLM-4.7 for implementation drafts. Low-cost bulk implementation processing. 200K context.
---

# OpenCode + GLM-4.7 Skill

> **⚠️ NOT PART OF RECOMMENDED WORKFLOW**
>
> This skill is **NOT** part of the recommended workflow. The recommended workflow uses **Gemini / Codex / Opus only** as defined in [ai-cli-selector](ai-cli-selector.md).
>
> This file is disabled (underscore prefix) and kept only for reference or alternative use cases.

Skill for using OpenCode CLI and GLM-4.7 model as a subagent. **Handles implementation drafts** processing large-scale implementations at low cost.

## Role in Workflow

```
Gemini (Analysis)
  -> Opus (Design)
  -> Codex (Review)
  -> GLM (Implementation Draft) <- HERE
  -> Opus (Final Polish)
```

**Why GLM handles implementation drafts:**
- Handles "bulk implementation" tasks (file splitting, replacement, type alignment, peripheral fixes, etc.)
- Opus focuses only on "judgment-required parts", reducing token consumption
- Enables low-cost trial and error

## When to Use

### Primary Role: Implementation Draft (Late Workflow)

Use OpenCode + GLM-4.7 for:

1. **PATCH PLAN-based Implementation**
   - Code implementation following design
   - Output in unified diff format
   - Minimal diffs

2. **Bulk Implementation Tasks**
   - File splitting/replacement
   - Type alignment/peripheral fixes
   - Boilerplate generation

### Secondary Role: Low-Cost Bulk Processing

3. **Routine Bulk Execution**
   - Batch lint/format fixes
   - Test fix loops
   - Import organization

4. **Exploratory Coding**
   - Tasks requiring much trial and error
   - Rapid prototyping

## Usage

### Command Format

```bash
opencode "<request>"
```

### TUI Mode (Interactive)

```bash
opencode
# Interactive chat UI
```

### Main Options

| Option | Description |
|--------|-------------|
| `--model` | Specify model (GLM-4.7, etc.) |
| `--provider` | Specify provider |
| `-y`, `--yes` | Auto-approval mode |

---

## Executing Implementation Drafts

### Input (What to pass to GLM)

- Finalized PATCH PLAN
- Codex Must items only

### Output

- **unified diff** (diff format) recommended
- Or "file-wise changes + modified code"

### Implementation Rules (Important)

| Rule | Description |
|------|-------------|
| **Minimal diff** | Only necessary changes |
| **No formatting** | No unrelated formatting changes |
| **No renaming** | No unrelated renaming |
| **Leave TODOs** | For unclear points, leave TODO comments and proceed |

### Prohibited Actions

| NG | Reason |
|----|--------|
| Unrelated file changes | Complicates Opus final polish |
| Large-scale rename/format | Diff becomes hard to read |
| Adding abstraction | New layers/patterns are design work |
| Extending beyond spec | Only implement what's specified |

### Command Example

```bash
opencode "Implement according to the following PATCH PLAN. Minimize diffs and output in unified diff format:

## PATCH PLAN
- auth.service.ts: Fix token validation logic
  - Add error handling to validateToken()
  - Fix return type of refreshToken()
- error.handler.ts: Create new file
  - Define AuthError class
  - Implement handleAuthError()

## Must (Required fixes)
- Return clear error message on token expiration

Leave TODO comments for unclear points"
```

---

## Other Uses

### Batch lint/format fixes

```bash
opencode "Auto-fix all TypeScript ESLint errors and list ones that can't be auto-fixed"
```

### Test-driven fixes

```bash
opencode "Run npm test, fix failing tests, and repeat until all tests pass"
```

## Use Cases

### Example 1: Batch lint fixes

**Request:**
```
Fix all lint errors in the project
```

**Execute:**
```bash
opencode "Auto-fix all TypeScript ESLint errors and list ones that can't be auto-fixed"
```

### Example 2: Test-driven fixes

**Request:**
```
Keep fixing until tests pass
```

**Execute:**
```bash
opencode "Run npm test, fix failing tests, and repeat until all tests pass"
```

### Example 3: Boilerplate generation

**Request:**
```
Generate CRUD APIs for each model
```

**Execute:**
```bash
opencode "Generate CRUD API endpoints in routes folder for each file in models folder"
```

## GLM-4.7 Characteristics

| Characteristic | Details |
|----------|---------|
| Context | 200K tokens |
| Output | Up to 128K tokens |
| Specialty | Agent-style coding |
| Function Call | Supported |
| MCP | Supported |
| Price | From $3/month (low cost) |

## Tasks OpenCode Excels At

| Category | Specific Tasks |
|----------|----------------|
| Bulk Processing | Lint fixes, format unification, import organization |
| Repetition | Test fix loops, build fix loops |
| Generation | Boilerplate, CRUD code, tests |
| Migration | Pattern-based bulk replacement |
| Exploration | Codebase investigation, pattern discovery |

## Cost Comparison

| Tool | Cost | Best Use |
|------|------------|-------------|
| Claude Code | High | Quality-focused production code |
| Codex CLI | Medium | Prototypes, GitHub integration |
| Gemini CLI | Medium | Large-scale refactoring |
| OpenCode + GLM | Low | Routine bulk tasks |

## When to Use Claude Code Instead

Use Claude Code for:
- Security-critical code
- Complex architecture design
- Production-quality final implementation
- Important customer-facing features

## Provider Configuration

OpenCode supports 75+ providers:

### macOS / Linux (bash/zsh)
```bash
# Z.AI (GLM-4.7)
export OPENCODE_PROVIDER=zai
export ZAI_API_KEY=your-key

# Local model
export OPENCODE_PROVIDER=ollama
export OLLAMA_HOST=http://localhost:11434
```

### Windows (PowerShell)
```powershell
# Z.AI (GLM-4.7)
$env:OPENCODE_PROVIDER = "zai"
$env:ZAI_API_KEY = "your-key"

# Local model
$env:OPENCODE_PROVIDER = "ollama"
$env:OLLAMA_HOST = "http://localhost:11434"
```

### Windows (CMD)
```cmd
rem Z.AI (GLM-4.7)
set OPENCODE_PROVIDER=zai
set ZAI_API_KEY=your-key

rem Local model
set OPENCODE_PROVIDER=ollama
set OLLAMA_HOST=http://localhost:11434
```

## Important Notes

- Use when cost takes priority over quality
- Always review important code
- Suitable for trial and error
- Polish production code with Claude Code

## Related Skills

- [ai-cli-selector](ai-cli-selector.md): Tool selection and overall flow
- [gemini-cli](gemini-cli.md): Analysis role
- [codex-cli](codex-cli.md): Review role
