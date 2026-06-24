---
name: integration-agent
description: Run previous/current/next seam audits for builder-team-qc phases. Use when checking that a phase connects cleanly to prior assumptions and next-phase contracts.
---

# Integration Agent

Audit the phase seam.

## Check

- Previous phase assumptions still hold.
- Current phase outputs exist and are documented.
- Next phase inputs/contracts are clear.
- Interface, schema, migration, config, or runtime changes are reflected in docs and tests.
- Any unresolved seam is logged in `issue-register.jsonl`.

## Output

Write `seam-audit.md` with:

- previous/current/next summary
- drift findings
- required follow-up
- verdict: `pass`, `revise`, or `block`
