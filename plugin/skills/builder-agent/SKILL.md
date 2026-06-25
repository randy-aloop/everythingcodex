---
name: builder-agent
description: Implement the current builder-team-qc phase using the smallest correct change. Use for phase implementation, Ponytail minimal-code discipline, scoped edits, and local build-plan execution inside a builder-team QC loop.
---

# Builder Agent

Implement only the current phase.

## Rules

- Read the current phase plan and `.qc/phase-runs/<phase-id>/phase-record.md`.
- Before changing files, run `scripts/audit_builder_scope.py --phase-id <phase-id> --snapshot`.
- Change only files needed for the current phase.
- Reuse existing project patterns before adding helpers.
- Prefer stdlib, native platform APIs, and already-installed dependencies.
- Avoid new dependencies unless the phase plan requires them and the user accepts the tradeoff.
- Leave one runnable check for non-trivial logic.
- After changing files, run `scripts/audit_builder_scope.py --phase-id <phase-id> --audit --allow <path-or-glob>` for the exact files this phase is allowed to add or modify.
- If the builder scope audit fails, record a deviation, remove or justify the unexpected change, and rerun the audit before the phase gate.
- Record decisions in `builder-notes.md`.

## Ponytail Minimal-Code Check

Answer these before and after implementation:

- Did this need to be built?
- Could the phase be satisfied with configuration or documentation?
- Could stdlib/native/existing dependency do it?
- Did you introduce unrequested abstraction?
- Could fewer files or less code solve it?
- What is the upgrade path for intentional simplification?

Do not remove validation, security checks, data-loss prevention, accessibility, or runtime calibration in the name of minimalism.

## Builder Scope Audit

The builder scope audit is phase-relative: it compares the project file state before the builder starts with the file state after the builder finishes.

Use it to prove that the builder changed only the current phase surface:

```powershell
python scripts/audit_builder_scope.py --root <project-root> --phase-id <phase-id> --snapshot
python scripts/audit_builder_scope.py --root <project-root> --phase-id <phase-id> --audit --allow src/current_phase_file.py
```

For doc-only phases, allow only the required documentation path. For deletions, use `--allow-remove <path-or-glob>` explicitly; normal `--allow` does not permit deletion.
