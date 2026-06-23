# Builder Team QC Phase-by-Phase Run Plan

This is the latest detailed operating plan for running Builder Team QC phase by phase.

Builder Team QC has two layers:

1. Product phases: the user's actual build plan, such as scaffold plugin, add scripts, add docs, run sample project, harden gates, or prepare release.
2. QC phase loop: the repeated builder-team process used to complete each product phase safely.

The product phase changes every time. The QC loop stays the same.

## Control Model

```text
user goal
  -> phase-controller
    -> open one phase
    -> builder-agent creates candidate work
    -> ponytail-adapter checks minimal-code discipline
    -> evidence fan-out runs sequentially in V01
    -> strict gate decides pass / revise / block / accepted_with_risk
    -> phase-board records final state
  -> next phase only when allowed
```

V01 is local-only. It does not launch remote agents, expose an API server, call A2A, call remote MCP, require API keys, or use public tunnels. Codex remains the visible controller.

## Phase 0 - Intake And Phase Selection

Goal: choose exactly one product phase to run.

Inputs:

- target project root
- build plan or phase summary
- current phase id
- current phase title
- next phase id, if known
- runtime/release impact
- required tests
- protected zones
- known blockers

Controller actions:

1. Read the build plan.
2. Identify the current phase only.
3. Decide whether `release_required=true`.
4. Set `max_revise_attempts=3` unless the user explicitly sets a lower cap.
5. Record assumptions in the phase record or deviation log.

Do not start implementation if the phase cannot be named.

Example phase identity:

```text
phase_id: phase-004
title: Add decision-log enforcement
next_phase_id: phase-005
release_required: false
max_revise_attempts: 3
```

## Phase 1 - Initialize QC State

Goal: create or verify the local `.qc/` evidence area.

Command:

```powershell
python scripts\init_qc.py --root <target-project>
```

Expected state:

```text
.qc/
  phase-board.json
  qc-config.json
  issue-register.jsonl
  deviation-log.jsonl
  decision-log.jsonl
  ponytail-events.jsonl
  test-results/
  phase-runs/
```

Gate rule:

- If `.qc/` cannot be created or inspected, stop and report `block`.

## Phase 2 - Start Or Resume The Phase

Goal: create the phase run folder and seed role evidence files.

Command:

```powershell
python scripts\start_phase.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --title "<phase-title>" `
  --next-phase-id <next-phase-id> `
  --build-plan "<plan path or phase summary>"
```

Expected state:

```text
.qc/phase-runs/<phase-id>/
  phase-record.md
  builder-notes.md
  reviewer-report.md
  test-report.md
  compliance-report.md
  seam-audit.md
  release-gate.md
  evidence/
```

Manual phase-board contract until helper support exists:

```json
{
  "current_phase_id": "<phase-id>",
  "current_phase_status": "open",
  "latest_gate_decision": "pending",
  "release_required": false,
  "revise_attempts": 0,
  "max_revise_attempts": 3
}
```

Gate rule:

- No role work starts until the phase run exists.
- If the phase board cannot represent the current phase, stop and report `block`.

## Phase 3 - Builder Role

Goal: produce the smallest correct candidate change for the current phase.

Role: `builder-agent`

Builder checks:

- read phase record
- read target files
- change only current-phase files
- avoid unrelated refactors
- prefer existing patterns, stdlib, native platform APIs, and already-installed dependencies
- record changed files and decisions in `builder-notes.md`

Output:

```text
.qc/phase-runs/<phase-id>/builder-notes.md
candidate source/document changes
```

Gate rule:

- Builder output is evidence, not a gate decision.
- If implementation needs scope beyond the phase, record a deviation before continuing.

## Phase 4 - Ponytail Minimal-Code Gate

Goal: decide whether the candidate work is appropriately small before spending time on deeper checks.

Role: `ponytail-adapter`

Attribution: this adapter credits `DietrichGebert/ponytail` as the upstream Ponytail project. Builder Team QC does not vendor or run upstream Ponytail by default; V01 uses a local instruction/checklist adapter unless upstream hooks are explicitly reviewed, enabled, and recorded.

Command:

```powershell
python scripts\record_ponytail_check.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --mode task-scoped `
  --yagni-check "No extra scope added" `
  --stdlib-check "Used existing project/runtime tools where possible" `
  --dependency-check "No new dependency added" `
  --abstraction-check "No new abstraction unless required" `
  --minimum-code-verdict pass `
  --notes "Minimal-code discipline checked"
```

