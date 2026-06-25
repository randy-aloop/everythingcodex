# Builder Team QC Sandbox Demo Runbook

This runbook shows how to run the built `builder-team-qc` plugin without installing it, using the plugin scripts directly against a disposable sandbox project.

## Demo Result

Demo root:

```powershell
<sandbox-root>\builder-team-qc-demo-<timestamp>
```

Demo capture:

```powershell
<sandbox-root>\builder-team-qc-demo-<timestamp>\DEMO-RUN-CAPTURE.md
```

Strict gate result:

```json
{
  "errors": [],
  "warnings": [],
  "ok": true
}
```

## What The Demo Proved

- The plugin can initialize a project-local `.qc` hierarchy.
- The plugin can open a phase run from a phase-by-phase build plan.
- The phase run creates structured role files for builder, reviewer, test, compliance, seam audit, and release gate.
- Ponytail/minimal-code evidence can be recorded.
- A quick phase test can be recorded.
- The context-aware safety scanner can run during the gate.
- The strict phase gate can pass when required evidence is complete.

## Sandbox Run Steps

Set these variables first:

```powershell
$Python = '<python-executable>'
$Plugin = '<repo-root>\plugin'
$ProjectRoot = '<sandbox-root>\your-demo-project'
$BuildPlan = "$ProjectRoot\build-plan-phase-by-phase.md"
```

Create or copy your phase-by-phase build plan into `$BuildPlan`, then run a dry run:

```powershell
& $Python "$Plugin\scripts\init_qc.py" --root $ProjectRoot --dry-run
```

Initialize the real project-local QC hierarchy:

```powershell
& $Python "$Plugin\scripts\init_qc.py" --root $ProjectRoot
```

Start the first phase:

```powershell
& $Python "$Plugin\scripts\start_phase.py" `
  --root $ProjectRoot `
  --phase-id phase-000 `
  --title 'Intake And Phase Selection' `
  --next-phase-id phase-001 `
  --build-plan $BuildPlan
```

Execute the phase work exactly as the build plan requires. Keep the implementation modular and easy to debug.

Complete the generated phase evidence files:

```powershell
$PhaseDir = "$ProjectRoot\.qc\phase-runs\phase-000"
```

Required files:

- `phase-record.md`
- `builder-notes.md`
- `reviewer-report.md`
- `test-report.md`
- `compliance-report.md`
- `seam-audit.md`
- `release-gate.md`

Record the Ponytail/minimal-code check:

```powershell
& $Python "$Plugin\scripts\record_ponytail_check.py" `
  --root $ProjectRoot `
  --phase-id phase-000 `
  --mode contained-workspace `
  --yagni-check 'only the needed phase work was built' `
  --stdlib-check 'used existing project/plugin tools first' `
  --dependency-check 'no unnecessary dependency added' `
  --abstraction-check 'no unnecessary abstraction added' `
  --minimum-code-verdict pass `
  --notes 'phase evidence complete'
```

Run a quick test for the phase, then record it:

```powershell
& $Python "$Plugin\scripts\record_test_result.py" `
  --root $ProjectRoot `
  --phase-id phase-000 `
  --name 'phase-000-smoke-test' `
  --command 'describe the command you ran' `
  --status pass `
  --exit-code 0 `
  --notes 'quick phase test passed'
```

If a deviation, error, or required iteration appears, stop and record it before continuing:

```powershell
& $Python "$Plugin\scripts\record_deviation.py" `
  --root $ProjectRoot `
  --phase-id phase-000 `
  --expected 'what the build plan required' `
  --actual 'what happened instead' `
  --severity blocker `
  --resolution 'waiting for user decision before changing the build'
```

Run the gate:

```powershell
& $Python "$Plugin\scripts\validate_phase_record.py" `
  --root $ProjectRoot `
  --phase-id phase-000 `
  --strict-gate `
  --scan-safety `
  --json
```

Summarize the phase:

```powershell
& $Python "$Plugin\scripts\summarize_phase.py" `
  --root $ProjectRoot `
  --phase-id phase-000
```

Only start the next phase after the gate passes and the previous/current/next seam audit is complete.

## How To Use This In Codex For Another Project

When you have a build plan for another project, give Codex the project root and build plan path, then ask it to run the builder-team QC process. Use this prompt shape:

```text
Use the builder-team-qc plugin workflow for this project.

Project root:
<absolute project path>

Build plan:
<absolute build plan path>

Start at:
phase-000

Run it first in `<sandbox-root>` before touching the durable project folder.
For each phase:
1. Check the build plan doc.
2. Execute only what the build plan requires.
3. Catch deviations or errors during build.
4. Run a quick test for the phase.
5. Catch bugs or errors during the run.
6. Log and report.
7. File the work process in the structured .qc hierarchy.
8. Audit current phase completion.
9. Cross-check previous/current/next phase seams.
10. Start the next phase only after the gate passes.

If any iteration or change is needed, stop and write a detailed report before changing the build.
```

For production project work, replace the sandbox `$ProjectRoot` with the real project root only after the sandbox run is reviewed or explicitly approved.
