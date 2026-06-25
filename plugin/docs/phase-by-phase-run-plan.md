# Builder Team QC Phase-by-Phase Run Plan

Version: V05
Updated: 2026-06-24
Supersedes: V04

This is the latest detailed operating plan for running Builder Team QC phase by phase.

Document V05 describes the current Runtime V01 control model unless a later runtime version is explicitly named.

Builder Team QC has two layers:

1. Product phases: the user's actual build plan, such as scaffold plugin, add scripts, add docs, run sample project, harden gates, or prepare release.
2. QC phase loop: the repeated builder-team process used to complete each product phase safely.

The product phase changes every time. The QC loop stays the same.

## Control Model

```text
user goal
  -> phase-controller
    -> choose one phase
    -> pre-build plan check, no durable writes yet
    -> initialize .qc
    -> open one phase and persist pre-build findings
    -> builder-agent creates candidate work
    -> changed-files/diff evidence is persisted
    -> ponytail-adapter checks minimal-code discipline
    -> evidence fan-out runs sequentially in V01
    -> strict gate decides pass / revise / block / accepted_with_risk
    -> phase-board records final state
  -> next phase only when allowed
```

V01 is local-only. It does not launch remote agents, expose an API server, call A2A, call remote MCP, require API keys, or use public tunnels. Codex remains the visible controller.

## V04 Field Lesson - Phase 6 Safety Scan Classification

During the `phase-002` run, Phase 6 initially blocked on safety scan findings that were policy documentation, reference URLs, and scanner self-definitions rather than active risky behavior.

Observed Phase 6 blocker:

```text
warning: pending verdict remains in phase-record.md
error: safety scan found 12 banned markers
failed
```

Root cause:

- The scanner treated every banned-pattern match as a blocker.
- It could not distinguish policy-deny text such as "No remote A2A agents" from executable remote-agent setup.
- It could not distinguish GitHub attribution/reference URLs from runtime endpoints.
- It self-detected `BANNED_PATTERNS` definitions in `scripts/builder_team_qc_lib.py`.

V04 solution:

- Keep banned patterns.
- Classify every safety finding with `severity` and `reason`.
- Use `blocker` only for active secrets, active credentials, active remote execution/configuration, unsafe executor setup, or remote Docker configuration.
- Use `warning` for risky terms in review-worthy docs/config context that do not look active.
- Use `info` for scanner self-definitions, policy-deny documentation, and safe attribution/reference links.
- Phase 6 and Phase 7 fail only when safety findings include `severity=blocker`.

Required scanner output shape:

```json
{
  "severity": "info",
  "kind": "remote_url",
  "file": "docs/orchestration-notes.md",
  "line": 12,
  "reason": "reference URL in documentation",
  "text": "..."
}
```

Controller rule:

- If Phase 6 blocks on safety findings, inspect `.qc/safety-scan-findings.json`.
- If findings are false positives caused by scanner context blindness, stop and report the proposed classifier change before editing scanner behavior.
- After an approved safety-policy change, rerun the full proof set, not only the affected proof.
- Record the blocker, fix rationale, affected build area, consequence, and final-result impact in `phase-record.md`, `.qc/issue-register.jsonl`, `gate-summary.md`, and the phase-by-phase build log.

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
- open/applicable lessons from `.qc/lessons-learned.jsonl`, when the file already exists

Controller actions:

1. Read the build plan.
2. Identify the current phase only.
3. Decide whether `release_required=true`.
4. Set `max_revise_attempts=3` unless the user explicitly sets a lower cap.
5. Read open/applicable lessons if `.qc/lessons-learned.jsonl` already exists.
6. Run the pre-build plan check in memory.
7. Hold assumptions, lesson inputs, and blockers as provisional findings until Phase 1 and Phase 2 create durable records.

Do not start implementation if the phase cannot be named.

