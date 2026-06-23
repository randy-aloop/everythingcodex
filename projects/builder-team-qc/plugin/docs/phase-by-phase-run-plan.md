# Builder Team QC Phase-by-Phase Run Plan

Version: V02
Updated: 2026-06-23
Supersedes: V01

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
    -> pre-build plan check
    -> builder-agent creates candidate work
    -> changed-files/diff evidence is persisted
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
5. Run the pre-build plan check.
6. Record assumptions in the phase record or deviation log.

Do not start implementation if the phase cannot be named.

Pre-build plan check:

| Check | Gate meaning |
| --- | --- |
| Current phase is named | Required before implementation. |
| Deliverables are scoped to one phase | Block or record deviation when the work spans multiple phases. |
| Required evidence is known | Block if there is no meaningful way to prove the phase. |
| Release impact is classified | Default to `release_required=true` when runtime impact is uncertain. |
| Protected zones are identified | Stop for approval before writes. |
| Existing failures are noted | Baseline failures must not be hidden as new proof. |

Record the pre-build plan check in `phase-record.md`. If the check finds a blocker, open an issue in `.qc/issue-register.jsonl` and do not continue to builder work.

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
  lessons-learned.jsonl
  deviation-log.jsonl
  decision-log.jsonl
  ponytail-events.jsonl
  test-results/
  phase-runs/
```

Gate rule:

- If `.qc/` cannot be created or inspected, stop and report `block`.

Confirmed current helper gap: `init_qc.py` creates the core JSONL files, but does not yet seed `lessons-learned.jsonl`. Create it manually when a phase records process lessons.

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
  changed-files.json
  implementation-diff.patch
  reviewer-report.md
  test-report.md
  compliance-report.md
  seam-audit.md
  release-gate.md
  gate-summary.md
  evidence/
```

Confirmed current helper gap: `start_phase.py` creates the phase markdown files and `evidence/`, but it does not yet create `changed-files.json`, `implementation-diff.patch`, or `gate-summary.md`. The controller must create those manually until helper support exists.

Manual phase-board contract until helper support exists:

```json
{
  "schema_version": "1.0",
  "current_phase_id": "<phase-id>",
  "current_phase_status": "open",
  "next_phase_id": "<next-phase-id>",
  "latest_gate_decision": "pending",
  "latest_gate_at": "",
  "release_required": false,
  "release_not_applicable_rationale": "<required when release_required=false>",
  "revise_attempts": 0,
  "max_revise_attempts": 3,
  "required_evidence": [
    "phase-record.md",
    "builder-notes.md",
    "changed-files.json",
    "implementation-diff.patch",
    "ponytail-events.jsonl",
    "test-results/<phase-id>.jsonl",
    "reviewer-report.md",
    "compliance-report.md",
    "seam-audit.md"
  ],
  "blocking_issues": [],
  "accepted_risk_decision_id": "",
  "updated_at": "<UTC timestamp>"
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
.qc/phase-runs/<phase-id>/changed-files.json
.qc/phase-runs/<phase-id>/implementation-diff.patch
candidate source/document changes
```

Gate rule:

- Builder output is evidence, not a gate decision.
- If implementation needs scope beyond the phase, record a deviation before continuing.
- The reviewer and compliance roles must read the persisted changed-file/diff evidence, not only a chat summary.

Current helper gap:

- There is no dedicated diff recorder yet. Until one exists, the controller must create or refresh `changed-files.json` and `implementation-diff.patch` manually after builder work and after each revise attempt.

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
- The Ponytail event should include the current attempt number and mode source. Current helper support is incomplete, so record missing attempt/mode-source details in `phase-record.md` when the JSONL event cannot carry them.
- Upstream Ponytail hooks are off by default. They require an explicit review id and user approval before being treated as executable tooling.

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

Current helper gap:

- Confirmed current `record_test_result.py` supports `--name`, `--command`, `--status`, `--exit-code`, `--output-file`, and `--notes`.
- It does not yet support `--required` or `--attempt`.
- Until that support exists, the controller must write required status and attempt number in `test-report.md`.

Target command contract after helper hardening:

```powershell
python scripts\record_test_result.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --attempt 1 `
  --name syntax `
  --command "<command run>" `
  --status pass `
  --exit-code 0 `
  --required `
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
- When `release_required=false`, `release-gate.md` must include `Release Required: false`, `Not Applicable Rationale`, `Checked By`, and `Checked At`, and the same rationale must be copied to `phase-board.json`.

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
- required role verdicts are missing, duplicated, unknown, `pending`, `revise`, or `block`
- latest Ponytail verdict is not `pass`
- no test result exists
- all required tests are skipped
- any recorded test failed
- a blocker issue remains open in `.qc/issue-register.jsonl`
- unaccepted blocker deviation exists
- accepted-risk claim lacks matching decision-log entry
- safety scan finds banned markers
- release phase lacks completed release evidence

Exit-code handling:

- Confirmed current `validate_phase_record.py` returns `0` when no errors are present and `1` for any validation error.
- Target contract is `0` pass, `10` strict-gate failure, `20` schema/config/invocation error, and `30` safety blocker.
- Until target exit codes are implemented, the controller must read the validator output and record the observed exit code plus the interpreted failure class in `gate-summary.md`.

## Phase 8 - Revise Loop

Goal: fix only the smallest failing item.

Loop cap:

```text
attempt 1 -> fix smallest failing item -> rerun affected proof by default
attempt 2 -> narrow blocker -> rerun affected proof by default
attempt 3 -> pass, block, or ask for human accepted-risk decision
```

State:

```json
{
  "schema_version": "1.0",
  "current_phase_id": "<phase-id>",
  "current_phase_status": "revising",
  "latest_gate_decision": "revise",
  "latest_gate_at": "<UTC timestamp>",
  "revise_attempts": 1,
  "max_revise_attempts": 3,
  "blocking_issues": ["<issue-id or summary>"],
  "updated_at": "<UTC timestamp>"
}
```

Gate rule:

- After three failed revise attempts, block.
- Do not keep retrying silently.
- Raising the cap requires an explicit human decision.
- Rerun the full proof set, not only affected proof, when the fix touches shared contracts, schema, runtime behavior, dependencies, Docker, safety policy, release behavior, or when the affected scope is uncertain.
- Record each failed attempt in `phase-board.json`, `.qc/issue-register.jsonl`, and the relevant role report.

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
- `accepted_with_risk` must reference a human decision id in both the deviation or issue record and `phase-board.json`.

Target helper contract:

```powershell
python scripts\record_decision.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --decision-type accepted_with_risk `
  --accepted-by "<human approver>" `
  --risk "<what remains unverified>" `
  --impact "<blast radius>" `
  --reason "<why accepted>" `
  --owner "<follow-up owner>" `
  --deadline "<date or phase>" `
  --rollback "<rollback path>" `
  --follow-up "<next required check>"
