# 0.2.0-Trial Hardening Implementation Report

Version: `0.2.0-trial.1`
Created: 2026-06-24
Status: Implemented
Supersedes:

- `docs/0.1.0-Trial/patch-01-strict-gate-enforcement.md` status `Proposed`
- `docs/0.1.0-Trial/patch-02-phase-board-transition.md` status `Proposed`
- `0.1.0-prototype` helper-gap state for strict gate, decision recording, gate recording, and Ponytail evidence binding

This report records the first implementation pass for `0.2.0-trial`.

## Implemented

- Anchored role verdict parsing for `Verdict:` and `Gate Decision:` fields.
- Strict-gate failure for role `revise`, `block`, `pending`, missing, duplicated, or unknown verdicts.
- Strict-gate issue-register blocker enforcement.
- Required-test enforcement with latest required result per check name.
- Release-gate auto-detection from phase title and `.qc/qc-config.json` patterns.
- Classified validator exit codes:
  - `0` pass
  - `1` non-strict/general failure
  - `10` strict-gate failure
  - `20` schema/config/invocation failure
  - `30` safety blocker
- `record_decision.py` for human accepted-risk and approval records.
- `record_gate_decision.py` for phase-board transitions, gate summaries, and append-only gate events.
- Phase-board fields for gate timestamps, revise attempts, release requirement, and accepted-risk decision id.
- Start-phase guard that refuses a different new phase while the board is still open/revising/blocked unless `--force` is used.
- Ponytail evidence binding to:
  - `.qc/phase-runs/<phase-id>/changed-files.json`
  - `.qc/phase-runs/<phase-id>/implementation-diff.patch`
  - `.qc/phase-runs/<phase-id>/evidence/builder-scope-audit.json`
- Ponytail structured subcheck statuses and upstream-hook proof fields.

## Verification

Smoke target:

```text
phase-by-phase-build-log/hardening-smoke-20260624
```

Verified:

- baseline fully-evidenced phase passes strict gate
- reviewer `Verdict: block` fails strict gate
- open blocker issue fails strict gate
- all-skipped required test fails strict gate
- release-pattern phase auto-detects release requirement and fails incomplete release gate
- stale Ponytail implementation-diff hash fails strict gate
- refreshed Ponytail event restores pass
- `record_gate_decision.py --gate pass` updates board and gate summary
- `start_phase.py` allows next phase after pass
- `start_phase.py` blocks a different new phase while current board is open
- `accepted_with_risk` without decision id fails
- `accepted_with_risk` with matching `decision-log.jsonl` entry succeeds

## Implementation Notes

- Release auto-detection intentionally uses phase id/title, not the whole phase-record body. The first harness run showed that scanning boilerplate text such as "release gate when applicable" creates false release positives.
- Required skipped tests are evaluated by latest required result per check name, so a later rerun can clear an earlier skipped record.
- `record_gate_decision.py` records deterministic policy outcomes. It does not decide whether the phase deserves a pass; the controller still owns the gate decision.

## Remaining Trial Work

- Run a real local target build, not only a synthetic smoke harness.
- Add a formal reusable mutation harness script if repeated trial runs need the same checks.
- Update any public README or install guide examples that still show the old Ponytail or phase-board command shape.
- Decide whether `latest_gate_at` or `last_gate_at` should remain as dual fields long term.
