# 0.2.1-Trial Installer Implementation Report

Version: `0.2.1-trial`
Date: 2026-06-25
Status: implemented locally

## Purpose

`0.2.1-trial` packages the executed `DOC-V03-SYNC-TO-CODE-EXPANDED` patch as an installable trial version.

It does not introduce a new agent runtime. It makes the latest patch explicit at install time by requiring:

- plugin manifest version `0.2.1-trial`
- V03.1 headers in the touched live docs
- executed corrected patch record
- recovery-pack manifest and README
- the new `install-builder-team-qc-0.2.1-trial.ps1` wrapper

## Files Changed

- `.codex-plugin/plugin.json`
- `scripts/install-builder-team-qc.ps1`
- `scripts/install-builder-team-qc-0.2.1-trial.ps1`
- `docs/installation-and-first-run-guide.md`
- `docs/CHANGELOG.md`

## Installer Behavior

The canonical installer now defaults to `ExpectedVersion = 0.2.1-trial`.

The `0.2.1-trial` wrapper:

- preserves existing `.qc/` records by default
- validates the source package shape
- validates the installed project-local package when copying is enabled
- supports explicit fresh installs with `-FreshInstall`
- supports `-StartPhase`, `-WriteInstallReport`, `-DryRun`, and custom `-Python`

## Verification Plan

Required checks:

1. Parse-check PowerShell installer scripts.
2. Compile Python scripts.
3. Run canonical installer dry run against a sandbox target.
4. Run `0.2.1-trial` wrapper dry run against a sandbox target.
5. Run fresh install into a disposable sandbox target.
6. Confirm installed manifest reports `0.2.1-trial`.
7. Confirm installed wrapper and V03.1 patch evidence exist.

## Verification Results

Result: pass.

Checks run on 2026-06-25:

| Check | Result |
| --- | --- |
| PowerShell parse check for `install-builder-team-qc.ps1` | pass |
| PowerShell parse check for `install-builder-team-qc-0.2.1-trial.ps1` | pass |
| `python -m compileall scripts` | pass |
| Canonical installer dry run with default `ExpectedVersion` | pass |
| `install-builder-team-qc-0.2.1-trial.ps1 -DryRun` | pass |
| `install-builder-team-qc-0.2.1-trial.ps1 -FreshInstall -WriteInstallReport` | pass |
| Installed manifest version | `0.2.1-trial` |
| Installed wrapper exists | pass |
| Installed corrected patch record exists | pass |
| Installed recovery-pack manifest exists | pass |
| Installed `install-report.json` version | `0.2.1-trial` |

Fresh-install sandbox:

```text
installer-tests/install-0.2.1-trial-fresh-20260625
```

Installed validation:

```text
validate_phase_record.py --template-only --json
ok: true
```

## Boundary

This installer proves package installation and patch-evidence validation. It does not prove a full real product build; that remains a separate trial-run milestone.
