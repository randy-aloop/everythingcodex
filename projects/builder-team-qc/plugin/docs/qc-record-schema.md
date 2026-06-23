# QC Record Schema

Version: V02
Updated: 2026-06-23
Supersedes: V01

Builder Team QC stores local, inspectable records under `.qc/`. Records are local files. Do not store secrets, tokens, API keys, OAuth files, passwords, service account keys, or credentials.

This document is the deterministic record contract for the phase controller. When current scripts do not yet enforce a field, the controller must record the field manually and disclose that manual step in the phase report.

## Deterministic Conventions

Timestamps use UTC ISO 8601, such as `2026-06-23T15:00:00Z`.

Role verdicts are parsed from the first non-empty top-level line matching:

```text
Verdict: <value>
```

Allowed role verdict values are `pending`, `pass`, `revise`, `block`, and `not_applicable`. Parsing is case-insensitive for the label and value, but writers should use lowercase values. Missing verdicts, multiple conflicting verdicts, or unknown verdicts fail strict gate. For required reports, only `pass` can satisfy the gate. `not_applicable` is valid only for `release-gate.md` when `release_required=false` and a rationale is recorded.

Target validator exit-code contract:

| Exit code | Meaning |
| --- | --- |
| `0` | Validation passed. |
| `1` | Current implementation fallback: validation failed or validator reported errors. |
| `10` | Target contract: strict gate failed because evidence or role verdicts do not pass. |
| `20` | Target contract: schema, config, JSON, path, or invocation error. |
| `30` | Target contract: safety scan blocker. |

Confirmed current behavior: `validate_phase_record.py` currently returns `0` on success and `1` for any error. Until richer exit codes are implemented, the controller must read the printed JSON/text result and classify the failure in the phase report.

## QC Config

File: `.qc/qc-config.json`

This file defines project-level gate settings. It is read by the controller and should be read by scripts as they gain deterministic enforcement.

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Current schema version, starting at `1.0`. |
| `project_name` | string | Human-readable project name. |
| `default_max_revise_attempts` | integer | Default `3`; raising above `3` requires an explicit human decision. |
| `safety_scan_enabled` | boolean | Whether strict gate must run with `--scan-safety`. |
| `release_gate_default` | string | `auto`, `required`, or `not_required`. Use `auto` unless the user explicitly sets a policy. |
| `required_roles` | array | Role report files required for gate pass. |
| `required_test_policy` | object | Test requirement policy. |
| `protected_zones` | array | Paths or path patterns requiring approval before writes. |
| `remote_access_policy` | string | Default `deny`; remote/API access requires explicit approval. |
| `ponytail_modes_allowed` | array | Allowed Ponytail modes for this project. |

Example:

```json
{
  "schema_version": "1.0",
  "project_name": "builder-team-qc",
  "default_max_revise_attempts": 3,
  "safety_scan_enabled": true,
  "release_gate_default": "auto",
  "required_roles": [
    "reviewer-report.md",
    "test-report.md",
    "compliance-report.md",
    "seam-audit.md"
  ],
  "required_test_policy": {
    "minimum_required_passes": 1,
    "skipped_required_tests_block": true
  },
  "protected_zones": [],
  "remote_access_policy": "deny",
  "ponytail_modes_allowed": [
    "task-scoped",
    "project-agents",
    "contained-workspace",
    "unavailable-fallback"
  ]
}
```

## Phase Board

File: `.qc/phase-board.json`

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Current schema version, starting at `1.0`. |
| `current_phase_id` | string | Active phase id. |
| `current_phase_status` | string | `not_started`, `open`, `revising`, `blocked`, or `complete`. |
| `next_phase_id` | string | Planned next phase id, empty if unknown. |
| `latest_gate_decision` | string | `pending`, `pass`, `revise`, `block`, or `accepted_with_risk`. |
| `latest_gate_at` | string | UTC timestamp for the latest final gate decision; empty while pending. |
| `release_required` | boolean | True when runtime, Docker, API, deploy, sidecar, dependency, or production-debug evidence is required. |
| `release_not_applicable_rationale` | string | Required when `release_required=false` and release evidence is marked `not_applicable`. |
| `revise_attempts` | integer | Failed revise attempts in the current loop. |
| `max_revise_attempts` | integer | Default `3`; raising it requires explicit user approval. |
| `required_evidence` | array | Required evidence files and JSONL records. |
| `blocking_issues` | array | Current blocker ids or summaries. |
| `accepted_risk_decision_id` | string | Decision id when latest gate is `accepted_with_risk`; otherwise empty. |
| `updated_at` | string | UTC timestamp for the latest board update. |

