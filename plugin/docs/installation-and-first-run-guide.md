# Builder Team QC Installation And First Run Guide

Version: V04
Updated: 2026-06-25
Supersedes: V03

This guide compiles the installation/setup steps from `docs/phase-by-phase-run-plan.md` into a user-facing sequence.

Important status from this thread:

- `builder-team-qc` is built as a local Codex plugin bundle.
- The plugin manifest exists at `.codex-plugin/plugin.json` and is expected to report `0.2.1-trial`.
- The plugin contains skills under `skills/`.
- The plugin contains local helper scripts under `scripts/`.
- The plugin was not confirmed as installed/loaded into the active Codex plugin registry.
- The confirmed working path is direct local use of the plugin scripts against a sandbox or target project.

Use this guide for two things:

1. Run Builder Team QC safely without registry installation.
2. Initialize a target project with `.qc` phase records and run the phase loop.

## Easy PowerShell Install - Recommended

Use this when you want the easiest local installation path.

What it does:

- verifies the Builder Team QC plugin bundle shape
- verifies the expected plugin manifest version
- verifies the `0.2.0-trial` hardening helpers are present
- verifies the `0.2.1-trial` V03.1 patch record and recovery pack are present
- creates the target project folder if missing
- copies the plugin into the target project at `.codex/plugins/builder-team-qc`
- initializes the target project `.qc/` folder
- optionally starts the first phase

What it does not do:

- does not install globally
- does not write to Codex home or registry folders
- does not change PATH, registry, services, scheduled tasks, or system policy
- does not require secrets, API keys, network access, public tunnels, or remote services

From PowerShell:

```powershell
$PluginRoot = '<local-clone>\projects\builder-team-qc\plugin'
$TargetRoot = '<target-project>'
$BuildPlan = "$TargetRoot\build-plan.md"

powershell -NoProfile -ExecutionPolicy Bypass `
  -File "$PluginRoot\scripts\install-builder-team-qc.ps1" `
  -TargetRoot $TargetRoot `
  -StartPhase `
  -PhaseId phase-000 `
  -PhaseTitle 'Intake And Phase Selection' `
  -NextPhaseId phase-001 `
  -BuildPlan $BuildPlan
```

If the plugin is checked out in this standalone local folder, set `$PluginRoot` to that folder:

```powershell
$PluginRoot = '<local-path>\builder-team-qc'
```

Dry run first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "$PluginRoot\scripts\install-builder-team-qc.ps1" `
  -TargetRoot $TargetRoot `
  -StartPhase `
  -PhaseId phase-000 `
  -PhaseTitle 'Intake And Phase Selection' `
  -NextPhaseId phase-001 `
  -BuildPlan $BuildPlan `
  -DryRun
```

Useful options:

| Option | Meaning |
| --- | --- |
| `-DryRun` | Print/call dry-run actions without writing `.qc` records or copying the plugin. |
| `-SkipProjectPluginCopy` | Initialize `.qc` without copying the plugin into `.codex/plugins/`. |
| `-SkipQcInit` | Copy the plugin only; do not initialize `.qc`. |
| `-ForceTemplates` | Overwrite existing `.qc/templates`, `.qc/phase-board.json`, and `.qc/qc-config.json` seeds. |
| `-ExpectedVersion` | Require the manifest version, default `0.2.1-trial`. |
| `-UpgradeFromPrototype` | Preserve existing `.qc` records when upgrading a prototype install. |
| `-ValidateInstalled` | Validate the copied project-local plugin bundle and templates. |
| `-WriteInstallReport` | Write installed package metadata to `install-report.json`. |
| `-StartPhase` | Also run `start_phase.py` after `.qc` initialization. |
| `-Python <command-or-path>` | Use a specific Python executable. |

Rollback is local to the target project. Remove only the project-local paths you intended to create:

```powershell
Remove-Item -LiteralPath "$TargetRoot\.codex\plugins\builder-team-qc" -Recurse
Remove-Item -LiteralPath "$TargetRoot\.qc" -Recurse
```

Do not remove `.qc` if it contains phase evidence you need to keep.

## Prototype Or 0.2.0-Trial To 0.2.1-Trial Upgrade - Recommended For Existing Installs

Use this path when a target project already has the prototype copied to:

```text
<target-project>\.codex\plugins\builder-team-qc
```

This upgrade path:

- copies the local `0.2.1-trial` plugin bundle into the project
- preserves existing `.qc/` records by default
- validates the source and installed manifest version
- verifies the trial helper scripts and trial docs are present
- verifies the V03.1 docs sync patch and recovery pack are present
- optionally writes `install-report.json` inside the installed plugin copy

Dry run first:

```powershell
$PluginRoot = '<local-path>\builder-team-qc'
$TargetRoot = '<target-project>'

