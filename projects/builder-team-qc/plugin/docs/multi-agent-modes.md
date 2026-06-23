# Multi-Agent Run Model

Version: V02
Updated: 2026-06-23
Supersedes: V01

Builder Team QC uses ADK-style orchestration ideas without depending on a live Google ADK runtime in V01.

The root controller is the `phase-controller` Codex skill. The role skills behave like sub-agents, and the `.qc/` folder behaves like shared session state. Scripts are explicit tools that record evidence and validate phase gates.

## Current V01 Mode

V01 is a local Codex instruction-plus-scripts plugin.

It does not launch autonomous remote agents, expose an API server, run A2A, call MCP over remote transports, or require API keys. Codex stays in control and applies each role contract while the scripts make the state durable.

```text
User request
  -> Codex
    -> phase-controller
      -> builder-agent
      -> ponytail-adapter
      -> test-agent
      -> reviewer-agent
      -> compliance-agent
      -> integration-agent
      -> release-agent when applicable
    -> validate strict gate
  -> user-visible gate result
```

## Hierarchy

```text
Root controller
  phase-controller

Permanent role contracts
  builder-agent
  ponytail-adapter
  test-agent
  reviewer-agent
  compliance-agent
  integration-agent
  release-agent

Explicit script tools
  init_qc.py
  start_phase.py
  record_ponytail_check.py
  record_test_result.py
  record_deviation.py
  validate_phase_record.py
  summarize_phase.py
  record_decision.py, planned
  record_gate_decision.py, planned
```

The role skills are the stable org chart. The scripts are tools called by the controller to create records, not independent agents that take over control.

Two hardening tool contracts are required before this process can be called fully deterministic:

- `record_decision.py` or an equivalent controller step must append accepted-risk and approval records to `.qc/decision-log.jsonl`.
- `record_gate_decision.py` or an equivalent controller step must update `.qc/phase-board.json` after the final gate.

Until those helpers exist, the controller must write those records manually and report that the decision/gate transition was manually recorded.

The same rule applies to fields that current helper scripts do not yet support, such as test `required`, test `attempt`, Ponytail `attempt`, Ponytail `mode_source`, deviation `issue_id`, and final gate summary output. Missing helper support is a current implementation gap, not permission to omit the evidence.

## Context Isolation

V01 uses one Codex conversation, so role separation is logical rather than process-isolated. To reduce self-grading risk:

- The builder role records changed files and implementation evidence before review starts.
- Reviewer, compliance, and integration roles read persisted `.qc` records and project files instead of relying only on the builder's chat summary.
- The controller treats model-authored reports as judgment evidence, not executable proof.
- Tests, validators, safety scans, and file artifacts carry more weight than a role saying "complete."
- If a future runtime runs real parallel or isolated agents, it should still write to the same `.qc` contract.

## ADK Concept Mapping

| ADK concept | Builder Team QC V01 equivalent |
| --- | --- |
| `BaseAgent` | Codex skill contract. |
| `LlmAgent` | Codex reasoning while acting under a role skill. |
| `SequentialAgent` | The default phase loop order. |
| `ParallelAgent` | Logical fan-out for independent checks after build. In V01 this is sequential role execution, not runtime concurrency. |
| `LoopAgent` | Bounded revise loop until strict gate passes, blocks, or accepted risk is recorded. Default cap: three failed revise attempts. |
| Shared session state | Project-local `.qc/` files and JSONL logs. |
| LLM-driven delegation | Codex choosing which role contract to apply based on phase state. |
| Agent-as-a-tool | Helper scripts invoked by the controller. |
| Sub-agent | A permanent role skill in the builder-team hierarchy. |

## Sequential Flow

The normal run is sequential because phase evidence has dependencies.

```text
1. Read build plan and current phase.
2. Run the pre-build plan check and open blocker issues if the phase is not ready.
3. Initialize `.qc/` if needed.
4. Start or resume phase record.
5. Apply builder role.
6. Persist `changed-files.json` and `implementation-diff.patch`.
7. Apply Ponytail minimal-code check.
8. Record tests.
9. Apply reviewer role.
10. Apply compliance role.
11. Apply integration seam audit.
12. Apply release role when the phase is runtime, Docker, deploy, or production-related.
13. Run in-progress validation.
14. Run strict gate validation before completion.
15. Decide pass, revise, block, or accepted_with_risk.
16. Record `gate-summary.md` and the final gate transition in `.qc/phase-board.json`.
```

