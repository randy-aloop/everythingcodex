# Version Rationale

Version: `0.1.0-prototype`
Created: 2026-06-24

This file explains why the archived thread state is called `0.1.0-prototype`.

## Why Not Alpha Yet

The design is strong, but alpha should mean:

```text
careful early user can run end-to-end with known rough edges
```

The prototype does not yet meet that bar because:

- a real local build trial has not fully proven the packaged system
- docs and scripts have had mismatches
- strict validator behavior is not yet as strong as the docs intend
- builder scope audit has not been fully shipped
- `record_decision.py` and `record_gate_decision.py` are not fully shipped
- safety scanner can overblock policy/reference text
- no single phase controller command exists yet

## Why Prototype Fits

Prototype means:

```text
the concept is implemented enough to inspect, improve, and trial
```

That matches the current state:

- role model exists
- local scripts exist
- `.qc` schema direction exists
- orchestration docs exist
- phase-by-phase runbook exists
- safety and release gates are designed
- version and alpha planning exist

## Why Move To 0.2.0-Trial

`0.2.0-trial` should be the next stage because it can focus on proof:

```text
Can a real local target use this from install to final phase-board transition?
```

Trial should not claim alpha polish. It should claim:

- real use begins
- gaps are visible
- scripts are hardened against real failure paths
- docs are corrected against actual run behavior

## Suggested Version Ladder

```text
0.1.0-prototype
  historical design and scaffold package

0.2.0-trial
  real local trial and script hardening

0.1.0-alpha.1 or 0.3.0-alpha.1
  careful early user can run end-to-end

0.x beta
  repeated real builds prove repeatability
```

Note:

If semantic versioning is kept strictly monotonic, alpha after `0.2.0-trial` should probably be `0.3.0-alpha.1`, not `0.1.0-alpha.1`. If the project treats `0.1.0-alpha.1` as a release label rather than a monotonic package version, keep the meaning explicit in the changelog.

## Release Honesty Rule

Do not use a label because the design deserves it.

Use a label when a user can reproduce the behavior from the packaged repo.
