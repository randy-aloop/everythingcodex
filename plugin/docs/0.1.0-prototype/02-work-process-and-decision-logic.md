# Work Process And Decision Logic

Version: `0.1.0-prototype`
Created: 2026-06-24

This file captures the reasoning model used during the prototype work. It is not raw hidden chain-of-thought. It is the curated engineering logic needed for future maintainers.

## Core Decision Principles

### Local First

The project repeatedly chose local-first behavior:

- no API keys required
- no remote A2A runtime
- no remote MCP transport
- no OpenAPI tool execution
- no public tunnels
- no global install without approval
- no cloud session or remote memory backend

Reason:

The project is a build-control plugin/process. It should not surprise a user with remote automation, credential use, or background services.

### Evidence Over Prose

The system is valuable because it writes durable `.qc/` evidence.

Required evidence types grew over the prototype:

- phase board
- phase record
- builder notes
- changed file list
- implementation diff
- Ponytail events
- test results
- reviewer report
- compliance report
- seam audit
- release gate
- decision log
- deviation log
- issue register
- gate summary
- lessons learned

Reason:

Chat history is ephemeral. `.qc/` records make the build inspectable after the conversation ends.

### One Phase Is The Unit Of Control

The system should not run "the whole project" vaguely. It should open one phase, gather evidence, then decide:

```text
pass
revise
block
accepted_with_risk
```

Reason:

Phase-level control reduces scope creep and makes review/test/compliance checks meaningful.

### Strict Gate Claims Must Match Code

A major prototype lesson was that docs can easily overstate the scripts.

The docs now try to separate:

```text
implemented behavior
manual fallback
target contract
planned helper
```

Reason:

If docs say "strict gate enforces X" but the validator does not enforce X, the project creates false trust.

### Single-Run Before Parallel

The prototype chose single-run multiagent for Runtime V01.

Reason:

Single-run is safer while records and validators are still maturing:

- no concurrent writes
- no stale worker outputs
- no locking required
- easier to debug
- easier for a careful user to inspect

Parallel Runtime V02 is a future target, not prototype behavior.

## Prompt Processing Logic

The user often asked broad, compound questions. The working pattern was:

1. Identify the concrete artifact requested.
2. Read the existing docs/code when available.
3. Decide whether the task is planning, review, implementation, or publication.
4. If review-only was requested, write a report and avoid patching.
5. If patching was requested, use scoped edits.
6. Validate with text scans, JSON parsing, and script inspection where relevant.
7. Report what changed and what remains unimplemented.

## Version Logic

The prototype conversation developed this version model:

```text
0.1.0-prototype = designed and scaffolded, not yet real-build proven
0.1.0-planning = public honesty label when docs/scripts still diverge
0.2.0-trial = next stage focused on real local trial and script hardening
0.1.0-alpha.1 = careful user can run end-to-end with known rough edges
beta = multiple real builds prove repeatability
```

The user now wants to move to `0.2.0-trial`. That should be treated as a trial-development branch, not as public alpha.

## Key Engineering Judgments

### Do Not Delete Safety Scanner Patterns

When the scanner self-detected banned regex strings, the correct fix was not to remove the patterns.

Better logic:

```text
scanner policy definition = info
docs/policy reference = info or warning
active secret/remote tool config = blocker
```

Reason:

Removing patterns would blind the scanner.

### Do Not Call Logical Fan-Out Parallel

The docs now distinguish:

```text
logical fan-out = checks are independent in concept
true parallel = workers execute concurrently
```

Runtime V01 has logical fan-out only.

### Accepted Risk Requires Human Proof

`accepted_with_risk` is a gate bypass.

Required proof:

- human approver
- risk
- impact
- reason
- owner
- deadline
- rollback
- follow-up
- decision id

Reason:

The controller must not self-approve risk.

### Phase 0 Cannot Write Before Records Exist

The V03 run plan fixed this:

```text
Phase 0 = in-memory precheck
Phase 1 = init .qc
Phase 2 = start phase and persist findings
```

Reason:

`.qc/issue-register.jsonl` and `phase-record.md` do not exist until after initialization/start.

## Verification Style Used

Verification during the prototype included:

- reading target docs before patching
- reading current script surfaces before documenting behavior
- searching for stale wording
- scanning for local path leaks
- parsing fenced JSON examples
- checking plugin/repo status when relevant
- inspecting generated artifact paths
- using fable5 run folders when explicitly requested

## Known Prototype Limitations

The prototype remains limited because:

- no real local build trial has proven the full loop
- strict validator still needs hardening
- builder scope audit is shipped at script/validator level but not real-trial proven
- final gate recording helper is not fully shipped
- decision recording helper is not fully shipped
- safety scanner has severity classification but needs real-trial tuning
- docs and templates may still require synchronization
- no single "run this phase" controller command exists yet

These limitations are the reason for moving into `0.2.0-trial` before alpha.
