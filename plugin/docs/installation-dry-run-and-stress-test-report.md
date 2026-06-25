# Installation Dry Run And Stress Test Report

Version: V02
Updated: 2026-06-24
Supersedes: V01 unversioned report

This report compiles the installation progress, dry runs, and stress tests performed for `builder-team-qc`.

## Current Installation Status

`builder-team-qc` is built as a local Codex plugin bundle.

Confirmed public source artifact:

```text
https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents/plugin
```

Confirmed manifest:

```text
.codex-plugin/plugin.json
expected version: 0.2.0-trial
```

Confirmed package shape:

- `.codex-plugin/plugin.json`
- `skills/`
- `scripts/`
- `assets/`
- `docs/`

Confirmed direct-run installation mode:

- Use local helper scripts directly from `scripts/`.
- Initialize a target project's `.qc` folder.
- Run the phase loop against a sandbox or target project.
- Use `scripts/install-builder-team-qc.ps1` as the easy PowerShell front door for project-local install and first-run setup.
- Use `scripts/install-builder-team-qc-0.2.0-trial.ps1` as the safe prototype-to-trial upgrade front door.

Not confirmed yet:

- Installed into the active Codex plugin registry.
- Auto-loaded as a plugin/skill set in the active Codex session.

## 0.2.0-Trial Installer Addendum

The `0.2.0-trial` installer layer adds:

- manifest version enforcement for `0.2.0-trial`
- required-file checks for the hardening helpers, trial docs, templates, and role skills
- installed-copy validation through the copied project-local plugin
- a prototype-upgrade wrapper that preserves existing `.qc/` records by default
- optional `install-report.json` output inside the installed plugin copy

The installer remains project-local. It does not register the plugin globally with Codex and does not write to Codex home, registry folders, system policy, PATH, scheduled tasks, or remote services.

Verification performed for this addendum:

- Python helper compile passed for the `0.2.0-trial` script set.
- Trial wrapper dry-run passed with `-FreshInstall`, `-StartPhase`, and installed-copy validation enabled.
- Fresh sandbox install passed at `<local-sandbox>/trial-fresh-install-<redacted-run-id>`; installed manifest reported `0.2.0-trial`, `record_gate_decision.py` existed, and `install-report.json` was written.
- Simulated prototype upgrade passed at `<local-sandbox>/trial-upgrade-prototype-<redacted-run-id>`; installed manifest changed from `0.1.0` to `0.2.0-trial`, `.qc` marker data was preserved, `record_gate_decision.py` existed, and `install-report.json` was written.
- Mirrored repository plugin wrapper dry-run passed from the local `everythingcodex` branch package.

## Tested Python Runtime

The tested runtime was a local Python 3.13 interpreter. Do not publish workstation-specific interpreter paths in this report.

```powershell
python
```

## Installation Progress Summary

| Area | Status | Evidence |
| --- | --- | --- |
| Plugin manifest exists | Pass | `.codex-plugin/plugin.json` |
| Skills directory exists | Pass | `skills/` |
| Helper scripts exist | Pass | `scripts/` |
| Easy PowerShell installer exists | Pass | `scripts/install-builder-team-qc.ps1` |
| Trial upgrade wrapper exists | Pass | `scripts/install-builder-team-qc-0.2.0-trial.ps1` |
| Trial manifest version enforced | Pass | installer requires `0.2.0-trial` unless explicitly overridden |
| Trial helper coverage enforced | Pass | installer checks `audit_builder_scope.py`, `record_decision.py`, `record_gate_decision.py`, Ponytail, validator, docs, templates, and skills |
| Direct `.qc` initialization | Pass | sandbox demo and full-loop stress |
| Dry-run no-write behavior | Pass | init/start dry-run checks |
| Phase creation | Pass | `.qc/phase-runs/<phase-id>/` |
| Builder scope audit | Pass | native script proof |
| Ponytail enforcement | Pass | negative and positive control |
| Strict gate validation | Pass | multiple sandbox runs |
| Self-correction loop | Pass | full-loop and builder-agent stress |
| Stop report behavior | Pass as Codex workflow evidence | builder-agent current stress |
| Codex registry install | Not confirmed | no installed registry copy found |