Allowed verdicts:

- `pass`: continue to evidence checks
- `revise`: loop back to builder for the smallest correction
- `block`: stop and report blocker

Gate rule:

- Tests/review fan-out should not proceed if Ponytail verdict is `revise` or `block`.
- The latest Ponytail event for the phase must be `pass` before final gate pass.

## Phase 5 - Evidence Fan-Out

Goal: collect independent evidence after Ponytail passes.

V01 behavior: logical fan-out only. Codex executes these role passes sequentially, not concurrently.

Required role passes:

| Role | Output | Gate expectation |
| --- | --- | --- |
| `test-agent` | `test-report.md`, `.qc/test-results/<phase-id>.jsonl` | At least one required non-skipped passing check. |
| `reviewer-agent` | `reviewer-report.md` | `Verdict: pass`. |
| `compliance-agent` | `compliance-report.md` | `Verdict: pass`. |
| `integration-agent` | `seam-audit.md` | `Verdict: pass`. |
| `release-agent` | `release-gate.md` | `Verdict: pass` when `release_required=true`; `not_applicable` only when false. |

## Phase 5A - Test Agent

Goal: prove the phase works at the smallest useful level.

Recommended ladder:

```text
syntax or compile
targeted unit test
integration smoke when boundaries changed
Docker build when packaging changes
Docker smoke when runtime packaging changes
stress/load only when phase risk requires it
```

Command:

```powershell
python scripts\record_test_result.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --name syntax `
  --command "<command run>" `
  --status pass `
  --exit-code 0 `
  --notes "Syntax check passed"
```

Gate rule:

- Missing tests are not pass.
- A phase with only `skipped` checks blocks.
- A skipped required check requires an accepted-risk decision.

## Phase 5B - Reviewer Agent

Goal: review correctness, architecture fit, and minimal-code discipline.

Role output:

```text
.qc/phase-runs/<phase-id>/reviewer-report.md
```

Required verdict:

```text
Verdict: pass
```

Gate rule:

- `Verdict: pending`, `revise`, or `block` fails strict gate.

## Phase 5C - Compliance Agent

Goal: verify process, approvals, safety, and record completeness.

Checks:

- build-plan adherence
- protected zones
- user approvals
- no secrets in `.qc/`
- no remote/API surface without approval
- accepted-risk records include human decision proof

Required verdict:

```text
Verdict: pass
```

Gate rule:

- A blocker deviation fails strict gate unless tied to a valid `.qc/decision-log.jsonl` accepted-risk record.

## Phase 5D - Integration Agent

Goal: confirm previous/current/next phase seams.

Questions:

- What did the previous phase promise?
- What does this phase change?
- What must the next phase receive?
- Are schema, config, migration, docs, tests, and debug paths compatible?
- What would break if the next phase started now?

Required verdict:

```text
Verdict: pass
```

Gate rule:

- Missing, pending, revise, or block seam audit blocks completion.

## Phase 5E - Release Agent

Goal: verify runtime, Docker, API, deployment, and production-debug readiness when relevant.

Run this role when the phase touches:

- runtime packaging
- Docker
- dependencies
- APIs
- services
- deployment behavior
- production debug
- rollback
- logging
- feature flags

Required verdict:

```text
Verdict: pass
```

Release strict validation:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety `
  --strict-gate `
  --release-phase
```

Gate rule:

- `Verdict: not_applicable` is allowed only when `release_required=false`.
- If runtime impact is uncertain, default to `release_required=true` until the controller records why release evidence is not applicable.

## Phase 6 - In-Progress Validation

Goal: catch missing records early.

Command:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety
```

Expected behavior:

- warnings are allowed while role reports are still pending
- errors should stop the phase and be fixed or recorded as blockers

Gate rule:

- Do not claim completion from in-progress validation.

## Phase 7 - Strict Gate Validation

Goal: make a hard phase decision.

Command:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety `
  --strict-gate
```

Release/runtime command:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety `
  --strict-gate `
  --release-phase