powershell -NoProfile -ExecutionPolicy Bypass `
  -File "$PluginRoot\scripts\install-builder-team-qc-0.2.1-trial.ps1" `
  -TargetRoot $TargetRoot `
  -DryRun
```

Apply the upgrade:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "$PluginRoot\scripts\install-builder-team-qc-0.2.1-trial.ps1" `
  -TargetRoot $TargetRoot `
  -WriteInstallReport
```

Fresh install is explicit:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "$PluginRoot\scripts\install-builder-team-qc-0.2.1-trial.ps1" `
  -TargetRoot $TargetRoot `
  -FreshInstall `
  -StartPhase `
  -PhaseId phase-000 `
  -PhaseTitle 'Intake And Phase Selection' `
  -NextPhaseId phase-001 `
  -BuildPlan $BuildPlan `
  -WriteInstallReport
```

Do not use `-ForceTemplates` for prototype or trial upgrades. If template refresh is required, back up `.qc/` first and treat it as a separate migration step.

Use `install-builder-team-qc-0.2.0-trial.ps1` only when intentionally installing the older `0.2.0-trial` package. The current latest trial installer is `install-builder-team-qc-0.2.1-trial.ps1`.

## 1. Prerequisites

Use a local Python runtime.

Use `python`, or set this to your own local Python executable without publishing the machine-specific path:

```powershell
$Python = 'python'
```

Set the plugin root:

```powershell
$PluginRoot = '<local-clone>\projects\builder-team-qc\plugin'
```

Public source path:

```text
https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents/plugin
```

Verify the plugin manifest:

```powershell
Get-Content -Raw -LiteralPath "$PluginRoot\.codex-plugin\plugin.json"
```

Verify the skills and scripts exist:

```powershell
Get-ChildItem -LiteralPath "$PluginRoot\skills"
Get-ChildItem -LiteralPath "$PluginRoot\scripts"
```

Verify the PowerShell installer exists:

```powershell
Get-Content -LiteralPath "$PluginRoot\scripts\install-builder-team-qc.ps1" -TotalCount 20
```

## 2. Installation Meaning

There are two different meanings of "install" for this plugin.

### Confirmed: Direct-Run Installation Into A Project

This means using the plugin scripts to create a project-local `.qc` hierarchy and run phase gates.

This is confirmed and tested.

### Not Yet Confirmed: Codex Plugin Registry Installation

This means making Codex discover and load the plugin automatically from its plugin registry or plugin home.

This was not confirmed in this thread. Do not copy this plugin into protected Codex home/plugin folders without explicit approval and a known rollback path.

Until registry installation is confirmed, use the direct-run method below.

## 3. Recommended Sandbox-First Setup

Create a sandbox target project:

```powershell
$TargetRoot = '<local-sandbox>\builder-team-qc-install-demo'
New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
```

Create or copy a build plan:

```powershell
$BuildPlan = "$TargetRoot\build-plan-phase-by-phase.md"
```

The build plan should follow:

```text
docs/build-plan-authoring-guide.md
```

At minimum, each phase must define:

- phase id
- phase type
- objective
- allowed change surface
- forbidden changes
- required test
- Ponytail checklist
- previous/current/next seam audit
- deviation stop rules
- acceptance gate

## 4. Phase 0 - Intake And Phase Selection

Before writing any durable `.qc` records, identify one phase only.

Required intake values:

```text
target_project_root: <absolute path>
build_plan: <absolute path>
current_phase_id: phase-000
current_phase_title: <title>
next_phase_id: <next phase or blank>
release_required: true|false
max_revise_attempts: 3
```

Do not start implementation if:

- the current phase cannot be named
- the phase spans multiple unrelated goals
- required proof/test is undefined
- protected zones are unclear
- release impact is unknown and cannot be classified

## 5. Phase 1 - Initialize QC State

Dry run first:

```powershell
& $Python "$PluginRoot\scripts\init_qc.py" `
  --root $TargetRoot `
  --dry-run
```

Then initialize the real project-local `.qc` hierarchy:

```powershell
& $Python "$PluginRoot\scripts\init_qc.py" `
  --root $TargetRoot