Open-phase example:

```json
{
  "schema_version": "1.0",
  "current_phase_id": "phase-004",
  "current_phase_status": "open",
  "next_phase_id": "phase-005",
  "latest_gate_decision": "pending",
  "latest_gate_at": "",
  "release_required": false,
  "release_not_applicable_rationale": "Docs-only phase; no runtime, API, Docker, dependency, deploy, logging, rollback, or production-debug behavior changed.",
  "revise_attempts": 0,
  "max_revise_attempts": 3,
  "required_evidence": [
    "phase-record.md",
    "builder-notes.md",
    "changed-files.json",
    "implementation-diff.patch",
    "ponytail-events.jsonl",
    "test-results/phase-004.jsonl",
    "reviewer-report.md",
    "compliance-report.md",
    "seam-audit.md"
  ],
  "blocking_issues": [],
  "accepted_risk_decision_id": "",
  "updated_at": "2026-06-23T15:00:00Z"
}
```

After final gate, the board must not remain `open` with `latest_gate_decision=pending`.

## Phase Run Directory

Directory: `.qc/phase-runs/<phase-id>/`

Required files:

| File | Required verdict or content |
| --- | --- |
| `phase-record.md` | `Gate Decision: pass`, `block`, or `accepted_with_risk` after final gate. |
| `builder-notes.md` | Scope, changed files, assumptions, and implementation notes. |
| `changed-files.json` | Machine-readable list of files created, modified, deleted, or inspected for the phase. |
| `implementation-diff.patch` | Patch or equivalent diff summary for reviewer and compliance roles. |
| `reviewer-report.md` | `Verdict: pass` for gate pass. |
| `test-report.md` | `Verdict: pass` for gate pass. |
| `compliance-report.md` | `Verdict: pass` for gate pass. |
| `seam-audit.md` | `Verdict: pass` for gate pass. |
| `release-gate.md` | `Verdict: pass` when `release_required=true`; `Verdict: not_applicable` only when `release_required=false` and a rationale is recorded. |
| `gate-summary.md` | Final validator result, gate decision, and phase-board update note. |

Strict gate treats `Verdict: pending`, `Verdict: revise`, and `Verdict: block` as failures for required role reports.

## Changed Files And Diff Evidence

File: `.qc/phase-runs/<phase-id>/changed-files.json`

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Current schema version. |
| `phase_id` | string | Current phase id. |
| `attempt` | integer | Current builder or revise attempt. Starts at `1`. |
| `files` | array | File records. |
| `generated_at` | string | UTC timestamp. |

File record fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `path` | string | Project-relative path only. |
| `change_type` | string | `created`, `modified`, `deleted`, `renamed`, or `inspected`. |
| `reason` | string | Why the phase needed this file. |
| `phase_scoped` | boolean | True when the change belongs to the current phase. |

File: `.qc/phase-runs/<phase-id>/implementation-diff.patch`

The diff artifact should be generated after builder work and refreshed after each revise attempt. If a full patch cannot be produced, write a text summary that lists project-relative changed files and the reason each change belongs to the current phase.

Reviewer and compliance roles must use these artifacts instead of relying only on a chat summary.

## Ponytail Events

File: `.qc/ponytail-events.jsonl`

Required fields:

