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
4. Apply the role checks: builder, reviewer, test, compliance, integration, release when relevant.
5. Record Ponytail minimal-code evidence with `record_ponytail_check.py`.
6. Record deviations and test results as they happen.
7. Run `validate_phase_record.py --phase-id <id> --scan-safety` while the phase is in progress.
8. Before any completion claim, run `validate_phase_record.py --phase-id <id> --scan-safety --strict-gate`.
9. Decide the phase gate: `pass`, `revise`, `block`, or `accepted_with_risk`.
10. Do not start the next phase unless the current gate allows it.

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

## Gate Rules

Pass only when:

- required deliverables are complete
- quick tests are recorded
- Ponytail minimal-code verdict is `pass`
- seam audit is complete
- no blocker deviation remains
- no safety scan blocker remains
- release gate is complete for release/runtime phases

If evidence is missing, choose `block` or `revise`, not `pass`.
