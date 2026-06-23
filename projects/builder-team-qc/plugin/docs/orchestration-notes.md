# Orchestration Notes

These notes describe how `builder-team-qc` should run a builder-teams multiagent Ponytail phase.

V01 is intentionally local and evidence-first. It borrows the useful orchestration ideas from Google ADK, but it does not run a remote ADK service, does not expose an API server, and does not require API keys. Codex is the visible controller, role skills are the builder-team contracts, scripts are explicit tools, and `.qc/` is the shared state.

For renderable diagrams of this flow, see `docs/orchestration-diagram.md`.

## Core Principle

One phase is the unit of control.

```text
phase-controller owns the gate
roles produce evidence
scripts write durable records
.qc stores shared state
strict validation decides whether the phase can complete
```

No role is allowed to silently advance the build. No next phase starts until the current phase has a `pass` gate or an explicitly recorded `accepted_with_risk` decision in `.qc/decision-log.jsonl`.

## Controller Stack

```text
User intent
  -> Codex conversation
    -> builder-team-qc plugin
      -> phase-controller skill
        -> role skills
          -> local scripts
            -> .qc evidence
        -> strict gate validation
    -> user-facing decision
```

The controller does not own product code. The target project remains the source of truth for implementation files, tests, Docker files, runtime configuration, and release behavior.

## Default Orchestration Mode

The default mode is a sequential phase pipeline with optional parallel-style review checks and a bounded revise loop.

```text
Sequential open:
  read plan -> init .qc -> start phase -> identify deliverables

Sequential build:
  builder implementation -> Ponytail check -> tests

Parallel-style evidence checks:
  reviewer
  compliance
  integration seam audit
  release/debug gate when applicable

Loop:
  validate -> revise smallest failing item -> validate again, max 3 failed attempts

Final:
  pass, revise, block, or accepted_with_risk -> phase-board final transition
```

In V01, Codex performs the parallel-style checks one after another unless a future runtime adds real concurrency. The control rule is still parallel-agent shaped: all required branches must join before the gate can pass.

## Intake Checklist

Before opening a phase, the controller should identify:

| Field | Required value |
| --- | --- |
| Target root | Project directory that will receive `.qc/`. |
| Build plan | Plan file or phase summary. |
| Phase id | Stable id such as `phase-001`. |
| Phase title | Human-readable objective. |
| Next phase id | Empty if unknown, otherwise the next planned phase. |
| Ponytail mode | `task-scoped`, `project-agents`, `contained-workspace`, or `unavailable-fallback`. |
| Runtime impact | Whether the phase touches Docker, dependencies, APIs, runtime, deploy, or production behavior. |
| Release required | `true` when runtime impact requires a completed `release-gate.md` and release-aware strict validation. |
| Max revise attempts | Default `3`; lower when risk is high. Raising the cap requires an explicit user decision. |
| Required tests | Commands or checks expected for this phase. |
| Protected zones | Any files/areas that need explicit approval before writes. |
| Known risks | Open assumptions, missing approvals, or possible blockers. |

If any intake item is unknown, the controller may start with a conservative default, but it must record the assumption in the phase record or deviation log. Conservative defaults are: `release_required=false` only when no runtime/release signal exists, `max_revise_attempts=3`, and required tests are whatever the build plan or project tooling makes meaningful for the phase.

## Phase Run Sequence

### 1. Initialize QC State

Create or verify the `.qc/` evidence structure.

```powershell
python scripts\init_qc.py --root <target-project>
```

Expected result:

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

### 2. Start Or Resume The Phase

Open the phase run directory and seed required role reports.

```powershell
python scripts\start_phase.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --title "<phase-title>" `
  --next-phase-id <next-phase-id> `
  --build-plan "<plan path or phase summary>"
```

Expected result:

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

The phase board should also carry the current gate contract:

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

If helper support for those fields is not implemented yet, the controller must maintain them manually in `.qc/phase-board.json` and say so in the gate summary.

### 3. Apply Builder Role

The builder role implements only the current phase. It should:

- Read the phase plan and target files.
- Avoid unrelated refactors.
- Prefer smallest correct change.
- Record touched files and runnable proof in `builder-notes.md`.
- Log deviations when the plan cannot be followed.

Builder output is not a gate decision. It is evidence for later checks.

### 4. Apply Ponytail Discipline

Ponytail is instruction discipline by default, not trusted automation.