Phase 0 does not write to `.qc/issue-register.jsonl`, `.qc/deviation-log.jsonl`, or `phase-record.md`, because those durable records may not exist yet. If Phase 0 finds a blocker, stop before implementation. After Phase 1 initializes `.qc/` and Phase 2 creates the phase run, persist the provisional findings to `phase-record.md`, `.qc/issue-register.jsonl`, and `.qc/deviation-log.jsonl` as applicable.

Pre-build plan check:

| Check | Gate meaning |
| --- | --- |
| Current phase is named | Required before implementation. |
| Deliverables are scoped to one phase | Block or record deviation when the work spans multiple phases. |
| Required evidence is known | Block if there is no meaningful way to prove the phase. |
| Release impact is classified | Default to `release_required=true` when runtime impact is uncertain. |
| Protected zones are identified | Stop for approval before writes. |
| Existing failures are noted | Baseline failures must not be hidden as new proof. |

Hold the pre-build plan check result as provisional evidence. Persist it in `phase-record.md` during Phase 2. If the check finds a blocker, open the issue in `.qc/issue-register.jsonl` after `.qc/` exists, then do not continue to builder work.

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

Target layout after `init_qc.py` plus manual controller records:

```text
.qc/
  phase-board.json
  qc-config.json
  issue-register.jsonl
  lessons-learned.jsonl (manual until helper support exists)
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

Target phase-run layout after `start_phase.py` plus manual controller records:

```text
.qc/phase-runs/<phase-id>/
  phase-record.md
  builder-notes.md
  changed-files.json (manual until helper support exists)
  implementation-diff.patch (manual until helper support exists)
  reviewer-report.md
  test-report.md
  compliance-report.md
  seam-audit.md
  release-gate.md
  gate-summary.md (manual until helper support exists)
  evidence/
```

Confirmed current helper gap: `start_phase.py` creates the phase markdown files and `evidence/`, but it does not yet create `changed-files.json`, `implementation-diff.patch`, or `gate-summary.md`. The controller must create those manually until helper support exists.

Manual phase-board contract until helper support exists:

`release_not_applicable_rationale` is always present. When `release_required=false`, it must contain the release not-applicable rationale. When `release_required=true`, set it to an empty string and put release evidence in `release-gate.md`.

```json
{
  "schema_version": "1.0",
  "current_phase_id": "<phase-id>",
  "current_phase_status": "open",
  "next_phase_id": "<next-phase-id>",
  "latest_gate_decision": "pending",
  "latest_gate_at": "",
  "release_required": false,
  "release_not_applicable_rationale": "<rationale when release_required=false; empty string when true>",
  "revise_attempts": 0,
  "max_revise_attempts": 3,
  "required_evidence": [
    "phase-record.md",
    "builder-notes.md",
    "changed-files.json",
    "implementation-diff.patch",
    "ponytail-events.jsonl",
    "test-report.md",
    "test-results/<phase-id>.jsonl",
    "reviewer-report.md",
    "compliance-report.md",
    "seam-audit.md",
    "release-gate.md",
    "gate-summary.md"
  ],
  "blocking_issues": [],
  "accepted_risk_decision_id": "",
  "updated_at": "<UTC timestamp>"
}
```

Gate rule:

- No role work starts until the phase run exists.
- Persist Phase 0 provisional findings to `phase-record.md`, `.qc/issue-register.jsonl`, and `.qc/deviation-log.jsonl` before builder work starts.
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

Confirmed current helper behavior:

- `record_test_result.py` supports `--name`, `--command`, `--status`, `--attempt`, `--required`, `--exit-code`, `--output-file`, and `--notes`.
- It writes `attempt` and `required` into `.qc/test-results/<phase-id>.jsonl`.
- When `.qc/phase-runs/<phase-id>/test-report.md` exists, it also appends the recorded JSON there.

Current command contract:

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

Required verdict when `release_required=true`:

```text
Verdict: pass
```

Allowed verdict when `release_required=false`:

```text
Verdict: not_applicable
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
- When `release_required=true`, `release_not_applicable_rationale` in `phase-board.json` must be an empty string and `release-gate.md` must use `Verdict: pass`.

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

