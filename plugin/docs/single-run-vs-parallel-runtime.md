# Single-Run Multiagent Vs Parallel Runtime

Version: V03
Updated: 2026-06-24
Supersedes: V02

This note explains why Builder Team QC currently uses a single-run multiagent model, and what changes when the builder team becomes a true parallel runtime.

## Short Answer

Use **single-run multiagent** for Runtime V01.

Plan **parallel runtime** for a later Runtime V02 only after the strict gate, file locking, evidence schema, and safety scanner are deterministic enough to handle concurrent workers.

## What Single-Run Multiagent Means

Single-run multiagent means one Codex runtime performs the builder-team roles one at a time.

Runtime V01 is not a Google ADK runtime. It is a Codex-controlled sequential role pass that borrows ADK-style orchestration vocabulary while keeping execution local, visible, and file-auditable.

```text
phase-controller
  -> builder-agent
  -> ponytail-adapter
  -> test-agent
  -> reviewer-agent
  -> compliance-agent
  -> integration-agent
  -> release-agent when required
  -> strict gate
```

The system is multiagent by role, but not by process. The agents are role contracts that Codex applies sequentially.

## Why Single-Run Is The Right Runtime V01

Single-run keeps the first production path safer and easier to audit.

Reasons:

- The controller has one clear phase state.
- `.qc/` writes happen in a predictable order.
- There are no race conditions between agents writing the same files.
- No file locks are required.
- No worker scheduler is required.
- No remote service, API server, public tunnel, A2A, or remote MCP transport is required.
- A human can inspect the conversation and the `.qc/` records in the same order the work happened.
- The strict gate can fail fast without reconciling conflicting worker results.

Single-run also fits the current helper reality. The `0.2.0-trial` hardening pass added `record_decision.py`, `record_gate_decision.py`, richer validator exit codes, and stronger evidence/diff recording, but these surfaces still need a real local build trial before parallel workers should multiply the number of writers.

## What Parallel Runtime Means

Parallel runtime means the controller starts independent worker agents after the builder output and Ponytail check exist.

```text
phase-controller
  -> builder-agent
  -> changed-files/diff evidence
  -> ponytail-adapter
  -> parallel evidence fan-out
       test-agent
       reviewer-agent
       compliance-agent
       integration-agent
       release-agent when required
  -> join evidence
  -> strict gate
```

The builder and Ponytail stages should remain sequential. The parallel part starts only after there is a candidate change to inspect.

## Verification Against ADK

This note uses ADK terms as a comparison model, not as a claim that Runtime V01 already runs ADK.

Confirmed alignment with current ADK documentation:

- ADK `SequentialAgent` executes sub-agents in the order they are listed and is deterministic in how it orchestrates those sub-agents.
- ADK `ParallelAgent` executes sub-agents concurrently. Its branches run independently, and shared state must be handled explicitly through shared context, external state, post-processing, and concurrency controls such as locks.
- ADK `LoopAgent` repeats its sub-agents until a max-iteration limit or termination condition is reached. A bounded revise loop must define its stop condition.
- ADK 2.0 introduces graph and dynamic workflow structures. For a future real ADK implementation, graph/dynamic workflows should be considered first; `SequentialAgent`, `ParallelAgent`, and `LoopAgent` remain useful template-workflow analogies and possible implementation choices when they fit the target ADK version.

Reference docs:

- https://adk.dev/agents/workflow-agents/sequential-agents/
- https://adk.dev/agents/workflow-agents/parallel-agents/
- https://adk.dev/agents/workflow-agents/loop-agents/

## What Can Run In Parallel

These can run in parallel after Ponytail passes:

- `test-agent`
- `reviewer-agent`
- `compliance-agent`
- `integration-agent`
- `release-agent`, when `release_required=true`

These should not run in parallel:

- `phase-controller`, because it owns the gate.
- `builder-agent`, because it creates the candidate work.
- `ponytail-adapter`, because it decides whether the candidate is small enough to justify deeper checks.
- `strict gate`, because it must join all evidence after the workers finish.

## Trade-Offs

| Runtime | Strength | Cost |
| --- | --- | --- |
| Single-run | Simple, auditable, deterministic order. | Slower and less independent. |
| Parallel | Faster evidence collection and more independent role review. | Requires locking, worker isolation, conflict handling, and stronger gate scripts. |

## Why Parallel Is Riskier

Parallel agents create new failure modes:

- Two workers may write the same `.qc/` file at the same time.
- A reviewer may read stale diff evidence while the test worker is still updating results.
- A compliance worker may approve an earlier candidate after the builder has revised it.
- A release worker may mark runtime evidence complete while test evidence failed.
- Worker outputs may disagree and require a deterministic join rule.
- A false-positive safety scan can block every worker unless severity and allowlist handling are deterministic.

These are engineering problems, not reasons to avoid parallel forever. They are reasons not to ship parallel before the coordination layer is ready.

## Required Runtime V02 Controls

Parallel Runtime V02 should not start until these controls exist:

- Per-agent output files or folders.
- File locking or append-only JSONL writes with atomic append.
- Attempt ids on every worker result.
- Candidate/diff id shared by all workers.
- Deterministic join rule.
- `record_decision.py` with stable decision ids.
- `record_gate_decision.py` for final phase-board transitions.
- Strict verdict parsing for every role report.
- Required-test enforcement.
- Issue-register enforcement.
- Safety scanner severity classification.
- Release-gate `not_applicable` handling.
- Clear rule for stale worker outputs after a revise attempt.

## Recommended Runtime Path

Use this sequence:

```text
Runtime V01:
  single Codex runtime
  sequential role passes
  durable .qc evidence
  strict gate blocks on missing proof

Runtime V02:
  same phase contract
  same .qc schema
  parallel evidence workers after Ponytail
  deterministic join before strict gate

Runtime V03:
  optional real ADK implementation
  prefer ADK graph/dynamic workflows when targeting ADK 2.0+
  or use template workflow agents when they fit:
    SequentialAgent for build path
    ParallelAgent for evidence checks
    LoopAgent for bounded revise loop
```

## Decision

Builder Team QC should remain **single-run multiagent** until its evidence and gate scripts are strong enough for concurrent workers.

The target design is not "single forever." The target design is:

```text
sequential build
parallel evidence checks
sequential strict gate
```

That gives the project the speed and independence of parallel agents without sacrificing the auditability that makes Builder Team QC valuable.
