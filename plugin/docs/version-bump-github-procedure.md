# GitHub Version Bump Procedure

Use this phased procedure when bumping the public GitHub repo for `builder-team-qc`.

Filled example for this pass:

| Field | Value |
| --- | --- |
| Repository | `randy-aloop/everythingcodex` |
| Branch | `Codex-builder-team-multiagents` |
| Previous public line | `0.1.0-prototype` |
| Target version | `0.2.1-trial` |
| Canonical plugin path | `plugin/` |
| Public plugin URL | `https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents/plugin` |

Do not publish local backup folders, project-local QC records, local audit-run folders, installer-test targets, local Codex thread IDs, credentials, or machine paths.

## Phase 0 - Guardrails And Backup

1. Confirm the repo and branch.
2. Record `git status --short --branch`.
3. Create a full directory backup that preserves `.git`.
4. Optionally create a zip of the working files for quick inspection.
5. Store backups outside the repo tree so they cannot be staged by accident.

Standard Windows backup command shape:

```powershell
$RepoRoot = '<local-repo-root>'
$BackupRoot = '<agent-work-backups-root>'
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$BackupDir = Join-Path $BackupRoot "everythingcodex-pre-$Stamp"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
robocopy $RepoRoot $BackupDir /E /COPY:DAT /DCOPY:DAT /R:1 /W:1
```

Backup acceptance criteria:

- `.git/` exists in the backup.
- changed and untracked docs exist in the backup.
- the backup path is not inside the Git staging scope.

## Phase 1 - Sync And Baseline

Fetch the target branch before mapping changes:

```powershell
git fetch origin Codex-builder-team-multiagents
git status --short --branch
git diff --stat
```

Baseline facts to write down:

- current branch
- upstream branch
- whether local changes are user-owned, generated, or agent-created
- current version in `VERSION`
- current version in `project.json`
- current version in `plugin/.codex-plugin/plugin.json`

For this pass, GitHub currently reports `0.1.0-prototype` in `VERSION`, while the old public plugin manifest reports `0.1.0`. The local working tree version surfaces already report `0.2.1-trial`; the old `0.1.x` references mostly live in historical archive docs and should not be blindly rewritten.

## Phase 2 - Version Surfaces To Change

Change these when moving the live package to a new target version:

| Path | Required action |
| --- | --- |
| `VERSION` | Set to the target version. |
| `project.json` | Set `version`, current installer artifact paths, and live documentation pointers. |
| `plugin/.codex-plugin/plugin.json` | Set plugin manifest `version`; update descriptions only if capability changed. |
| `README.md` | Update current-version table, install commands, feature status, and known proof gaps. |
| `MASTER.md` | Update project summary and version ledger. |
| `CHANGELOG.md` | Add a top entry for the bump. |
| `plugin/docs/CHANGELOG.md` | Add package-doc change notes. |
| `plugin/scripts/install-builder-team-qc.ps1` | Update default expected version and required package checks. |
| `plugin/scripts/install-builder-team-qc-<version>.ps1` | Add or update the versioned wrapper. |
| `plugin/docs/installation-and-first-run-guide.md` | Update install/upgrade examples and version assertions. |
| `site/index.html` | Update public page copy if it reports version or installer commands. |

Do not change historical version claims inside archive folders unless the file is being amended for public safety. Add a superseding note instead of rewriting history.

## Phase 3 - Docs To Map For Push

Every doc must be mapped before staging.

