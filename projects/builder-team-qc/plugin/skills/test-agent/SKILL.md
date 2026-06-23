---
name: test-agent
description: Run and record local checks for a builder-team-qc phase. Use for quick tests, unit checks, Docker smoke checks, runtime smoke checks, and failure evidence in a phase-controlled build.
---

# Test Agent

Prove the current phase works at the smallest useful level.

## Check Order

1. Syntax or compile check.
2. Unit or focused test for touched behavior.
3. Integration smoke when phase boundaries changed.
4. Docker/runtime smoke when packaging, API, dependencies, sidecars, or deployment behavior changed.
5. Stress/load check only when the phase plan demands it.

## Recording

Use `scripts/record_test_result.py` for each meaningful check. Capture:

- command
- status: `pass`, `fail`, or `skipped`
- exit code when available
- output file or notes

If a required test cannot run, record why and block unless the user explicitly accepts the risk.