Command skeleton:

```powershell
# Project source:
# https://github.com/randy-aloop/everythingcodex/tree/main/projects/builder-team-qc/plugin
cd <local-clone>/projects/builder-team-qc/plugin

python scripts\init_qc.py --root <target-project>

python scripts\start_phase.py `
  --root <target-project> `
  --phase-id phase-001 `
  --title "Phase title" `
  --next-phase-id phase-002 `
  --build-plan "<plan path or short phase summary>"

python scripts\record_ponytail_check.py `
  --root <target-project> `
  --phase-id phase-001 `
  --mode task-scoped `
  --yagni-check "No extra scope added" `
  --stdlib-check "Used existing project/runtime tools where possible" `
  --dependency-check "No new dependency added" `
  --abstraction-check "No new abstraction unless required" `
  --minimum-code-verdict pass `
  --notes "Minimal-code check completed"

python scripts\record_test_result.py `
  --root <target-project> `
  --phase-id phase-001 `
  --name syntax `
  --command "<command run>" `
  --status pass `
  --exit-code 0 `
  --notes "Syntax check passed"

python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id phase-001 `
  --scan-safety

python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id phase-001 `
  --scan-safety `
  --strict-gate

# Add --release-phase when the phase touches runtime, Docker, APIs, deploy,
# production debug, dependencies, sidecars, rollback, or release behavior.
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id phase-001 `
  --scan-safety `
  --strict-gate `
  --release-phase
```

## Parallel Flow

ADK `ParallelAgent` is useful when checks do not depend on each other. Builder Team QC mimics the join rule after the builder has produced a candidate change, but V01 does not execute true concurrent agents.

Conceptual parallel set:

```text
After builder output exists:
  test-agent          -> test-report.md and test-results JSONL
  reviewer-agent      -> reviewer-report.md
  compliance-agent    -> compliance-report.md
  integration-agent   -> seam-audit.md
  release-agent       -> release-gate.md, only when applicable

Join point:
  phase-controller reads all role outputs
  phase-controller reads issue-register, changed-files, and diff artifacts
  validate_phase_record.py checks evidence
  strict gate decides next action
```

In V01, Codex executes these as separate role passes unless a future runtime adds real concurrency. The important control rule is the same as ADK parallel orchestration: all branches must join before the gate can pass.

## Loop Flow

ADK `LoopAgent` maps to the revise loop.

```text
while strict gate does not pass:
  if revise_attempts >= 3:
    gate = block
    stop and ask for human decision
  if blocker exists:
    gate = block
    stop
  if user explicitly accepts risk:
    gate = accepted_with_risk
    record decision-log entry and stop
  otherwise:
    gate = revise
    increment revise_attempts
    builder fixes the smallest failing item
    affected tests/review/compliance/seam run again
    full proof reruns when contracts, schema, runtime, release behavior, dependencies, Docker, or safety policy changed
    strict validation runs again

