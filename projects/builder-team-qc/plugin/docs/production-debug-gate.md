# Production Debug Gate

Use for release, deploy, runtime, Docker, API, sidecar, and production phases.

Required evidence:

- debug switches are explicit and safe
- logs do not expose secrets
- runtime configuration is reproducible
- Docker or runtime smoke checks are recorded when relevant
- rollback and troubleshooting notes exist

Release phases cannot pass with `release-gate.md` still pending or `not_applicable`.