| Field | Type | Allowed values |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `phase_id` | string | Current phase id. |
| `attempt` | integer | Builder/revise attempt this check applies to. |
| `mode` | string | `task-scoped`, `project-agents`, `contained-workspace`, or `unavailable-fallback`. |
| `mode_source` | string | `controller`, `project-instructions`, `contained-workspace`, or `manual-fallback`. |
| `upstream_hook_enabled` | boolean | True only when upstream Ponytail code or hooks were explicitly reviewed and enabled. |
| `upstream_hook_review_id` | string | Required when `upstream_hook_enabled=true`; otherwise empty. |
| `yagni_check` | string | Non-empty rationale. |
| `stdlib_check` | string | Non-empty rationale. |
| `dependency_check` | string | Non-empty rationale. |
| `abstraction_check` | string | Non-empty rationale. |
| `minimum_code_verdict` | string | `pass`, `revise`, or `block`. |
| `notes` | string | Optional notes. |

Gate pass requires the latest event for the phase and attempt to have `minimum_code_verdict=pass`.

## Test Results

File: `.qc/test-results/<phase-id>.jsonl`

Required fields:

| Field | Type | Allowed values |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `phase_id` | string | Current phase id. |
| `attempt` | integer | Builder/revise attempt this result applies to. |
| `name` | string | Stable check name. |
| `command` | string | Command or manual check description. |
| `status` | string | `pass`, `fail`, or `skipped`. |
| `exit_code` | integer or null | Process exit code when available. |
| `output_file` | string | Optional evidence path. |
| `notes` | string | Notes or skip reason. |
| `required` | boolean | True when this check is required for the phase. |

Strict gate requires at least one required non-skipped passing check. A skipped required check blocks unless a matching accepted-risk decision exists.

Confirmed current helper gap: `record_test_result.py` does not yet accept `--required` or `--attempt`. Until it does, the controller must record required status and attempt number in `test-report.md` and treat missing machine-readable fields as a strict-gate limitation.

Target command contract:

```powershell
python scripts\record_test_result.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --attempt 1 `
  --name syntax `
  --command "<command run>" `
  --status pass `
  --exit-code 0 `
  --required `
  --notes "Syntax check passed"
```

## Deviations

File: `.qc/deviation-log.jsonl`

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `phase_id` | string | Current phase id. |
| `attempt` | integer | Attempt when the deviation was found. |
| `issue_id` | string | Matching issue id in `.qc/issue-register.jsonl`, or empty for informational deviations. |
| `expected` | string | Planned behavior or requirement. |
| `actual` | string | What happened instead. |
| `severity` | string | `low`, `medium`, `high`, or `blocker`. |
| `resolution` | string | Fix, mitigation, or pending state. |
| `accepted_by_user` | boolean | True only when backed by a decision-log record. |
| `decision_id` | string | Required when `accepted_by_user=true`. |

Unaccepted blocker deviations fail strict gate.

Confirmed current helper gap: `record_deviation.py` does not yet accept `--attempt`, `--issue-id`, or `--decision-id`. Until it does, the controller must add those fields manually when the deviation is gate-relevant.

Example:

```powershell
python scripts\record_deviation.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --expected "Required Docker smoke check passes" `
  --actual "Docker is unavailable on this machine" `
  --severity blocker `
  --resolution "Block phase or record accepted-risk human decision"
