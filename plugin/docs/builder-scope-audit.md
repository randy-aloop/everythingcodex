# Builder Scope Audit

`audit_builder_scope.py` makes the builder-agent scope check first-class.

It records a phase-relative baseline before builder edits, then compares the post-builder file state against the exact files or globs allowed for that phase.

## Snapshot Before Builder Work

```powershell
python scripts/audit_builder_scope.py `
  --root <project-root> `
  --phase-id <phase-id> `
  --snapshot `
  --json
```

This writes:

```text
.qc/phase-runs/<phase-id>/evidence/builder-scope-baseline.json
```

## Audit After Builder Work

```powershell
python scripts/audit_builder_scope.py `
  --root <project-root> `
  --phase-id <phase-id> `
  --audit `
  --allow src/current_phase_file.py `
  --json
```

This writes:

```text
.qc/phase-runs/<phase-id>/evidence/builder-scope-audit.json
.qc/builder-scope-audits.jsonl
```

Allowed paths apply to added or modified files. Deletions must be explicitly allowed:

```powershell
python scripts/audit_builder_scope.py `
  --root <project-root> `
  --phase-id <phase-id> `
  --audit `
  --allow docs/operator-note.md `
  --allow-remove src/old_file.py
```

## Strict Gate Enforcement

Use this when the phase should not pass without a clean builder scope audit:

```powershell
python scripts/validate_phase_record.py `
  --root <project-root> `
  --phase-id <phase-id> `
  --strict-gate `
  --scan-safety `
  --require-builder-scope `
  --json
```

The strict gate fails if the audit is missing or if the audit has unexpected added, modified, or removed files.

## Ignoring Harness Artifacts

If a test harness writes logs inside the target project root, ignore those paths during both snapshot and audit:

```powershell
python scripts/audit_builder_scope.py `
  --root <project-root> `
  --phase-id <phase-id> `
  --snapshot `
  --ignore capture/**

python scripts/audit_builder_scope.py `
  --root <project-root> `
  --phase-id <phase-id> `
  --audit `
  --allow src/current_phase_file.py `
  --ignore capture/**
```

Do not ignore normal source, config, docs, or build-plan paths unless the phase plan explicitly excludes them from builder ownership.
