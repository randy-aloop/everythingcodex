---
name: ponytail-adapter
description: Apply safe Ponytail minimal-code discipline inside builder-team-qc without trusting Ponytail hooks, benchmarks, remote install behavior, or generated-code execution paths.
---

# Ponytail Adapter

Use Ponytail as instruction discipline by default.

## Modes

- `task-scoped`: apply Ponytail rules for this task only.
- `project-agents`: project `AGENTS.md` contains Ponytail-style rules.
- `contained-workspace`: Ponytail is used only in a contained reviewed workspace.
- `unavailable-fallback`: Ponytail is not loaded; run the local minimal-code checklist.

Never claim hook-based Ponytail execution unless hooks were explicitly reviewed, enabled, and recorded.

## Core Rule

Use the smallest correct implementation:

YAGNI -> stdlib -> native platform -> already-installed dependency -> one-liner -> minimum new code.

Record evidence with `scripts/record_ponytail_check.py`.
