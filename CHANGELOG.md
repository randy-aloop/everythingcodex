# Changelog

## 0.2.1-trial - 2026-06-25

Installer and documentation-sync package for Builder Team QC.

Added:

- `plugin/scripts/install-builder-team-qc-0.2.1-trial.ps1` current trial wrapper
- `plugin/docs/0.2.1-trial/` implementation and required-test assessment records
- public version-bump procedure for moving GitHub from `0.1.0-prototype` to `0.2.1-trial`

Changed:

- plugin manifest, root `VERSION`, `project.json`, and live docs now target `0.2.1-trial`
- canonical installer defaults to `ExpectedVersion = 0.2.1-trial`
- docs and static site align with implemented recorder helpers, strict required-test behavior, accepted-risk handling, release auto-detection, and classified validator exits
- public docs redact local paths, local audit-run IDs, and machine-specific evidence paths

## 0.2.0-trial - 2026-06-24

Trial branch package for Builder Team QC.

Added:

- `plugin/scripts/install-builder-team-qc-0.2.0-trial.ps1` prototype-to-trial upgrade wrapper
- `record_decision.py`, `record_gate_decision.py`, and builder-scope audit helper coverage in the packaged plugin
- installed-copy validation and optional `install-report.json` output
- `plugin/docs/0.2.0-trial/` hardening report package

Changed:

- plugin manifest version moved to `0.2.0-trial`
- root `VERSION`, `project.json`, and `README.md` moved from prototype to trial
- installer now enforces expected version and required hardening helper files
- installation docs now describe upgrade and fresh-install paths for `0.2.0-trial`

## 0.1.0-prototype - 2026-06-24

Prototype branch package for Builder Team QC.

Added:

- branch-clone installation section
- PowerShell project-local installer
- agent dry-run and test report
- build plan authoring guide
- README sections for installation, dry-run evidence, and build plan authoring

Changed:

- project status moved from planning to prototype

## 0.1.0-planning - 2026-06-23

Initial project package for Everything Codex.

Added:

- repository-level project index
- Builder Team QC README
- Builder Team QC master file
- version metadata
- folder structure contract
- Codex plugin/process package
- static developer article page

Known gaps:

- runtime hook runner is not yet implemented
- sample project pass/revise/pass trial is not yet included
- first real-project trial is not yet complete
