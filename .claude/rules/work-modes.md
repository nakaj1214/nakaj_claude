# Work Modes

Detect the current work mode from user intent and apply the matching guidelines.

## Dev Mode (Implementation / Bug Fix)

Trigger: user asks to build, fix, add, implement, or modify code.

- Write code first, explain after
- Prefer working solutions over perfect solutions
- Run tests after changes
- Keep commits atomic

Priority: Make it work → Make it right → Make it clean

## Research Mode (Investigation / Learning)

Trigger: user asks to investigate, explore, understand, compare, or research.

- Read broadly before drawing conclusions
- Ask clarifying questions
- Document findings as you go
- Do NOT write code until understanding is clear

Priority: Understand first → Hypothesize → Verify with evidence → Summarize

## Review Mode (Code Review / Quality Check)

Trigger: user asks to review, check, audit, or analyze code quality.

- Read thoroughly before commenting
- Prioritize issues by severity: Critical > High > Medium > Low
- Suggest fixes, not just problems
- Check security vulnerabilities

Checklist: Logic errors, edge cases, error handling, security, performance, readability, test coverage
