# Agent Dry Run And Test Report

Version: V02
Updated: 2026-06-24
Supersedes: V01 report from 2026-06-23
Status: `0.2.0-trial` stress addendum added

This report compiles the agent dry runs, stress tests, self-correction checks, and Ponytail gate proof for `builder-team-qc`.

The focus of this report is agent behavior, not installation packaging.

## Current Agent Test Verdict

```text
Multiagent phase loop: pass
Builder-agent dry run: pass
Builder-agent stress test: pass
0.2.0-trial agent stress harness: pass
Builder scope audit gate: pass
Ponytail gate enforcement: pass
Ponytail hash-bound evidence: pass
Decision helper proof: pass
Gate-decision helper proof: pass
Release auto-detection gate: pass
Stop/debug/log/correct workflow: pass as Codex-controller workflow
Interactive stop-and-ask inside scripts: not built into scripts
```

## Agent Surfaces Tested

| Agent / Role | Evidence Tested | Result |
| --- | --- | --- |
| `phase-controller` | phase selection, `.qc` init, phase start, strict gate, phase-board final state | Pass |
| `builder-agent` | smallest phase change, overbuild detection, dependency drift, doc-only drift | Pass |
| `ponytail-adapter` | latest Ponytail verdict must be `pass`; stale changed-file/diff binding blocks | Pass |
| `test-agent` | phase test recording, missing-test failure, required skipped-test failure | Pass |
| `reviewer-agent` | reviewer report must leave pending state; `Verdict: revise` blocks strict gate | Pass |
| `compliance-agent` | deviation/safety evidence, no unresolved blockers | Pass |
| `integration-agent` | seam audit role evidence and next-phase handoff | Pass via completed role evidence |
| `release-agent` | release gate not-applicable handling and release-phase auto-detection | Pass |

Note:

- V01 and V02 execute role passes sequentially under Codex control. The "agents" are role contracts and evidence outputs, not independently launched remote agents.

## 0.2.0-Trial Agent Stress Addendum

Fable5 run:

```text
<redacted-local-fable5-run>
```

Target root:

```text
<redacted-local-installer-test-target>
```

Summary:

```text
Cases executed: 10
Cases passed: 10
Cases failed: 0
```

Stress cases:

| Case | Result |
| --- | --- |
| `template_validation` | Pass |
| `baseline_pass_and_gate_board_transition` | Pass |
| `role_verdict_revise_blocks_then_passes` | Pass |
| `skipped_required_test_blocks_then_passes` | Pass |
| `ponytail_revise_blocks_then_passes` | Pass |
| `ponytail_stale_diff_blocks_then_passes` | Pass |
| `builder_scope_overbuild_blocks_then_passes` | Pass |
| `open_blocker_issue_blocks_then_passes` | Pass |
| `accepted_risk_requires_decision_then_records_gate` | Pass |
| `release_phase_auto_detect_blocks_until_release_gate_passes` | Pass |

What this added over V01:

- `record_decision.py` behavior is now proved for accepted-risk decision-log evidence.
- `record_gate_decision.py` behavior is now proved for terminal phase-board transitions and `gate-summary.md` output.
- Strict role verdict parsing is now proved with a negative `Verdict: revise` control.
- Required skipped-test blocking is now proved.
- Ponytail changed-files and implementation-diff hash binding is now proved with a stale-diff negative control.
- Builder scope overbuild blocking is now proved through the installed `0.2.0-trial` script path.
- Open issue-register blocker enforcement is now proved.
- Release-phase auto-detection is now proved.

Boundary:

- This is a synthetic local sandbox stress run.
- It does not prove a real product build.
- It does not prove true concurrent autonomous agents.
- It does not prove global Codex plugin registry install/load.

## Dry Run 1 - Full Multiagent Phase Loop

Sandbox root:

```text
<local-sandbox>/builder-team-qc-full-loop-stress-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/builder-team-qc-full-loop-stress-<redacted-run-id>/FULL-DRY-RUN-STRESS-CAPTURE.md
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
<local-sandbox>/builder-agent-current-dryrun-stress-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/builder-agent-current-dryrun-stress-<redacted-run-id>/BUILDER-AGENT-CURRENT-DRYRUN-STRESS-CAPTURE.md
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
<local-sandbox>/builder-scope-native-test-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/builder-scope-native-test-<redacted-run-id>/BUILDER-SCOPE-NATIVE-TEST-CAPTURE.md
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
<local-sandbox>/ponytail-enforcement-proof-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/ponytail-enforcement-proof-<redacted-run-id>/PONYTAIL-ENFORCEMENT-PROOF.md
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
11. Accepted-risk blocker deviations require decision-log proof.
12. Role verdicts such as `revise` and `block` are strict-gate blockers.
13. Required tests cannot all be skipped.
14. Ponytail pass evidence must match the current changed-files and implementation-diff hashes.
15. Release phases are detected and blocked until release-gate evidence passes.

## What The Agent Tests Do Not Prove Yet

The tests do not yet prove:

- true concurrent subagent execution
- remote agent launch
- Codex plugin registry install/load
- interactive question prompts inside script-only mode
- automated changed-files/diff recording helper behavior
- a real product build outside a synthetic sandbox

Those are either intentionally out of V02 scope or still current helper gaps.

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
<local-sandbox>/builder-team-qc-full-loop-stress-<redacted-run-id>/FULL-DRY-RUN-STRESS-CAPTURE.md
```

Builder-agent stress:

```text
<local-sandbox>/builder-agent-current-dryrun-stress-<redacted-run-id>/BUILDER-AGENT-CURRENT-DRYRUN-STRESS-CAPTURE.md
```

Builder scope proof:

```text
<local-sandbox>/builder-scope-native-test-<redacted-run-id>/BUILDER-SCOPE-NATIVE-TEST-CAPTURE.md
```

Ponytail proof:

```text
<local-sandbox>/ponytail-enforcement-proof-<redacted-run-id>/PONYTAIL-ENFORCEMENT-PROOF.md
```

0.2.0-trial agent stress:

```text
<redacted-local-stress-summary>
```

## Final Verdict

```text
Agent dry run: PASS
Agent stress test: PASS
0.2.0-trial stress harness: PASS
Builder-agent scope control: PASS
Ponytail gate proof: PASS
Ponytail stale-binding control: PASS
Decision helper proof: PASS
Gate-decision helper proof: PASS
Release auto-detection gate: PASS
Self-correction proof: PASS
Logging proof: PASS
Script-level interactive ask: NOT IMPLEMENTED
Codex-controller stop-and-ask workflow: PROVEN BY STOP REPORTS
Real product build trial: NOT YET PROVEN
```
