# Phase Loop

Version: V03.1
Updated: 2026-06-25
Supersedes: V03

Builder Team QC mimics the useful part of ADK workflow routing: deterministic phase gates with recorded state.

For the full hierarchy, sequential/parallel/loop mapping, and shared-state model, see `docs/multi-agent-modes.md`.
For operational phase-control notes, see `docs/orchestration-notes.md`.
For the detailed phase-by-phase runbook, see `docs/phase-by-phase-run-plan.md`.
For the visual flow, see `docs/orchestration-diagram.md`.

Run order:

0. Pre-build plan check: phase named, evidence known, release impact classified, protected zones identified.
1. `init_qc.py`
2. `start_phase.py`
3. Builder role
4. Persist `changed-files.json` and `implementation-diff.patch`
5. Ponytail check
6. Test role with at least one required test whose status is `pass`
7. Reviewer role
8. Compliance role
9. Integration seam audit
10. Release role when `release_required=true`
11. `validate_phase_record.py --scan-safety`
12. `validate_phase_record.py --scan-safety --strict-gate` before completion
13. `summarize_phase.py`
14. Write `gate-summary.md` and update `.qc/phase-board.json`

Do not advance a phase when mandatory evidence is missing.

For release/runtime phases, strict validation must be release-aware:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety `
  --strict-gate `
  --release-phase
```

Strict gate blocks when:

- a required role report is missing
- a required role verdict is missing, duplicated, unknown, `pending`, `revise`, or `block`
- Ponytail is missing or not `pass`
- no test result exists
- no required test has status `pass`
- a required test is `skipped`
- any recorded test is `fail`
- a blocker issue is open in `.qc/issue-register.jsonl`
- a blocker deviation lacks accepted-risk proof
- release is required and `release-gate.md` is pending or `not_applicable`
- the safety scan finds a blocker

Helper status:

- `record_test_result.py` supports `--required` and `--attempt`; use those flags so strict validation can read machine-readable test policy evidence.
- `record_deviation.py` supports `--attempt`, `--issue-id`, and `--decision-id`; use those flags for gate-relevant deviations.
- `record_decision.py` and `record_gate_decision.py` are current scripts and should be used instead of hand-editing decision or phase-board state.
- `validate_phase_record.py` returns classified exit codes: `0` pass, `10` strict-gate failure, `20` schema/config/invocation error, and `30` safety blocker.
- Remaining helper gap: `changed-files.json` and `implementation-diff.patch` still require controller-generated evidence before Ponytail runs.

Revise loop:

```text
attempt 1 -> fix smallest failing item -> rerun proof
attempt 2 -> narrow blocker -> rerun proof
attempt 3 -> pass, block, or ask for human accepted-risk decision
```

Track the count in `.qc/phase-board.json` as `revise_attempts`. The default cap is `max_revise_attempts=3`; do not continue past the cap without a recorded human decision. Rerun affected proof by default; rerun full proof when the fix touches shared contracts, schemas, runtime behavior, dependencies, Docker, safety policy, release behavior, or when the affected scope is uncertain.

`accepted_with_risk` requires a matching `.qc/decision-log.jsonl` entry with impact, owner, deadline, rollback, and follow-up. The controller cannot self-approve accepted risk.

After `pass`, `block`, or `accepted_with_risk`, write `.qc/phase-runs/<phase-id>/gate-summary.md` and update `.qc/phase-board.json` so the phase does not remain `open` with `latest_gate_decision=pending`.
