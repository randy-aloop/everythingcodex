---
name: phase-controller
description: Run a local builder-team QC phase loop for project builds. Use when the user asks to use builder-team-qc, builder team QC, phase-controlled multiagent building, Ponytail minimal-code checks, .qc records, seam audits, release gates, or ADK-style deterministic builder workflow orchestration without remote services.
---

# Phase Controller

Coordinate one build phase at a time. Treat this as a deterministic workflow controller, similar to ADK `Workflow` routing, but local-only and evidence-first.

## Operating Model

Use this order:

1. Read the project build plan and identify the current phase.
2. Run `scripts/init_qc.py` if `.qc/` does not exist.
3. Run `scripts/start_phase.py --phase-id <id> --title <title>`.
4. Apply `builder-agent` to create the candidate phase change.
5. Apply Ponytail discipline and record minimal-code evidence with `record_ponytail_check.py`.
6. If Ponytail is not `pass`, choose `revise` or `block` before running deeper evidence checks.
7. Apply `test-agent`, then reviewer, compliance, integration, and release when relevant.
8. Record deviations and test results as they happen.
9. Run `validate_phase_record.py --phase-id <id> --scan-safety` while the phase is in progress.
10. Before any completion claim, run `validate_phase_record.py --phase-id <id> --scan-safety --strict-gate`.
11. Add `--release-phase` when runtime, Docker, API, deploy, dependency, sidecar, production-debug, rollback, or release behavior is in scope.
12. Decide the phase gate: `pass`, `revise`, `block`, or `accepted_with_risk`.
13. Update `.qc/phase-board.json` with the final gate transition.
14. Do not start the next phase unless the current gate allows it.

## Local-Only Policy

Default deny:

- API keys, OAuth files, passwords, refresh tokens, service account private keys
- remote model/provider endpoints
- OpenAPI REST tools
- remote MCP transports
- A2A remote agents
- cloud storage/session/memory backends
- unsafe local code execution unless explicitly in scope
- Docker remote daemon `base_url`
- non-loopback HTTP server binding

The controller may use local scripts and local project files. It must not install global tools, enable hooks, create public tunnels, or expose servers.

## Role Evidence

Each role writes a record in `.qc/phase-runs/<phase-id>/`:

- `builder-notes.md`
- `reviewer-report.md`
- `test-report.md`
- `compliance-report.md`
- `seam-audit.md`
- `release-gate.md`

Subagent output is evidence, not authority. The controller makes the gate decision from source, tests, and records.

Ponytail is not owned by the test role. It gates the candidate builder output before test/review fan-out, and its event is consumed by reviewer, compliance, and the final controller gate.

## Gate Rules

Pass only when:

- required deliverables are complete
- required role verdicts are `pass`
- at least one required non-skipped test is recorded as `pass`
- Ponytail minimal-code verdict is `pass`
- seam audit is complete
- no blocker deviation remains
- no safety scan blocker remains
- release gate is complete for release/runtime phases
- `.qc/phase-board.json` is updated from pending/open to the final gate state

If evidence is missing, choose `block` or `revise`, not `pass`.

Treat `Verdict: revise`, `Verdict: block`, all-skipped required tests, and missing release evidence as blockers. `accepted_with_risk` requires an explicit human decision in `.qc/decision-log.jsonl`; the controller must not self-approve it.
