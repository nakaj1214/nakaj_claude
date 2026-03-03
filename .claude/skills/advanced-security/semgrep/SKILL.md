---
name: semgrep
description: Run Semgrep static analysis scan on a codebase using parallel subagents. Automatically
  detects and uses Semgrep Pro for cross-file analysis when available. Use when asked to scan
  code for vulnerabilities, run a security audit with Semgrep, find bugs, or perform
  static analysis. Spawns parallel workers for multi-language codebases and triage.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Write
  - Task
  - AskUserQuestion
  - TaskCreate
  - TaskList
  - TaskUpdate
  - WebFetch
---

# Semgrep Security Scan

詳細な手順: [INSTRUCTIONS.md](INSTRUCTIONS.md)

## リソース

- [INSTRUCTIONS.md](INSTRUCTIONS.md) — 詳細手順・ルール・例