- warning-only pending role reports are allowed while `--strict-gate` is absent
- errors should stop the phase and be fixed or recorded as blockers
- safety scan findings must include `severity` and `reason`
- non-blocking safety findings produce warnings, not errors

Gate rule:

- Do not claim completion from in-progress validation.
- With the current validator, non-strict validation returns exit `0` when only warnings are present.
- With the current validator, non-strict validation returns exit `1` when actual errors are present, such as missing required files, missing Ponytail event, failed tests, unaccepted blocker deviations, release-phase errors, or safety scan blocker findings.
- Safety scan findings with `severity=warning` or `severity=info` do not block by themselves, but they must be written to `.qc/safety-scan-findings.json` for review.

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
- `release-gate.md` uses `Verdict: not_applicable` while `release_required=true`
- `release-gate.md` uses `Verdict: not_applicable` while `release_required=false` but lacks the required rationale block
- latest Ponytail verdict is not `pass`
- no test result exists
- all required tests are skipped
- any recorded test failed
- a blocker issue remains open in `.qc/issue-register.jsonl`
- unaccepted blocker deviation exists
- accepted-risk claim lacks matching decision-log entry
- safety scan finds one or more `severity=blocker` findings
- release phase lacks completed release evidence

Exit-code handling:

- Confirmed current `validate_phase_record.py` returns `0` when no errors are present and `1` for any validation error.
- Confirmed current non-strict behavior: pending role reports are warnings, not errors, when `--strict-gate` is absent.
- Confirmed V04 safety scan behavior: non-blocking safety findings are warnings; blocker safety findings are errors.
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
  "timestamp": "<UTC timestamp>",
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

Current helper contract:

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

Confirmed current helper behavior:

- `record_decision.py` should be used for accepted-risk and approval records. Manual JSONL edits are fallback-only and must be disclosed.
- `--decision-id` is optional; when omitted, the helper generates the next stable decision id for the phase.
- The helper writes the current UTC timestamp into the JSONL record.
- Add `--json` when the controller needs machine-readable output for a phase report.

## Phase 10 - Final Gate State Update

Goal: make durable state match the gate outcome.

In all final phase-board examples, `release_not_applicable_rationale` means: rationale text when `release_required=false`; empty string when `release_required=true`.

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
  "release_not_applicable_rationale": "<rationale when release_required=false; empty string when true>",
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
  "release_not_applicable_rationale": "<rationale when release_required=false; empty string when true>",
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
  "release_not_applicable_rationale": "<rationale when release_required=false; empty string when true>",
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

Current helper contract:

```powershell
python scripts\record_gate_decision.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --gate pass `
  --next-phase-id <next-phase-id> `
  --note "<short gate summary>"
```

Confirmed current helper behavior:

- `record_gate_decision.py` exists and should be used to update `phase-board.json`, append `gate-events.jsonl`, and write `gate-summary.md`. Manual edits are fallback-only and must be disclosed.
- For `accepted_with_risk`, pass `--decision-id <decision-id>` so the helper can verify a matching decision-log entry.
- Add `--json` when the controller needs machine-readable output for a phase report.

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

If the phase reveals a reusable process lesson, append it to `.qc/lessons-learned.jsonl`. Lessons do not satisfy or bypass current blockers. Phase 0 of the next run must read open/applicable lessons and either apply them to the new phase plan or record why they do not apply.

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
0A. Run pre-build plan check in memory, no durable writes yet
1. init_qc.py
2. start_phase.py
2A. Persist Phase 0 findings to phase-record, issue register, or deviation log
3. builder-agent creates candidate
3A. persist changed-files/diff evidence
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
11. summarize and report gate result
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
- run the pre-build plan check in memory
- initialize or verify .qc
- start/resume the phase
- persist pre-build findings after records exist
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

The latest documentation defines the deterministic contract. Two helper scripts now implement the strongest current state path:

- `record_decision.py` for decision-log and accepted-risk records
- `record_gate_decision.py` for final phase-board transitions

Until those exist, the controller must write those records manually and disclose that manual step in the phase report.
