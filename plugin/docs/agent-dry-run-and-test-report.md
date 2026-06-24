# Agent Dry Run And Test Report

This report compiles the agent dry runs, stress tests, self-correction checks, and Ponytail gate proof for `builder-team-qc`.

The focus of this report is agent behavior, not installation packaging.

## Current Agent Test Verdict

```text
Multiagent phase loop: pass
Builder-agent dry run: pass
Builder-agent stress test: pass
Builder scope audit gate: pass
Ponytail gate enforcement: pass
Stop/debug/log/correct workflow: pass as Codex-controller workflow
Interactive stop-and-ask inside scripts: not built into scripts
```

## Agent Surfaces Tested

| Agent / Role | Evidence Tested | Result |
| --- | --- | --- |
| `phase-controller` | phase selection, `.qc` init, phase start, strict gate, phase-board final state | Pass |
| `builder-agent` | smallest phase change, overbuild detection, dependency drift, doc-only drift | Pass |
| `ponytail-adapter` | latest Ponytail verdict must be `pass` | Pass |
| `test-agent` | phase test recording and missing-test failure | Pass |
| `reviewer-agent` | reviewer report must leave pending state before strict gate | Pass via completed role evidence |
| `compliance-agent` | deviation/safety evidence, no unresolved blockers | Pass |
| `integration-agent` | seam audit role evidence and next-phase handoff | Pass via completed role evidence |
| `release-agent` | release gate not-applicable handling for non-release phases | Pass for non-release scope |

Note:

- V01 executes role passes sequentially under Codex control. The "agents" are role contracts and evidence outputs, not independently launched remote agents.

## Dry Run 1 - Full Multiagent Phase Loop

Sandbox root:

```text
<local-sandbox>/builder-team-qc-full-loop-stress-20260623-202433
```

Capture:

```text
<local-sandbox>/builder-team-qc-full-loop-stress-20260623-202433/FULL-DRY-RUN-STRESS-CAPTURE.md
```

Summary:

```text
Phases executed: 13
Final strict safety gates passed: 13
Expected failure/checkpoint cases exercised: 5
Unexpected unresolved failures: 0
Recorded test rows: 13
Recorded deviation rows: 3
Self-improvement events: 3
```

What this proved:

- The phase loop can run from `phase-000` through `phase-012`.
- Strict gates stop incomplete or unsafe phase states.
- Test evidence, deviation logs, safety scan findings, and phase-board final state are recorded.
- The loop can correct sandbox failures and rerun the gates.

Stress cases:

1. Invalid phase ID rejected before phase creation.
2. Missing phase validation failed as expected.
3. Missing test evidence blocked strict gate.
4. Synthetic denylist-trigger safety material blocked the gate.
5. Placeholder-only safety correction was insufficient and blocked again.
6. Removing the risky field name cleared the gate.
7. Documentation policy/reference lines stayed non-blocking.

## Dry Run 2 - Builder-Agent Current Stress Test

Sandbox root:

```text
<local-sandbox>/builder-agent-current-dryrun-stress-20260623-205357
```

Capture:

```text
<local-sandbox>/builder-agent-current-dryrun-stress-20260623-205357/BUILDER-AGENT-CURRENT-DRYRUN-STRESS-CAPTURE.md
```

Summary:

```text
Builder phases executed: 5
Final strict gates passed: 5
Expected stop/failure checkpoints: 4
Unresolved failures: 0
Deviation records: 4
Stop reports: 4
Test records: 5
Builder scope audit records: 8
Self-improvement events: 4
```

What this proved:

- Builder-agent can operate in dry-run/no-write setup before real `.qc` initialization.
- Builder-agent can keep work phase-scoped.
- Overbuild is caught by builder scope audit.
- Missing test evidence is caught by strict gate.
- Dependency creep is caught by builder scope audit.
- Doc-only phase drift is caught by builder scope audit.
- Each issue was logged, corrected, rerun, and passed.

Builder-agent stress cases:

| Stress Case | Detector | Proof Of Correction |
| --- | --- | --- |
| Unexpected `src/future_engine.py` | builder scope audit | file removed, audit rerun passed |
| Missing test evidence | strict gate | test recorded, strict gate rerun passed |
| Unexpected `requirements.txt` | builder scope audit | dependency file removed, audit rerun passed |
| Doc-only phase created code | builder scope audit | code file removed, audit rerun passed |

Stop/debug/log/correct evidence:

