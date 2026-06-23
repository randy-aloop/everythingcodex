# QC Record Schema

Builder Team QC stores local, inspectable records under `.qc/`. Records are local files. Do not store secrets, tokens, API keys, OAuth files, passwords, service account keys, or credentials.

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
| `latest_gate_at` | string | UTC timestamp for the latest final gate decision. |
| `release_required` | boolean | True when runtime, Docker, API, deploy, sidecar, dependency, or production-debug evidence is required. |
| `revise_attempts` | integer | Failed revise attempts in the current loop. |
| `max_revise_attempts` | integer | Default `3`; raising it requires explicit user approval. |
| `required_evidence` | array | Required evidence files and JSONL records. |
| `blocking_issues` | array | Current blocker ids or summaries. |

After final gate, the board must not remain `open` with `latest_gate_decision=pending`.

## Phase Run Directory

Directory: `.qc/phase-runs/<phase-id>/`

Required files:

| File | Required verdict |
| --- | --- |
| `phase-record.md` | `Gate Decision: pass`, `block`, or `accepted_with_risk` after final gate. |
| `builder-notes.md` | No formal verdict required, but scope and changed files must be filled. |
| `reviewer-report.md` | `Verdict: pass` for gate pass. |
| `test-report.md` | `Verdict: pass` for gate pass. |
| `compliance-report.md` | `Verdict: pass` for gate pass. |
| `seam-audit.md` | `Verdict: pass` for gate pass. |
| `release-gate.md` | `Verdict: pass` when `release_required=true`; `Verdict: not_applicable` only when `release_required=false`. |

Strict gate treats `Verdict: pending`, `Verdict: revise`, and `Verdict: block` as failures for required role reports.

## Ponytail Events

File: `.qc/ponytail-events.jsonl`

Required fields:

| Field | Type | Allowed values |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `phase_id` | string | Current phase id. |
| `mode` | string | `task-scoped`, `project-agents`, `contained-workspace`, or `unavailable-fallback`. |
| `yagni_check` | string | Non-empty rationale. |
| `stdlib_check` | string | Non-empty rationale. |
| `dependency_check` | string | Non-empty rationale. |
| `abstraction_check` | string | Non-empty rationale. |
| `minimum_code_verdict` | string | `pass`, `revise`, or `block`. |
| `notes` | string | Optional notes. |

Gate pass requires the latest event for the phase to have `minimum_code_verdict=pass`.

## Test Results

File: `.qc/test-results/<phase-id>.jsonl`

Required fields:

| Field | Type | Allowed values |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `phase_id` | string | Current phase id. |
| `name` | string | Stable check name. |
| `command` | string | Command or manual check description. |
| `status` | string | `pass`, `fail`, or `skipped`. |
| `exit_code` | integer or null | Process exit code when available. |
| `output_file` | string | Optional evidence path. |
| `notes` | string | Notes or skip reason. |
| `required` | boolean | True when this check is required for the phase. |

Strict gate requires at least one required non-skipped passing check. A skipped required check blocks unless a matching accepted-risk decision exists.

## Deviations

File: `.qc/deviation-log.jsonl`

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `phase_id` | string | Current phase id. |
| `expected` | string | Planned behavior or requirement. |
| `actual` | string | What happened instead. |
| `severity` | string | `low`, `medium`, `high`, or `blocker`. |
| `resolution` | string | Fix, mitigation, or pending state. |
| `accepted_by_user` | boolean | True only when backed by a decision-log record. |
| `decision_id` | string | Required when `accepted_by_user=true`. |

Unaccepted blocker deviations fail strict gate.

## Decisions

File: `.qc/decision-log.jsonl`

Accepted-risk records must include:

| Field | Type | Meaning |
| --- | --- | --- |
| `timestamp` | string | UTC timestamp. |
| `decision_id` | string | Stable id referenced by deviations or gate notes. |
| `phase_id` | string | Current phase id. |
| `decision_type` | string | `accepted_with_risk`, `approval`, or `override`. |
| `accepted_by` | string | Human approver or user identifier. |
| `risk` | string | What remains unverified or unsafe. |
| `impact` | string | Expected blast radius. |
| `reason` | string | Why the risk is accepted. |
| `owner` | string | Person responsible for follow-up. |
| `deadline` | string | Follow-up due date or phase. |
| `rollback` | string | How to undo or contain the risk. |
| `follow_up` | string | Next required check or fix. |

The controller must not self-approve accepted risk. A boolean in `deviation-log.jsonl` is not sufficient without a matching decision record.

## Gate Decision

Gate pass requires:

- all required role verdicts are `pass`
- latest Ponytail verdict is `pass`
- at least one required non-skipped test passed
- no recorded test failed
- no unaccepted blocker deviation exists
- safety scan has no blockers
- release gate is `pass` when `release_required=true`
- phase board is updated after the final decision

`accepted_with_risk` allows the next phase only when the decision-log record is complete and the phase board records the bypass.