```

## Issue Register

File: `.qc/issue-register.jsonl`

This file is the durable list of blockers, revise items, review findings, and follow-up work created during phase control. Deviations may point to an issue id, and `blocking_issues` in `phase-board.json` should reference issue ids when possible.

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `issue_id` | string | Stable id, such as `issue-004-001`. |
| `phase_id` | string | Current phase id. |
| `attempt` | integer | Attempt when the issue was opened. |
| `source_role` | string | `builder`, `ponytail`, `test`, `reviewer`, `compliance`, `integration`, `release`, or `controller`. |
| `severity` | string | `low`, `medium`, `high`, or `blocker`. |
| `status` | string | `open`, `fixed`, `accepted_with_risk`, or `wont_fix`. |
| `summary` | string | Short issue summary. |
| `evidence` | string | Project-relative evidence path or command result. |
| `owner` | string | Owner or role responsible for resolution. |
| `resolution` | string | Fix, decision id, or reason. |

Strict gate must fail when a blocker issue remains `open`.

## Decisions

File: `.qc/decision-log.jsonl`

Accepted-risk records must include:

| Field | Type | Meaning |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `decision_id` | string | Stable id referenced by deviations, issues, or gate notes. |
| `phase_id` | string | Current phase id. |
| `decision_type` | string | `accepted_with_risk`, `approval`, `override`, or `revise_cap_change`. |
| `accepted_by` | string | Human approver or user identifier. |
| `risk` | string | What remains unverified or unsafe. |
| `impact` | string | Expected blast radius. |
| `reason` | string | Why the risk is accepted. |
| `owner` | string | Person responsible for follow-up. |
| `deadline` | string | Follow-up due date or phase. |
| `rollback` | string | How to undo or contain the risk. |
| `follow_up` | string | Next required check or fix. |

The controller must not self-approve accepted risk. A boolean in `deviation-log.jsonl` is not sufficient without a matching decision record.

Target helper contract:

```powershell
python scripts\record_decision.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --decision-type accepted_with_risk `
  --accepted-by "<human approver>" `
  --risk "<what remains unverified>" `
  --impact "<blast radius>" `
  --reason "<why accepted>" `
  --owner "<follow-up owner>" `
  --deadline "<date or phase>" `
  --rollback "<rollback path>" `
  --follow-up "<next required check>"
```

Confirmed current helper gap: `record_decision.py` does not exist yet. Until it exists, the controller must append the JSONL record manually and cite the decision id in the phase report.

## Release Not-Applicable Rationale

When `release_required=false`, `release-gate.md` may use `Verdict: not_applicable` only if it includes:

```text
Release Required: false
Not Applicable Rationale: <why this phase has no runtime, Docker, API, dependency, deploy, logging, rollback, sidecar, or production-debug impact>
Checked By: <role or user>
Checked At: <UTC timestamp>
```

The same rationale must be copied into `phase-board.json` as `release_not_applicable_rationale`.

## Lessons And Self-Improvement

File: `.qc/lessons-learned.jsonl`

Use this file for process lessons that should improve future phases without blocking the current gate.

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `phase_id` | string | Current phase id. |
| `lesson_id` | string | Stable id. |
| `source` | string | Role or validator that discovered it. |
| `lesson` | string | What should change in future phases. |
| `applies_to` | string | Future phase, role, script, doc, or policy. |
| `status` | string | `open`, `applied`, or `deferred`. |

Lessons are not a substitute for blockers. If the issue affects current correctness, record it in `issue-register.jsonl` and fail the gate.

## Gate Summary And Final Transition

File: `.qc/phase-runs/<phase-id>/gate-summary.md`

Required content:

- phase id and title
- final gate decision
- validator command
- observed validator exit code
- validator output summary
- role verdict table
- test result summary
- open issue count
- accepted-risk decision id, when applicable
- phase-board update status

Target helper contract:

```powershell
python scripts\record_gate_decision.py `
  --root <target-project> `
  --phase-id <phase-id> `
  --decision pass `
  --validator-exit-code 0 `
  --summary "<short gate summary>"
```

Confirmed current helper gap: `record_gate_decision.py` does not exist yet. Until it exists, the controller must update `phase-board.json` and write `gate-summary.md` manually.

## Phase Summary

Existing helper:

```powershell
python scripts\summarize_phase.py `
  --root <target-project> `
  --phase-id <phase-id>
```

Confirmed current behavior: the helper prints JSON to stdout and does not write an output file. The controller should capture or paste the summary into `gate-summary.md` when closing a phase.

## Gate Decision

Gate pass requires:

- all required role verdicts are `pass`
- latest Ponytail verdict for the current attempt is `pass`
- at least one required non-skipped test passed
- no recorded test failed
- no blocker issue remains open
- no unaccepted blocker deviation exists
- safety scan has no blockers
- release gate is `pass` when `release_required=true`
- release gate has a valid `not_applicable` rationale when `release_required=false`
- phase board is updated after the final decision

`accepted_with_risk` allows the next phase only when the decision-log record is complete and the phase board records the bypass.