```

Expected project-local structure:

```text
.qc/
  phase-board.json
  qc-config.json
  issue-register.jsonl
  deviation-log.jsonl
  decision-log.jsonl
  ponytail-events.jsonl
  builder-scope-audits.jsonl
  test-results/
  phase-runs/
  templates/
```

Current helper note:

- `lessons-learned.jsonl` may still need to be created manually when lessons are recorded.

## 6. Phase 2 - Start Or Resume One Phase

Dry run optional phase start:

```powershell
& $Python "$PluginRoot\scripts\start_phase.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --title 'Intake And Phase Selection' `
  --next-phase-id phase-001 `
  --build-plan $BuildPlan `
  --dry-run
```

Start the real phase:

```powershell
& $Python "$PluginRoot\scripts\start_phase.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --title 'Intake And Phase Selection' `
  --next-phase-id phase-001 `
  --build-plan $BuildPlan
```

Expected phase-run structure:

```text
.qc/phase-runs/phase-000/
  phase-record.md
  builder-notes.md
  reviewer-report.md
  test-report.md
  compliance-report.md
  seam-audit.md
  release-gate.md
  evidence/
```

Current helper note:

- `changed-files.json`, `implementation-diff.patch`, and `gate-summary.md` may still need to be created manually.

## 7. Phase 3 - Builder Role With Scope Audit

Before builder edits, snapshot the file baseline:

```powershell
& $Python "$PluginRoot\scripts\audit_builder_scope.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --snapshot `
  --ignore capture/** `
  --json
```

Then perform only the phase-scoped builder work.

After builder edits, audit the allowed change surface:

```powershell
& $Python "$PluginRoot\scripts\audit_builder_scope.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --audit `
  --allow <allowed-path-or-glob> `
  --ignore capture/** `
  --json
```

If the audit fails:

1. Stop.
2. Record the deviation.
3. Write a stop report.
4. Ask the user if correcting the issue changes phase scope.
5. Rerun the audit after correction.

## 8. Phase 4 - Ponytail Minimal-Code Gate

Record Ponytail evidence:

```powershell
& $Python "$PluginRoot\scripts\record_ponytail_check.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --mode contained-workspace `
  --yagni-check 'Only current phase scope was built' `
  --stdlib-check 'Used stdlib/native/existing dependency where possible' `
  --dependency-check 'No unapproved dependency added' `
  --abstraction-check 'No unrequested abstraction added' `
  --minimum-code-verdict pass `
  --notes 'Minimal-code discipline checked'
```

Gate rule:

- `pass` continues.
- `revise` loops back to builder.
- `block` stops the phase.

The latest Ponytail event for the phase must be `pass` before final gate pass.

## 9. Phase 5 - Evidence Fan-Out

V01 runs these role checks sequentially.

Required role evidence:

```text
test-agent        -> test-report.md and .qc/test-results/<phase-id>.jsonl
reviewer-agent    -> reviewer-report.md
compliance-agent  -> compliance-report.md
integration-agent -> seam-audit.md
release-agent     -> release-gate.md when release_required=true
```

Record a test result:

```powershell
& $Python "$PluginRoot\scripts\record_test_result.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --name smoke `
  --command '<command run>' `
  --status pass `
  --exit-code 0 `
  --output-file '<optional log path>' `
  --notes 'Smoke check passed'
```

The role markdown files must be completed with final verdicts before strict gate:

```text
Verdict: pass
```

For release gate only, `Verdict: not_applicable` is allowed when `release_required=false`.

## 10. Phase 6 - In-Progress Validation

Run validation while work is in progress:

```powershell
& $Python "$PluginRoot\scripts\validate_phase_record.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --scan-safety `
  --require-builder-scope `
  --json
```

Meaning:

- warnings can exist while the phase is in progress
- errors must stop the phase
- safety findings with `severity=blocker` stop the phase
- safety findings with `severity=warning` or `severity=info` do not block by themselves

## 11. Phase 7 - Strict Gate Validation

Run the hard gate:

```powershell
& $Python "$PluginRoot\scripts\validate_phase_record.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --scan-safety `
  --strict-gate `
  --require-builder-scope `
  --json
```

For runtime, release, Docker, deployment, dependency, API, server, or production-debug phases:

```powershell
& $Python "$PluginRoot\scripts\validate_phase_record.py" `
  --root $TargetRoot `
  --phase-id phase-000 `
  --scan-safety `
  --strict-gate `
  --require-builder-scope `
  --release-phase `
  --json
```

Strict gate must return:

```json
{
  "errors": [],
  "warnings": [],
  "ok": true
}
```

Non-blocking safety warnings may appear and still allow `ok=true`.

## 12. Phase 8 - Revise Loop

If strict gate fails:

1. Fix only the smallest failing item.
2. Record the deviation or issue.
3. Rerun the affected proof.
4. Rerun the full proof set when shared contracts, schema, runtime, dependency, release behavior, or safety policy changed.
5. Stop after three failed revise attempts unless the user explicitly raises the cap.

Do not silently retry forever.

## 13. Phase 9 - Accepted Risk Path

Accepted risk requires a human decision.

The controller cannot self-approve accepted risk.

Use `record_decision.py` to append a JSONL record to:

```text
.qc/decision-log.jsonl
```

The decision must include:

- decision id
- phase id
- accepted by
- risk
- impact
- reason
- owner
- deadline or phase
- rollback
- follow-up

## 14. Phase 10 - Final Gate State Update

After strict gate passes, update:

```text
.qc/phase-board.json
```

Expected final pass state:

```json
{
  "current_phase_status": "complete",
  "latest_gate_decision": "pass",
  "blocking_issues": []
}
```

Current helper note:

- Use `record_gate_decision.py` to update `phase-board.json`, append `.qc/gate-events.jsonl`, and write `gate-summary.md`.
- Manual board edits are fallback-only and must be disclosed in the phase report.

## 15. Phase 11 - User-Facing Report

Summarize the phase:

```powershell
& $Python "$PluginRoot\scripts\summarize_phase.py" `
  --root $TargetRoot `
  --phase-id phase-000
```

The final report must include:

- phase id and title
- files changed
- commands run
- Ponytail verdict
- builder scope audit result
- test summary
- reviewer/compliance/seam/release verdicts
- strict gate command and result
- final gate decision
- phase-board update status
- next phase recommendation

Do not say complete unless strict gate and phase-board update are complete.

## 16. Phase 12 - Next Phase Handoff

Start the next phase only after:

```text
latest_gate_decision = pass
```

or after a valid:

```text
accepted_with_risk
```

with a human decision-log record.

Handoff must include:

- current phase gate result
- unresolved issues
- accepted-risk follow-ups
- next phase id and objective
- next phase inputs from seam audit
- release/debug concerns

## One-Page Install And Run Order

```text
0. Confirm plugin root, Python, target project, and build plan.
1. Run install-builder-team-qc.ps1 -DryRun.
2. Run install-builder-team-qc.ps1, usually with -StartPhase.
3. Run audit_builder_scope.py --snapshot.
4. Execute builder-agent work.
5. Run audit_builder_scope.py --audit --allow <paths>.
6. Run record_ponytail_check.py.
7. Run required test.
8. Run record_test_result.py.
9. Complete reviewer, compliance, seam, and release reports.
10. Run validate_phase_record.py --scan-safety --require-builder-scope.
11. Run validate_phase_record.py --strict-gate --scan-safety --require-builder-scope.
12. Revise or block if gate fails.
13. Update phase-board final state.
14. Run summarize_phase.py.
15. Report and hand off next phase.
```

## Recommended Codex Prompt

```text
Use builder-team-qc for this build.

Plugin root:
https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents/plugin

Target root:
<target project path>

Build plan:
<build plan path>

Current phase:
<phase id and title>

Run sandbox-first unless I approve durable direct work.
Follow docs/phase-by-phase-run-plan.md.
Use builder scope audit, Ponytail, quick test, safety scan, strict gate, stop reports, and phase-board update.
If any deviation or error requires scope, dependency, architecture, runtime, release, or safety-policy change, stop and ask before editing.
```

## Current Gaps To Remember

Confirmed helper gaps from the run plan:

- `lessons-learned.jsonl` may need manual creation.
- `changed-files.json` must be produced from the actual phase change set before Ponytail evidence binding.
- `implementation-diff.patch` must be produced from the actual phase diff before Ponytail evidence binding.
- `record_decision.py` is available for decision-log and accepted-risk records.
- `record_gate_decision.py` is available for phase-board transitions and gate summaries.
- A build-plan linter is still not implemented.

Current registry-install gap:

- The plugin is built, but this thread did not confirm it is installed into the active Codex plugin registry.
- Direct local script use is the confirmed installation/run path.
- The PowerShell installer performs a project-local copy and `.qc` initialization. It is not a Codex registry installer.