```

Strict gate blocks when:

- required files are missing
- required role verdicts are `pending`, `revise`, or `block`
- latest Ponytail verdict is not `pass`
- no test result exists
- all required tests are skipped
- any recorded test failed
- unaccepted blocker deviation exists
- accepted-risk claim lacks matching decision-log entry
- safety scan finds banned markers
- release phase lacks completed release evidence

## Phase 8 - Revise Loop

Goal: fix only the smallest failing item.

Loop cap:

```text
attempt 1 -> fix smallest failing item -> rerun affected proof
attempt 2 -> narrow blocker -> rerun affected proof
attempt 3 -> pass, block, or ask for human accepted-risk decision
```

State:

```json
{
  "current_phase_status": "revising",
  "revise_attempts": 1,
  "max_revise_attempts": 3
}
```

Gate rule:

- After three failed revise attempts, block.
- Do not keep retrying silently.
- Raising the cap requires an explicit human decision.

## Phase 9 - Accepted Risk Path

Goal: allow progress only when the user explicitly accepts incomplete proof.

Required decision-log fields:

```json
{
  "decision_id": "decision-001",
  "phase_id": "<phase-id>",
  "decision_type": "accepted_with_risk",
  "accepted_by": "<human approver>",
  "risk": "<what remains unverified>",
  "impact": "<blast radius>",
  "reason": "<why accepted>",
  "owner": "<follow-up owner>",
  "deadline": "<date or phase>",
  "rollback": "<rollback or containment path>",
  "follow_up": "<next required check>"
}
```

Gate rule:

- The controller cannot self-approve accepted risk.
- A boolean in `deviation-log.jsonl` is not enough without a matching decision-log record.

## Phase 10 - Final Gate State Update

Goal: make durable state match the gate outcome.

For `pass`:

```json
{
  "current_phase_status": "complete",
  "latest_gate_decision": "pass",
  "latest_gate_at": "<UTC timestamp>",
  "blocking_issues": []
}
```

For `block`:

```json
{
  "current_phase_status": "blocked",
  "latest_gate_decision": "block",
  "latest_gate_at": "<UTC timestamp>",
  "blocking_issues": ["<blocker summary>"]
}
```

For `accepted_with_risk`:

```json
{
  "current_phase_status": "complete",
  "latest_gate_decision": "accepted_with_risk",
  "latest_gate_at": "<UTC timestamp>",
  "blocking_issues": [],
  "accepted_risk_decision_id": "<decision-id>"
}
```

Gate rule:

- No next phase starts while `phase-board.json` still says `open` and `latest_gate_decision=pending`.

## Phase 11 - User-Facing Report

Goal: close the phase clearly.

Report:

- phase id and title
- files changed
- commands run
- Ponytail verdict
- test summary
- reviewer/compliance/seam/release verdicts
- strict gate command and result
- final gate decision
- phase-board update status
- next phase recommendation

Do not say "complete" unless strict validation and final phase-board update are complete.

## Phase 12 - Next Phase Handoff

Goal: make the next phase safe to start.

Handoff package:

- current phase gate result
- unresolved issues
- accepted-risk follow-ups
- next phase id and objective
- next phase inputs from seam audit
- release/debug concerns if any

Gate rule:

- The next phase can start only after `pass` or valid `accepted_with_risk`.
- `revise` stays inside the current phase.
- `block` stops the build until the blocker is resolved or explicitly accepted by the user.

## One-Page Run Order

```text
0. Intake and choose one phase
1. init_qc.py
2. start_phase.py
3. builder-agent creates candidate
4. ponytail-adapter gates scope/minimal-code
5. evidence fan-out, sequential in V01
   5A. test-agent
   5B. reviewer-agent
   5C. compliance-agent
   5D. integration-agent
   5E. release-agent when release_required=true
6. validate in progress
7. validate strict gate
8. revise loop, max 3 failed attempts
9. accepted-risk path only with human decision-log proof
10. update phase-board final state
11. report gate result
12. hand off next phase
```

## Recommended Prompt

```text
Use builder-team-qc for this build.
Target root: <target project path>
Build plan: <plan path or phase summary>
Current phase: <phase id and title>
Next phase: <next phase id or unknown>
Run the latest phase-by-phase controller plan:
- initialize or verify .qc
- start/resume the phase
- run builder-agent
- run Ponytail before test/review fan-out
- run tests, reviewer, compliance, seam audit, and release gate when required
- run strict validation, using --release-phase when release_required=true
- cap revise loop at three failed attempts
- require decision-log proof for accepted_with_risk
- update phase-board final gate state before allowing the next phase
```

## Current Implementation Note

The latest documentation defines the desired deterministic contract. Two helper scripts are still planned for a stronger implementation:

- `record_decision.py` for decision-log and accepted-risk records
- `record_gate_decision.py` for final phase-board transitions

Until those exist, the controller must write those records manually and disclose that manual step in the phase report.