## Dry Run 1 - Basic Installation Demo

Sandbox root:

```text
<local-sandbox>/builder-team-qc-demo-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/builder-team-qc-demo-<redacted-run-id>/DEMO-RUN-CAPTURE.md
```

Result:

```text
strict gate passed
```

Command sequence tested:

1. `init_qc.py --dry-run`
2. `init_qc.py`
3. `start_phase.py --phase-id phase-000`
4. create minimal demo artifact
5. complete phase evidence files
6. `record_ponytail_check.py`
7. run smoke test
8. `record_test_result.py`
9. `validate_phase_record.py --strict-gate --scan-safety --json`
10. `summarize_phase.py`

What this proved:

- The plugin can be used directly without registry installation.
- `.qc` hierarchy can be initialized in a sandbox target.
- A phase can be started.
- Required evidence files can be completed.
- Ponytail, test recording, strict validation, and summary can run.

## Dry Run 2 - Full Phase Loop Stress Test

Sandbox root:

```text
<local-sandbox>/builder-team-qc-full-loop-stress-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/builder-team-qc-full-loop-stress-<redacted-run-id>/FULL-DRY-RUN-STRESS-CAPTURE.md
```

Result summary:

```text
Phases executed: 13
Final strict safety gates passed: 13
Expected failure/checkpoint cases exercised: 5
Unexpected unresolved failures: 0
Recorded test rows: 13
Recorded deviation rows: 3
Self-improvement events: 3
```

Stress cases tested:

1. Invalid phase ID was rejected before phase creation.
2. Missing phase validation failed as expected.
3. Missing test evidence caused a strict gate failure.
4. Synthetic denylist-trigger scanner material caused a safety blocker.
5. Placeholder-only correction still blocked because the risky field name remained.
6. Removing the risky field name cleared the gate.
7. Documentation policy/reference lines remained non-blocking.

What this proved:

- The full phase loop can run from `phase-000` through `phase-012`.
- The strict gate blocks incomplete or unsafe phases.
- Deviations are logged.
- The loop can self-correct inside sandbox and rerun gates.
- Safety scanner classification works as intended: blockers fail, non-blocking doc/reference findings do not fail.

## Dry Run 3 - Native Builder Scope Audit Proof

Sandbox root:

```text
<local-sandbox>/builder-scope-native-test-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/builder-scope-native-test-<redacted-run-id>/BUILDER-SCOPE-NATIVE-TEST-CAPTURE.md
```

Final gate:

```json
{
  "errors": [],
  "warnings": [],
  "ok": true
}
```

What this proved:

- `audit_builder_scope.py --snapshot` creates `builder-scope-baseline.json`.
- `audit_builder_scope.py --audit` fails when an unexpected file appears.
- The audit passes after the unexpected file is removed.
- `validate_phase_record.py --require-builder-scope` enforces the audit at strict gate.
- Harness logs can be ignored with `--ignore capture/**`.

## Dry Run 4 - Builder Agent Current Stress Test

Sandbox root:

```text
<local-sandbox>/builder-agent-current-dryrun-stress-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/builder-agent-current-dryrun-stress-<redacted-run-id>/BUILDER-AGENT-CURRENT-DRYRUN-STRESS-CAPTURE.md
```

Result summary:

```text
Builder phases executed: 5
Final strict gates passed: 5
Expected stop/failure checkpoints: 4
Unresolved failures: 0
Deviation records: 4
Stop reports: 4
Test records: 5
Builder scope audit records: 8
Self-improvement events: 4
```

Stress cases tested:

1. Overbuild added `src/future_engine.py`.
2. Missing test evidence caused strict gate failure.
3. Dependency creep added `requirements.txt`.
4. Doc-only phase created an unexpected code file.