gate = pass only when required evidence is complete
```

The default loop cap is three failed revise attempts. A project may lower the cap in `.qc/qc-config.json`; raising it requires an explicit user decision. The controller should not hide repeated failures, keep retrying blindly, or claim completion when evidence is missing.

## Shared State

ADK shared session state is represented by `.qc/`.

| State file | Shared meaning |
| --- | --- |
| `.qc/phase-board.json` | Current phase id, status, next phase, release requirement, revise attempt count, required evidence, latest gate, and final gate timestamp. |
| `.qc/phase-runs/<phase-id>/phase-record.md` | Phase plan, deliverables, evidence index, final gate notes. |
| `.qc/phase-runs/<phase-id>/builder-notes.md` | Builder role output. |
| `.qc/phase-runs/<phase-id>/changed-files.json` | Machine-readable changed-file list for reviewer and compliance roles. |
| `.qc/phase-runs/<phase-id>/implementation-diff.patch` | Diff evidence or equivalent patch summary. |
| `.qc/phase-runs/<phase-id>/reviewer-report.md` | Reviewer role output. |
| `.qc/phase-runs/<phase-id>/test-report.md` | Human-readable test evidence. |
| `.qc/test-results/<phase-id>.jsonl` | Machine-readable test events. |
| `.qc/ponytail-events.jsonl` | Ponytail mode and minimal-code verdicts. |
| `.qc/issue-register.jsonl` | Open/fixed/blocker issue records created by role checks. |
| `.qc/deviation-log.jsonl` | Deviations, blockers, and links to accepted-risk decision ids. |
| `.qc/decision-log.jsonl` | Human decisions, approvals, accepted-risk records, owner, deadline, rollback, and follow-up commitments. |
| `.qc/phase-runs/<phase-id>/seam-audit.md` | Previous/current/next compatibility evidence. |
| `.qc/phase-runs/<phase-id>/release-gate.md` | Production debug, Docker/runtime, rollback, and no-secrets evidence. |
| `.qc/phase-runs/<phase-id>/gate-summary.md` | Final validator result, role verdict table, gate decision, and phase-board update note. |
| `.qc/lessons-learned.jsonl` | Future-process lessons that do not bypass current blockers. |

Each role reads the current state and writes only its evidence. The phase controller reads everything and decides the gate.

## Delegation

In ADK, a parent LLM agent may route work dynamically to sub-agents. In Builder Team QC V01, Codex performs that routing under the `phase-controller` instructions.

Examples:

| Situation | Delegated role |
| --- | --- |
| A phase requires code changes. | `builder-agent` |
| The change may be too broad or over-abstracted. | `reviewer-agent` and `ponytail-adapter` |
| There is a runtime, Docker, API, or dependency change. | `test-agent` and `release-agent` |
| Work touches a phase boundary, schema, config, migration, or handoff. | `integration-agent` |
| The work touches protected zones, approvals, secrets, or plan deviation. | `compliance-agent` |

The controller may choose the order only when dependencies still hold. Ponytail must run after the builder candidate and before tests/review fan-out, and the controller may not skip required evidence before completion.

## Agent-As-A-Tool Vs Sub-Agent

Builder Team QC uses both concepts.

| Feature | Builder Team QC equivalent |
| --- | --- |
| Sub-agent | A role skill, such as `reviewer-agent`, that is always part of the builder-team org chart. |
| Agent-as-a-tool | A script, such as `record_test_result.py`, invoked for one specific evidence action. |
| Who stays in control | The phase-controller/Codex stays in control in V01. |
| Who talks to the user | Codex reports the gate result and blockers. |
| What takes over | Nothing takes over autonomously in V01. |

This is intentional. It keeps the system auditable and prevents a helper role from silently changing scope, calling remote services, or bypassing the gate.

## Gate Decision

The phase controller can return four outcomes:

| Gate | Meaning |
| --- | --- |
| `pass` | Evidence is complete, required role verdicts are `pass`, at least one required non-skipped test passes, safety scan passes, Ponytail verdict is `pass`, seams are complete, release gate is complete when applicable, and the phase board is updated. |
| `revise` | The phase is close, but a local repair is needed before completion. |
| `block` | A missing requirement, approval, safety condition, seam issue, or failing check prevents progress. |
| `accepted_with_risk` | The user explicitly accepts incomplete verification with impact, owner, rollback, deadline, and follow-up recorded in `.qc/decision-log.jsonl`. The controller must not self-approve it. |

No next phase should start until the current gate allows it.

Strict-gate validation should treat missing verdicts, duplicate/conflicting verdicts, `Verdict: revise`, and `Verdict: block` in required role reports as failures, not as completed evidence. Required tests that are only `skipped` also fail the gate unless a matching accepted-risk decision exists. Open blocker issues in `.qc/issue-register.jsonl` block the gate.

Confirmed current validator behavior: `validate_phase_record.py` currently returns `0` for success and `1` for errors. The target deterministic contract is richer: `0` pass, `10` strict-gate failure, `20` schema/config/invocation error, and `30` safety blocker. Until implemented, the controller must classify the observed `1` in `gate-summary.md`.

## Future ADK-Compatible Shape

A later implementation could wrap this model in real ADK agents:

```text
BuilderTeamRootAgent
  LoopAgent: phase_loop
    SequentialAgent: phase_pipeline
      LlmAgent: builder
      ParallelAgent: evidence_checks
        LlmAgent: reviewer
        CustomAgent: test_runner
        CustomAgent: compliance_checker
        CustomAgent: seam_auditor
        CustomAgent: release_checker
      CustomAgent: strict_gate_validator
```

That future form should still preserve the V01 safety defaults:

- Local-only by default.
- No secrets in `.qc/`.
- No remote A2A/MCP/OpenAPI by default.
- No public server exposure by default.
- No phase pass without durable evidence.