```

Current helper gap:

- `record_decision.py` does not exist yet. Until it exists, append the JSONL record manually and disclose that manual action in the user-facing report.

## Phase 10 - Final Gate State Update

Goal: make durable state match the gate outcome.

For `pass`:

```json
{
  "schema_version": "1.0",
  "current_phase_id": "<phase-id>",
  "current_phase_status": "complete",
  "next_phase_id": "<next-phase-id>",
  "latest_gate_decision": "pass",
  "latest_gate_at": "<UTC timestamp>",
  "release_required": false,
  "release_not_applicable_rationale": "<required when release_required=false>",
  "revise_attempts": 0,
  "max_revise_attempts": 3,
  "required_evidence": ["<evidence paths>"],
  "blocking_issues": [],
  "accepted_risk_decision_id": "",
  "updated_at": "<UTC timestamp>"
}
```

For `block`:

```json
{
  "schema_version": "1.0",
  "current_phase_id": "<phase-id>",
  "current_phase_status": "blocked",
  "next_phase_id": "<next-phase-id>",
  "latest_gate_decision": "block",
  "latest_gate_at": "<UTC timestamp>",
  "release_required": false,
  "release_not_applicable_rationale": "<required when release_required=false>",
  "revise_attempts": 3,
  "max_revise_attempts": 3,
  "required_evidence": ["<evidence paths>"],
  "blocking_issues": ["<issue-id or blocker summary>"],
  "accepted_risk_decision_id": "",
  "updated_at": "<UTC timestamp>"
}
```

For `accepted_with_risk`:

```json
{
  "schema_version": "1.0",
  "current_phase_id": "<phase-id>",
  "current_phase_status": "complete",
  "next_phase_id": "<next-phase-id>",
  "latest_gate_decision": "accepted_with_risk",
  "latest_gate_at": "<UTC timestamp>",
  "release_required": false,
  "release_not_applicable_rationale": "<required when release_required=false>",
  "revise_attempts": 0,
  "max_revise_attempts": 3,
  "required_evidence": ["<evidence paths>"],
  "blocking_issues": [],
  "accepted_risk_decision_id": "<decision-id>",
  "updated_at": "<UTC timestamp>"
}
```

Gate rule:

- No next phase starts while `phase-board.json` still says `open` and `latest_gate_decision=pending`.

Target helper contract:

```powershell
python scripts\record_gate_decision.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --decision pass `
  --validator-exit-code 0 `
  --summary "<short gate summary>"
```

Current helper gap:

- `record_gate_decision.py` does not exist yet. Until it exists, update `phase-board.json` and write `gate-summary.md` manually.

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

Use the existing summary helper before writing the final report:

```powershell
python scripts\summarize_phase.py `
  --root <target-project> `
  --phase-id <phase-id>
```

Confirmed current behavior: `summarize_phase.py` prints JSON to stdout and does not write a file. Capture or paste the summary into `gate-summary.md`.

If the phase reveals a reusable process lesson, append it to `.qc/lessons-learned.jsonl`. Lessons do not satisfy or bypass current blockers.

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
0A. Run pre-build plan check and open blocker issues if needed
1. init_qc.py
2. start_phase.py
3. builder-agent creates candidate
4. persist changed-files/diff evidence
5. ponytail-adapter gates scope/minimal-code
6. evidence fan-out, sequential in V01
   6A. test-agent
   6B. reviewer-agent
   6C. compliance-agent
   6D. integration-agent
   6E. release-agent when release_required=true
7. validate in progress
8. validate strict gate
9. revise loop, max 3 failed attempts
10. accepted-risk path only with human decision-log proof
11. update phase-board final state
12. summarize and report gate result
13. hand off next phase
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
- run the pre-build plan check
- start/resume the phase
- run builder-agent
- persist changed-files/diff evidence
- run Ponytail before test/review fan-out
- run tests, reviewer, compliance, seam audit, and release gate when required
- run strict validation, using --release-phase when release_required=true
- cap revise loop at three failed attempts
- require decision-log proof for accepted_with_risk
- write gate-summary.md and update phase-board final gate state before allowing the next phase
```

## Current Implementation Note

The latest documentation defines the desired deterministic contract. Two helper scripts are still planned for a stronger implementation:

- `record_decision.py` for decision-log and accepted-risk records
- `record_gate_decision.py` for final phase-board transitions

Until those exist, the controller must write those records manually and disclose that manual step in the phase report.