Ponytail applies to the builder output and the phase gate. It is not owned by the test role. The test role usually runs after the Ponytail check because testing a deliberately over-scoped or over-abstracted change can waste time, but the Ponytail result is also evidence for reviewer, compliance, and the controller's final gate.

Allowed modes:

| Mode | Use when |
| --- | --- |
| `task-scoped` | Ponytail rules apply only to this build session. |
| `project-agents` | Project-local instructions carry Ponytail behavior. |
| `contained-workspace` | Ponytail is used only in a contained reviewed workspace. |
| `unavailable-fallback` | Ponytail is unavailable, so the local checklist is used. |

Record the check:

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

The gate cannot pass if the latest Ponytail event for the phase is missing or not `pass`.

### 5. Run And Record Tests

The test role should run the quickest meaningful checks first. Missing commands are not considered a pass; they should be recorded as skipped or not configured with a reason.

Record each result:

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

Recommended test ladder:

```text
syntax or compile
targeted unit test
integration smoke
Docker build when runtime packaging changes
Docker smoke when runtime packaging changes
stress check only when required by phase risk
```

Strict gate requires at least one required non-skipped passing check. A phase with only `skipped` checks is blocked unless the user explicitly accepts the risk in `.qc/decision-log.jsonl`.

### 6. Apply Reviewer Role

The reviewer checks:

- Architecture fit.
- Minimal-code discipline.
- Unrelated refactors.
- Error handling.
- Test adequacy.
- Whether the diff matches the phase plan.

The reviewer writes `reviewer-report.md` and should choose a verdict of `pass`, `revise`, or `block`. Strict gate treats `revise` and `block` as failures, not completed evidence.

### 7. Apply Compliance Role

The compliance role checks:

- Build-plan adherence.
- Required evidence exists.
- Protected zones were respected.
- User approvals are recorded.
- No secrets are stored in `.qc/`.
- Remote/API surfaces are not introduced without explicit approval.

The compliance role writes `compliance-report.md` and updates deviation or decision logs when needed. Strict gate treats `revise` and `block` as failures, not completed evidence.

### 8. Apply Integration Seam Role

The integration role checks previous/current/next phase compatibility.

It should answer:

```text
What did the previous phase promise?
What does this phase change?
What must the next phase receive?
Are schemas, config, migrations, docs, tests, and debug paths compatible?
What would break if the next phase started now?
```

The integration role writes `seam-audit.md`. A missing, pending, `revise`, or `block` seam audit blocks phase completion.

### 9. Apply Release Role When Applicable

Use release checks when the phase touches:

- Docker or runtime packaging.
- Dependencies.
- APIs.
- Services.
- Deployment behavior.
- Production debug behavior.
- Logging, rollback, or feature flags.

The release role writes `release-gate.md` and should verify:

- Logs are available and do not leak secrets.
- Debug flags are explicit and safe by default.
- Rollback or disable path exists.
- Docker/container health is inspectable when applicable.
- No production-only behavior is hidden from local validation.

When `release_required=true`, strict validation must run in release-aware mode. With the current validator, that means adding `--release-phase`. A release/runtime phase cannot pass with `release-gate.md` still pending or `Verdict: not_applicable`.

### 10. Validate While In Progress

Run validation during the phase to find missing records early.

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety
```

This mode may warn about pending role reports while work is still in progress.

### 11. Validate Strict Gate Before Completion

Before saying the phase is complete, run:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety `
  --strict-gate
```

For release/runtime phases, run:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety `
  --strict-gate `
  --release-phase
```

Strict gate fails when:

- Required phase files are missing.
- Required role verdicts are pending, `revise`, or `block`.
- Ponytail evidence is missing or not pass.
- Test results are missing.
- A recorded test failed.
- Required tests are only skipped.
- An unaccepted blocker deviation exists.
- An accepted-risk claim lacks a matching `.qc/decision-log.jsonl` human decision with impact, owner, deadline, rollback, and follow-up.
- A safety scan blocker exists.
- A release phase lacks completed release evidence.

## Gate Outcomes

