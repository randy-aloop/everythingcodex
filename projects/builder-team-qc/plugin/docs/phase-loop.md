# Phase Loop

Builder Team QC mimics the useful part of ADK workflow routing: deterministic phase gates with recorded state.

For the full hierarchy, sequential/parallel/loop mapping, and shared-state model, see `docs/multi-agent-modes.md`.
For operational phase-control notes, see `docs/orchestration-notes.md`.
For the visual flow, see `docs/orchestration-diagram.md`.

Run order:

1. `init_qc.py`
2. `start_phase.py`
3. Builder role
4. Ponytail check
5. Test role with at least one required non-skipped passing check
6. Reviewer role
7. Compliance role
8. Integration seam audit
9. Release role when `release_required=true`
10. `validate_phase_record.py --scan-safety`
11. `validate_phase_record.py --scan-safety --strict-gate` before completion

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
- a required role verdict is `pending`, `revise`, or `block`
- Ponytail is missing or not `pass`
- no test result exists
- all required tests are `skipped`
- any recorded test is `fail`
- a blocker deviation lacks accepted-risk proof
- release is required and `release-gate.md` is pending or `not_applicable`
- the safety scan finds a blocker

Revise loop:

```text
attempt 1 -> fix smallest failing item -> rerun proof
attempt 2 -> narrow blocker -> rerun proof
attempt 3 -> pass, block, or ask for human accepted-risk decision
```

Track the count in `.qc/phase-board.json` as `revise_attempts`. The default cap is `max_revise_attempts=3`; do not continue past the cap without a recorded human decision.

`accepted_with_risk` requires a matching `.qc/decision-log.jsonl` entry with impact, owner, deadline, rollback, and follow-up. The controller cannot self-approve accepted risk.

After `pass`, `block`, or `accepted_with_risk`, update `.qc/phase-board.json` so the phase does not remain `open` with `latest_gate_decision=pending`.
