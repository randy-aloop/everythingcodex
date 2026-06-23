# Multi-Agent Run Model

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
```

The role skills are the stable org chart. The scripts are tools called by the controller to create records, not independent agents that take over control.

## ADK Concept Mapping

| ADK concept | Builder Team QC V01 equivalent |
| --- | --- |
| `BaseAgent` | Codex skill contract. |
| `LlmAgent` | Codex reasoning while acting under a role skill. |
| `SequentialAgent` | The default phase loop order. |
| `ParallelAgent` | Optional conceptual grouping for independent checks after build. |
| `LoopAgent` | Revise loop until strict gate passes, blocks, or accepted risk is recorded. |
| Shared session state | Project-local `.qc/` files and JSONL logs. |
| LLM-driven delegation | Codex choosing which role contract to apply based on phase state. |
| Agent-as-a-tool | Helper scripts invoked by the controller. |
| Sub-agent | A permanent role skill in the builder-team hierarchy. |

## Sequential Flow

The normal run is sequential because phase evidence has dependencies.

```text
1. Read build plan and current phase.
2. Initialize `.qc/` if needed.
3. Start or resume phase record.
4. Apply builder role.
5. Apply Ponytail minimal-code check.
6. Record tests.
7. Apply reviewer role.
8. Apply compliance role.
9. Apply integration seam audit.
10. Apply release role when the phase is runtime, Docker, deploy, or production-related.
11. Run in-progress validation.
12. Run strict gate validation before completion.
13. Decide pass, revise, block, or accepted_with_risk.
```

Command skeleton:

```powershell
cd D:\Workhorse\01_PRODUCTS\Skills-Creation-Test-Install\06_agent-work\codex\builder-teams-multiagent-ponytail\builder-team-qc

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
  --abstraction-check "No new abstraction unless needed" `
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
```

## Parallel Flow

ADK `ParallelAgent` is useful when checks do not depend on each other. Builder Team QC can mimic that after the builder has produced a candidate change.

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
  validate_phase_record.py checks evidence
  strict gate decides next action
```

In V01, Codex may execute these as separate role passes rather than true runtime concurrency. The important control rule is the same as ADK parallel orchestration: all branches must join before the gate can pass.

## Loop Flow

ADK `LoopAgent` maps to the revise loop.

```text
while strict gate does not pass:
  if blocker exists:
    gate = block
    stop
  if user explicitly accepts risk:
    gate = accepted_with_risk
    record decision and stop
  otherwise:
    gate = revise
    builder fixes the smallest failing item
    tests/review/compliance/seam run again
    strict validation runs again

gate = pass only when required evidence is complete
```

The loop is bounded by engineering judgment and user instructions. It should not hide repeated failures, keep retrying blindly, or claim completion when evidence is missing.

## Shared State

ADK shared session state is represented by `.qc/`.

| State file | Shared meaning |
| --- | --- |
| `.qc/phase-board.json` | Current phase id, status, next phase, required evidence, latest gate. |
| `.qc/phase-runs/<phase-id>/phase-record.md` | Phase plan, deliverables, evidence index, final gate notes. |
| `.qc/phase-runs/<phase-id>/builder-notes.md` | Builder role output. |
| `.qc/phase-runs/<phase-id>/reviewer-report.md` | Reviewer role output. |
| `.qc/phase-runs/<phase-id>/test-report.md` | Human-readable test evidence. |
| `.qc/test-results/<phase-id>.jsonl` | Machine-readable test events. |
| `.qc/ponytail-events.jsonl` | Ponytail mode and minimal-code verdicts. |
| `.qc/deviation-log.jsonl` | Deviations and accepted-risk metadata. |
| `.qc/decision-log.jsonl` | User decisions, approvals, and gate overrides. |
| `.qc/phase-runs/<phase-id>/seam-audit.md` | Previous/current/next compatibility evidence. |
| `.qc/phase-runs/<phase-id>/release-gate.md` | Production debug, Docker/runtime, rollback, and no-secrets evidence. |

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

The controller may choose the order, but it may not skip required evidence before completion.

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
| `pass` | Evidence is complete, required tests pass, safety scan passes, Ponytail verdict is pass, seams are complete, and release gate is complete when applicable. |
| `revise` | The phase is close, but a local repair is needed before completion. |
| `block` | A missing requirement, approval, safety condition, seam issue, or failing check prevents progress. |
| `accepted_with_risk` | The user explicitly accepts incomplete verification with impact, owner, and follow-up recorded. |

No next phase should start until the current gate allows it.

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