What this proved:

- Builder scope audit catches overbuild.
- Strict gate catches missing test evidence.
- Builder scope audit catches unapproved dependency file creation.
- Builder scope audit catches doc-only phase drift.
- Each issue produced:
  - failed audit or gate
  - deviation log entry
  - stop report
  - correction
  - rerun
  - final pass

Stop-and-ask status:

- The scripts stop by returning non-zero or failing strict gate.
- The sandbox run wrote stop reports for the user-decision point.
- Script-only mode does not ask interactively by itself.
- The Codex controller workflow must ask the user before applying a real correction when the fix changes scope, dependency, architecture, runtime, release, or safety policy.

## Dry Run 5 - Ponytail Enforcement Proof

Sandbox root:

```text
<local-sandbox>/ponytail-enforcement-proof-<redacted-run-id>
```

Capture:

```text
<local-sandbox>/ponytail-enforcement-proof-<redacted-run-id>/PONYTAIL-ENFORCEMENT-PROOF.md
```

Negative control:

```json
{
  "errors": [
    "latest ponytail event is not pass"
  ],
  "warnings": [],
  "ok": false
}
```

Positive control:

```json
{
  "errors": [],
  "warnings": [],
  "ok": true
}
```

What this proved:

- Ponytail is not only a note.
- The strict gate fails when the latest Ponytail verdict is not `pass`.
- The strict gate passes after a later Ponytail event records `pass`.

## Dry Run 6 - Easy PowerShell Installer Proof

Sandbox root:

```text
<local-sandbox>/ps-install-<redacted-run-id>
```

Commands tested:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "$PluginRoot\scripts\install-builder-team-qc.ps1" `
  -TargetRoot $TargetRoot `
  -Python $Python `
  -StartPhase `
  -PhaseId phase-000 `
  -PhaseTitle 'Intake And Phase Selection' `
  -NextPhaseId phase-001 `
  -BuildPlan $BuildPlan `
  -DryRun

powershell -NoProfile -ExecutionPolicy Bypass `
  -File "$PluginRoot\scripts\install-builder-team-qc.ps1" `
  -TargetRoot $TargetRoot `
  -Python $Python `
  -StartPhase `
  -PhaseId phase-000 `
  -PhaseTitle 'Intake And Phase Selection' `
  -NextPhaseId phase-001 `
  -BuildPlan $BuildPlan
```

Result summary:

```text
Dry-run installer: PASS
Real sandbox install: PASS
Template validation after install: PASS
Repeat install against same target: PASS
```

Template validation result after install:

```json
{
  "errors": [],
  "warnings": [],
  "ok": true
}
```

What this proved:

- The PowerShell installer can resolve the plugin root from its own script location.
- The installer verifies `.codex-plugin/plugin.json`, `assets/`, `docs/`, `scripts/`, and `skills/`.
- The installer copies the plugin into a target-project-local `.codex/plugins/builder-team-qc` folder.
- The installer initializes `.qc/`.
- The installer can start `phase-000`.
- The installer can be rerun against the same target without failing.
- The installer does not perform global Codex registry installation.

## Installation Commands Proven

These commands were exercised across the dry runs and stress tests:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$PluginRoot\scripts\install-builder-team-qc.ps1" -TargetRoot $TargetRoot -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File "$PluginRoot\scripts\install-builder-team-qc.ps1" -TargetRoot $TargetRoot -StartPhase -PhaseId phase-000 -PhaseTitle 'Intake And Phase Selection' -NextPhaseId phase-001 -BuildPlan $BuildPlan
& $Python "$PluginRoot\scripts\init_qc.py" --root $TargetRoot --dry-run
& $Python "$PluginRoot\scripts\init_qc.py" --root $TargetRoot
& $Python "$PluginRoot\scripts\start_phase.py" --root $TargetRoot --phase-id <phase-id> --title '<title>' --build-plan $BuildPlan
& $Python "$PluginRoot\scripts\audit_builder_scope.py" --root $TargetRoot --phase-id <phase-id> --snapshot --ignore capture/** --json
& $Python "$PluginRoot\scripts\audit_builder_scope.py" --root $TargetRoot --phase-id <phase-id> --audit --allow <path> --ignore capture/** --json
& $Python "$PluginRoot\scripts\record_ponytail_check.py" --root $TargetRoot --phase-id <phase-id> --mode contained-workspace --minimum-code-verdict pass
& $Python "$PluginRoot\scripts\record_test_result.py" --root $TargetRoot --phase-id <phase-id> --name <name> --command '<command>' --status pass --exit-code 0
& $Python "$PluginRoot\scripts\validate_phase_record.py" --root $TargetRoot --phase-id <phase-id> --scan-safety --strict-gate --require-builder-scope --json
& $Python "$PluginRoot\scripts\summarize_phase.py" --root $TargetRoot --phase-id <phase-id>
```

