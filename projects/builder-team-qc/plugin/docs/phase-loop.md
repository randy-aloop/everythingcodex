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
5. Test role
6. Reviewer role
7. Compliance role
8. Integration seam audit
9. Release role when applicable
10. `validate_phase_record.py --scan-safety`
11. `validate_phase_record.py --scan-safety --strict-gate` before completion

Do not advance a phase when mandatory evidence is missing.