| Doc | Push decision | 0.2.1 action |
| --- | --- | --- |
| `plugin/docs/CHANGELOG.md` | Push | Live docs changelog for `0.2.1-trial`. |
| `plugin/docs/agent-dry-run-and-test-report.md` | Push | Keep as validation evidence after public-safety scan. |
| `plugin/docs/build-plan-authoring-guide.md` | Push | Keep as live user guide. |
| `plugin/docs/multi-agent-modes.md` | Push | Update branch GitHub links and keep live architecture guidance. |
| `plugin/docs/orchestration-diagram.md` | Push | Keep if diagram still matches live roles. |
| `plugin/docs/orchestration-notes.md` | Push | Keep live orchestration contract; verify no stale helper claims. |
| `plugin/docs/phase-by-phase-run-plan.md` | Push | Keep as canonical live run plan. |
| `plugin/docs/phase-loop.md` | Push | Keep as live loop reference. |
| `plugin/docs/production-debug-gate.md` | Push | Keep as release/debug gate reference. |
| `plugin/docs/qc-record-schema.md` | Push | Keep as live schema reference. |
| `plugin/docs/single-run-vs-parallel-runtime.md` | Push | Keep; external ADK links are allowed after review. |
| `plugin/docs/installation-and-first-run-guide.md` | Push | New `0.2.1-trial` install guide; replace old GitHub paths. |
| `plugin/docs/installation-dry-run-and-stress-test-report.md` | Push | New validation report; replace old GitHub paths. |
| `plugin/docs/docs-v03-sync-to-code-expanded-version-record-CORRECTED.md` | Push after sanitizing | Redact local audit source and local run id. |
| `plugin/docs/builder-scope-audit.md` | Push | Evidence/support doc; scan before staging. |
| `plugin/docs/phase-by-phase-run-plan-V02-findings-assessment.md` | Push | Evidence/support doc; scan before staging. |
| `plugin/docs/sandbox-demo-runbook.md` | Push after sanitizing | Replace machine paths with placeholders. |
| `plugin/docs/0.2.1-trial/DOC-03-required-test-finding-assessment.md` | Push | Target-version assessment. |
| `plugin/docs/0.2.1-trial/installer-implementation-report.md` | Push | Target-version implementation evidence. |
| `plugin/docs/0.2.0-trial/hardening-implementation-report.md` | Push as archive | Freeze old-version claims. |
| `plugin/docs/0.1.0-Trial/patch-01-strict-gate-enforcement.md` | Push as archive or exclude | Freeze old-version claims; public-safety scan only. |
| `plugin/docs/0.1.0-Trial/patch-02-phase-board-transition.md` | Push as archive or exclude | Freeze old-version claims; public-safety scan only. |
| `plugin/docs/0.1.0-Trial/versioning-anything-template.md` | Push as archive or exclude | Keep placeholders; no live version rewrite. |
| `plugin/docs/0.1.0-prototype/README.md` | Push as archive or exclude | Freeze historical meaning. |
| `plugin/docs/0.1.0-prototype/01-chronological-thread-record.md` | Push only after careful review | Historical thread-style record; remove any private details. |
| `plugin/docs/0.1.0-prototype/02-work-process-and-decision-logic.md` | Push as archive or exclude | Freeze old-version claims. |
| `plugin/docs/0.1.0-prototype/03-prompt-processing-record.md` | Push as archive or exclude | Freeze old-version claims. |
| `plugin/docs/0.1.0-prototype/04-code-build-artifact-map.md` | Push as archive or exclude | Freeze old-version claims. |
| `plugin/docs/0.1.0-prototype/05-version-rationale.md` | Push as archive or exclude | Freeze old-version claims. |
| `plugin/docs/0.1.0-prototype/06-handoff-to-0.2.0-trial.md` | Push as archive or exclude | Freeze old-version claims. |
| `plugin/docs/alpha-transition-phase-plan.md` | Review before push | Historical planning line; do not let `0.1.0-alpha.1` look current. |

## Phase 4 - One-Doc-At-A-Time Public Safety Cleanup

For each mapped doc:

1. Open the doc.
2. Decide whether it is live, evidence, or archive.
3. Search for sensitive or machine-specific content.
4. Replace local paths with repo-relative paths or the branch GitHub URL.
5. Replace concrete local run ids, thread ids, or session ids with placeholders unless the id is already a public release artifact.
6. Keep policy examples about secrets only when they are clearly examples and contain no real value.
7. Re-scan the doc before marking it ready.

Required scan patterns:

```powershell
rg -n --hidden --glob '*.md' `
  "([A-Za-z]:\\|https?://|api[_-]?key|secret|token|password|passwd|credential|oauth|bearer|authorization|login|thread|session|run id|request id|trace id)" `
  plugin/docs
```