## What Passed

- Direct local plugin use.
- Easy PowerShell installer wrapper.
- Project-local plugin copy to `.codex/plugins/builder-team-qc`.
- Sandbox-first installation flow.
- `.qc` initialization.
- Phase run creation.
- Builder scope baseline and audit.
- Ponytail recording and enforcement.
- Test result recording.
- Safety scan blocker classification.
- Strict gate validation.
- Full phase loop.
- Builder-agent role stress.
- Stop report generation in the Codex workflow.
- Self-correction and rerun after logged deviations.

## What Failed Intentionally And Was Corrected

| Failure | Detected By | Correction |
| --- | --- | --- |
| Invalid phase ID | `start_phase.py` argument validation | rejected before phase creation |
| Missing phase directory | `validate_phase_record.py` | failed as expected |
| Missing test evidence | strict gate | recorded test result and reran gate |
| Synthetic denylist-trigger file | safety scan | removed risky field name and reran gate |
| Placeholder denylist field still blocked | safety scan | replaced with neutral field name |
| Unexpected builder file | builder scope audit | removed unrequested file |
| Unapproved dependency file | builder scope audit | removed dependency file |
| Doc-only phase created code | builder scope audit | removed code file |
| Ponytail `revise` verdict | strict gate | recorded later Ponytail `pass` event |

## Remaining Gaps

The installation progress is strong for direct local script use, but not complete for full registry/plugin installation.

Remaining gaps:

- Codex plugin registry installation has not been confirmed.
- Active-session plugin loading has not been confirmed.
- The PowerShell installer is project-local only; it does not register the plugin globally with Codex.
- `changed-files.json` must still be produced from the actual phase change set before Ponytail evidence binding.
- `implementation-diff.patch` must still be produced from the actual phase diff before Ponytail evidence binding.
- `lessons-learned.jsonl` may still need manual creation.
- A build-plan linter has not yet been built.
- A real product build trial has not yet proven the full `0.2.0-trial` path outside synthetic/sandbox targets.

Resolved in `0.2.0-trial`:

- `record_decision.py` exists for decision-log and accepted-risk records.
- `record_gate_decision.py` exists for phase-board transitions, `.qc/gate-events.jsonl`, and `gate-summary.md`.
- The installer validates the trial helper set before copying the plugin bundle.

## Current Verdict

Direct-run installation and first-run workflow:

```text
PASS
```

Sandbox dry-run behavior:

```text
PASS
```

Stress-test behavior:

```text
PASS
```

Self-correction and logging:

```text
PASS
```

Stop-and-ask process:

```text
PARTIAL PASS
```

Reason:

- The process stops and writes stop reports.
- The scripts do not ask interactively by themselves.
- The Codex controller must ask the user at the stop report before applying scope-changing corrections.

Codex registry installation:

```text
NOT CONFIRMED
```

Recommended next step:

```text
Build a registry-install procedure or install checker, then run a separate plugin installation stress test.
```
