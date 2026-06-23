# Production Debug Gate

Use for release, deploy, runtime, Docker, API, sidecar, and production phases.

When this gate applies, set `release_required=true` in phase state and run strict validation with release awareness.

Required evidence:

- debug switches are explicit and safe
- logs do not expose secrets
- runtime configuration is reproducible
- Docker or runtime smoke checks are recorded when relevant
- rollback and troubleshooting notes exist

Release phases cannot pass with `release-gate.md` still pending or `not_applicable`.

Validator command for release/runtime phases:

```powershell
python scripts\validate_phase_record.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --scan-safety `
  --strict-gate `
  --release-phase
```

`Verdict: not_applicable` is allowed only when `release_required=false`. If runtime impact is uncertain, default to `release_required=true` until the controller records why the release gate is not applicable.

Accepted risk cannot replace this gate unless the user explicitly records the production impact, owner, rollback path, deadline, and follow-up check in `.qc/decision-log.jsonl`.