Cleanup rules:

| Finding | Required action |
| --- | --- |
| Local drive path | Replace with repo-relative path, `<local-repo-root>`, `<sandbox-root>`, or the branch GitHub URL. |
| Personal email/login | Remove or replace with `<redacted-contact>`. |
| API key/token/password/secret value | Remove immediately; rotate externally if it was real. |
| Secret keyword in policy text | Keep only if no actual value is present. |
| External URL | Allow public docs, upstream credits, and branch GitHub URLs; review everything else. |
| Thread/session/run id | Replace with `<redacted-local-run-id>` or `<validation-run-id>` unless public traceability is intentional. |

## Phase 5 - Freeze Versus Change

Freeze these:

- historical archive folders: `plugin/docs/0.1.0-prototype/`, `plugin/docs/0.1.0-Trial/`, `plugin/docs/0.2.0-trial/`
- old changelog entries below the new top entry
- historical rationale for why a previous version name was used
- third-party credit/license references
- safety policy examples that contain no real secret values

Change these:

- live package version surfaces
- current install commands
- current GitHub URLs
- live docs claiming the current package state
- validation evidence for the target version
- any local path, private run id, or machine-specific reference
- docs that say a helper is missing when the helper now exists

If unsure, freeze historical docs and add a short "Superseded by `<target-version>`" note rather than rewriting old evidence.

## Phase 6 - Package Validation

Run checks before staging:

```powershell
git diff --check
git status --short

Get-Content plugin/.codex-plugin/plugin.json -Raw | ConvertFrom-Json
Get-Content project.json -Raw | ConvertFrom-Json
Get-Content plugin/assets/qc-templates/qc-config.json -Raw | ConvertFrom-Json
Get-Content plugin/assets/qc-templates/phase-board.json -Raw | ConvertFrom-Json
```

Run script syntax checks:

```powershell
python -m py_compile plugin/scripts/*.py

$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
  'plugin/scripts/install-builder-team-qc.ps1',
  [ref]$tokens,
  [ref]$errors
) | Out-Null
$errors
```

Run installer validation in a disposable target:

```powershell
powershell -ExecutionPolicy Bypass -File plugin/scripts/install-builder-team-qc-0.2.1-trial.ps1 `
  -TargetRoot '<sandbox-target>' `
  -FreshInstall `
  -WriteInstallReport `
  -ValidateInstalled
```

## Phase 7 - Stage, Review, Commit

Stage only intentional files:

```powershell
git add VERSION project.json README.md MASTER.md CHANGELOG.md
git add plugin/.codex-plugin/plugin.json plugin/assets plugin/docs plugin/scripts plugin/skills site/index.html
git status --short
git diff --cached --stat
```

Review before commit:

- no backup files staged
- no project-local QC records, local audit-run folders, `installer-tests/`, or local sandbox outputs staged
- no local paths remain in public docs
- no real credentials or account identifiers exist
- version strings are intentional
- archive docs are clearly historical

Commit message shape:

```text
Bump builder-team-qc to 0.2.1-trial
```

## Phase 8 - Push And GitHub Review

Push only after the local validation gates pass:

```powershell
git push origin Codex-builder-team-multiagents
```

After push:

1. Open the branch on GitHub.
2. Verify the plugin manifest renders at `plugin/.codex-plugin/plugin.json`.
3. Verify the docs render without broken relative links.
4. Verify no backup/sandbox/private files were pushed.
5. If using a pull request, summarize the version bump, docs added, validation commands, and known proof gaps.

## Phase 9 - Post-Push Freeze Record

Create or update a release note that records:

- target version
- branch
- commit hash
- docs included
- docs excluded or frozen
- validation commands and outcomes
- known limitations
- rollback plan

For `0.2.1-trial`, the remaining proof gap is a real product build trial outside sandbox targets.

## Phase 10 - Rollback

If the bump is wrong after push:

1. Do not rewrite public history unless explicitly approved.
2. Revert with a normal Git revert commit.
3. Restore from the local pre-bump backup if the working tree must be reconstructed.
4. Re-run the public-safety scan before any corrected push.