- failed audit or gate log
- `.qc/deviation-log.jsonl`
- stop report under `capture/`
- self-improvement event under `capture/self-improvement-events.json`
- rerun proof
- final strict gate pass

## Dry Run 3 - Builder Scope Audit Gate Proof

Sandbox root:

```text
<local-sandbox>/builder-scope-native-test-20260623-204519
```

Capture:

```text
<local-sandbox>/builder-scope-native-test-20260623-204519/BUILDER-SCOPE-NATIVE-TEST-CAPTURE.md
```

Final gate:

```json
{
  "errors": [],
  "warnings": [],
  "ok": true
}
```

What this proved:

- `audit_builder_scope.py --snapshot` writes a baseline.
- `audit_builder_scope.py --audit` catches unexpected file creation.
- The audit passes after the unexpected file is removed.
- `validate_phase_record.py --require-builder-scope` enforces builder scope at strict gate.
- Test-harness logs can be ignored using `--ignore capture/**`.

## Ponytail Gate Proof

Sandbox root:

```text
<local-sandbox>/ponytail-enforcement-proof-20260623-222802
```

Capture:

```text
<local-sandbox>/ponytail-enforcement-proof-20260623-222802/PONYTAIL-ENFORCEMENT-PROOF.md
```

### Negative Control

The proof intentionally recorded the latest Ponytail verdict as `revise`.

Strict gate result:

```json
{
  "errors": [
    "latest ponytail event is not pass"
  ],
  "warnings": [],
  "ok": false
}
```

Meaning:

- Ponytail is not just a note.
- The final gate fails when the latest Ponytail event is not `pass`.

### Positive Control

The proof then recorded a later Ponytail verdict as `pass`.

Strict gate result:

```json
{
  "errors": [],
  "warnings": [],
  "ok": true
}
```

Meaning:

- The strict gate consumes the latest Ponytail event.
- The gate passes after Ponytail records `pass` and other required evidence exists.

## What The Agent Tests Prove

The tests prove the following behavior:

1. A phase cannot pass without required role evidence.
2. A phase cannot pass if the latest Ponytail verdict is not `pass`.
3. A phase cannot pass if a required test result is missing.
4. A phase cannot pass if builder scope audit has unexpected changes when required.
5. Safety blockers stop the gate.
6. Non-blocking safety docs/reference findings can remain warnings.
7. Deviations are logged.
8. Stop reports can document user-decision points.
9. Corrected phases can rerun and pass.
10. The phase board records final completion.

## What The Agent Tests Do Not Prove Yet

The tests do not yet prove:

- true concurrent subagent execution
- remote agent launch
- Codex plugin registry install/load
- interactive question prompts inside script-only mode
- `record_decision.py` helper behavior
- `record_gate_decision.py` helper behavior
- automated changed-files/diff recording helper behavior

Those are either intentionally out of V01 scope or still current helper gaps.

## Stop-And-Ask Status

Confirmed:

- The process stops by failed audit/gate exit code.
- The process records deviations.
- The process writes stop reports in the Codex-controlled workflow.

Not built into scripts:

- A script-level interactive prompt asking the user what to do.

Operational rule:

```text
When a stop report is written, Codex must ask the user before applying a correction that changes scope, dependency, architecture, runtime, release behavior, or safety policy.
```

## Evidence Index

Full-loop stress:

```text
<local-sandbox>/builder-team-qc-full-loop-stress-20260623-202433/FULL-DRY-RUN-STRESS-CAPTURE.md
```

Builder-agent stress:

```text
<local-sandbox>/builder-agent-current-dryrun-stress-20260623-205357/BUILDER-AGENT-CURRENT-DRYRUN-STRESS-CAPTURE.md
```

Builder scope proof:

```text
<local-sandbox>/builder-scope-native-test-20260623-204519/BUILDER-SCOPE-NATIVE-TEST-CAPTURE.md
```

Ponytail proof:

```text
<local-sandbox>/ponytail-enforcement-proof-20260623-222802/PONYTAIL-ENFORCEMENT-PROOF.md
```

## Final Verdict

```text
Agent dry run: PASS
Agent stress test: PASS
Builder-agent scope control: PASS
Ponytail gate proof: PASS
Self-correction proof: PASS
Logging proof: PASS
Script-level interactive ask: NOT IMPLEMENTED
Codex-controller stop-and-ask workflow: PROVEN BY STOP REPORTS
```
