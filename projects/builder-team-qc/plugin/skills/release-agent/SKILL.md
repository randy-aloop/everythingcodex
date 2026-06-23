---
name: release-agent
description: Check production/debug readiness for builder-team-qc phases. Use for release gates, runtime evidence, no-secret logging, rollback notes, Docker readiness, and troubleshooting checks.
---

# Release Agent

Run this role for release, runtime, Docker, deployment, API, sidecar, or production-debug phases.

## Check

- Debug switches are explicit and safe.
- Logs do not leak secrets.
- Runtime config is reproducible.
- Docker/container checks are recorded when relevant.
- Rollback and troubleshooting notes exist.
- Health checks or smoke checks are documented.

## Output

Write `release-gate.md` with verdict `pass`, `revise`, `block`, or `not_applicable`.