| Gate | Meaning | Controller action |
| --- | --- | --- |
| `pass` | Required evidence is complete and checks pass. | Summarize evidence, update `.qc/phase-board.json`, and allow next phase. |
| `revise` | A local fix is needed. | Identify smallest repair and loop back to builder/test/review. |
| `block` | A requirement, approval, safety condition, or seam prevents progress. | Stop and report exact blocker. |
| `accepted_with_risk` | User explicitly accepts incomplete verification. | Record human decision with risk, owner, deadline, rollback, and next required check before allowing next phase. |

`accepted_with_risk` is a gate bypass. The controller must not self-approve it. The decision record should include `decision_id`, `phase_id`, `accepted_by`, `risk`, `impact`, `reason`, `owner`, `deadline`, `rollback`, and `follow_up`.

## Final Gate State Update

After `pass` or `accepted_with_risk`, update `.qc/phase-board.json` so durable state no longer says the phase is still open or pending.

Minimum final fields:

```json
{
  "current_phase_id": "<phase-id>",
  "current_phase_status": "complete",
  "latest_gate_decision": "pass",
  "latest_gate_at": "<UTC timestamp>",
  "next_phase_id": "<next-phase-id>",
  "revise_attempts": 0,
  "blocking_issues": []
}
```

If the gate is `block`, set `current_phase_status` to `blocked`, keep `latest_gate_decision=block`, and list the blocker ids or summaries in `blocking_issues`.

## Revise Loop

Use a bounded loop. Do not retry blindly.

```text
attempt 1:
  fix smallest failing item
  rerun affected tests
  rerun affected role checks
  strict validate

attempt 2:
  narrow the blocker
  log deviation if plan changed
  rerun proof
  strict validate

attempt 3:
  either pass, block, or ask for accepted-risk approval
```

The controller should block rather than keep looping when the same condition fails repeatedly. Track `revise_attempts` in `.qc/phase-board.json`; after three failed attempts, block and ask for a human decision before continuing.

## Shared State Contract

| Producer | Reads | Writes |
| --- | --- | --- |
| phase-controller | build plan, `.qc/phase-board.json`, role reports | gate summary, phase-board updates, decision-log entries when explicitly approved |
| builder-agent | phase record, target code | `builder-notes.md`, implementation diff |
| ponytail-adapter | phase scope, builder plan | `.qc/ponytail-events.jsonl` |
| test-agent | target code, qc-config, builder notes | `test-report.md`, `.qc/test-results/<phase-id>.jsonl` |
| reviewer-agent | implementation diff, tests, builder notes | `reviewer-report.md` |
| compliance-agent | build plan, records, protected-zone rules | `compliance-report.md`, deviation findings, decision-log review |
| integration-agent | previous/current/next phase contracts | `seam-audit.md` |
| release-agent | runtime/Docker/deploy evidence | `release-gate.md` |

## Safety Defaults

The orchestration is local-only by default.

Do not introduce:

- API keys.
- OAuth files.
- Passwords.
- Refresh tokens.
- Service account private keys.
- Remote MCP transports.
- Remote A2A agents.
- OpenAPI REST tools.
- Cloud session or memory backends.
- Remote Docker daemons.
- Public tunnels.
- Non-loopback server exposure.
- Global installs or machine-wide configuration changes without explicit approval.

If a phase needs any of these, the controller should stop, record the reason, and ask for explicit approval before continuing.

## What A User Says To Run It

Use a prompt like:

```text
Use builder-team-qc for this build.
Target root: <project path>
Build plan: <plan path>
Current phase: <phase id and title>
Run the phase controller with Ponytail minimal-code checks, tests, seam audit, compliance review, and strict gate validation.
```

Codex should then:

1. Read the plugin docs and role skills.
2. Initialize `.qc/`.
3. Start the phase.
4. Execute the phase work.
5. Record evidence.
6. Validate the gate.
7. Report `pass`, `revise`, `block`, or `accepted_with_risk`.

## Future ADK Runtime Shape

A later ADK implementation could use this shape:

```text
BuilderTeamRootAgent
  LoopAgent phase_loop
    SequentialAgent phase_pipeline
      LlmAgent builder
      LlmAgent ponytail_check
      ParallelAgent evidence_checks
        LlmAgent reviewer
        CustomAgent test_runner
        CustomAgent compliance_checker
        CustomAgent seam_auditor
        CustomAgent release_checker
      CustomAgent strict_gate_validator
```

Even in that future form, the safety policy should remain the same:

- Local-first.
- Evidence-first.
- No secrets in `.qc/`.
- No remote access by default.
- No phase pass without strict gate proof.
