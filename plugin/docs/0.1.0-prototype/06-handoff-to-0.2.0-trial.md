# Handoff To 0.2.0-Trial

Version: `0.1.0-prototype`
Created: 2026-06-24

This handoff turns the prototype archive into a concrete next step.

## Trial Objective

`0.2.0-trial` should prove Builder Team QC on a real local target.

Success means:

```text
install
initialize .qc
start one phase
run builder/Ponytail/test/review/compliance/seam
strict gate blocks missing proof
strict gate passes when proof is complete
record final phase-board transition
inspect .qc afterward
```

## First Trial Target

Use a tiny local project before trying a real product repo.

Suggested shape:

```text
toy-alpha-build/
  README.md
  src/math_utils.py
  tests/test_math_utils.py
```

Suggested phases:

```text
phase-000: initialize README
phase-001: add one Python function
phase-002: add one test
phase-003: close phase with strict gate and final board transition
```

## Trial Workstreams

### T1. Align Packaged Docs With Current Scripts

Fix:

- README path mismatch.
- Any commands that do not exist.
- Any claims that validator enforces behavior it does not enforce.

### T2. Harden Validator

Implement:

- role verdict parsing
- skipped required test enforcement
- decision-log accepted-risk matching
- issue-register blocker enforcement
- release `not_applicable` conditional handling
- stronger exit codes or clear current exit-code docs

### T3. Add Gate Recording

Implement or exact-manual fallback:

- `record_decision.py`
- `record_gate_decision.py`
- final `gate-summary.md`
- final phase-board transition

### T4. Validate And Harden Builder Scope Audit

Current state:

- `audit_builder_scope.py` exists.
- `validate_phase_record.py` has `--require-builder-scope`.

Trial work:

- validate baseline creation on a real target
- validate allowed path globs
- validate unexpected file changes fail the gate
- validate `--require-builder-scope` blocks missing or failed audit evidence
- update docs if trial behavior differs from the target contract

### T5. Validate And Tune Safety Scanner Classification

Current state:

- safety scanner classification exists for `info`, `warning`, and `blocker`

Trial work:

- keep banned patterns in place
- verify policy docs, attribution links, and scanner self-definitions stay non-blocking
- verify active secrets, remote execution, and remote tool configuration remain blockers
- tune false positives found during the real trial

### T6. Run The Trial

Record:

- commands
- failures
- fixes
- `.qc` artifacts
- strict gate output
- final phase-board state

## Trial Gate

Do not call trial complete until:

- one target project completed at least one phase
- `.qc/phase-board.json` records final decision
- safety scan does not block harmless references
- accepted-risk path cannot self-approve
- missing evidence causes strict gate failure
- complete evidence causes strict gate pass

## Output Artifacts For 0.2.0-Trial

Create:

```text
docs/0.2.0-trial/
  README.md
  trial-plan.md
  trial-run-log.md
  validator-hardening-report.md
  safety-scanner-classification-report.md
  final-trial-readiness-assessment.md
```

Optional:

```text
.qc/
  phase-runs/<trial-phase-id>/
  test-results/<trial-phase-id>.jsonl
  issue-register.jsonl
  decision-log.jsonl
```

## Carry-Forward Decisions

- Runtime V01 remains single-run multiagent.
- Parallel Runtime V02 remains future work.
- `.qc` remains the durable source of truth.
- Alpha waits for a reproducible end-to-end local trial.
- Beta waits for repeated real project success.
