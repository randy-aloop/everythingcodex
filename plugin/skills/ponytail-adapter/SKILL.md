---
name: ponytail-adapter
description: Apply safe Ponytail minimal-code discipline inside builder-team-qc without trusting Ponytail hooks, benchmarks, remote install behavior, or generated-code execution paths.
---

# Ponytail Adapter

Use Ponytail as instruction discipline by default.

## Attribution

This adapter credits [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), the MIT-licensed Ponytail project by Dietrich Gebert. Builder Team QC does not vendor or run upstream Ponytail by default; it applies a local checklist unless upstream hooks are explicitly reviewed, enabled, and recorded.

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

The event must identify the current attempt and bind the pass to the exact builder evidence:

- `.qc/phase-runs/<phase-id>/changed-files.json`
- `.qc/phase-runs/<phase-id>/implementation-diff.patch`
- `.qc/phase-runs/<phase-id>/evidence/builder-scope-audit.json`

Use structured subcheck status fields. A `minimum_code_verdict=pass` is valid only when YAGNI, stdlib/native/existing-dependency, dependency, and abstraction statuses are all `pass`.

For upstream Ponytail hooks, record `upstream_hook_enabled=true`, `upstream_hook_review_id`, and the upstream version. Do not enable upstream hooks without explicit review and approval.
