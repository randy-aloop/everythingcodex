# DOC-03 Required-Test Finding Assessment

Date: 2026-06-25
Status: assessed, no code/doc patch applied

## Verdict

DOC-03 correctly describes the implemented `0.2.1-trial` validator behavior: strict gate requires at least one passing test row where `required=true`; an optional passing test alone does not satisfy the gate; an accepted-risk decision does not exempt a skipped required test.

However, DOC-03's documentation-drift finding is stale against the current local source, installed local plugin, and `everythingcodex` package mirror. The four affected docs are already `V03.1`, and the stale phrases listed by DOC-03 are no longer present in the current docs.

The current issue is not broken code. The current code and docs are aligned. The remaining opportunity is wording polish: DOC-03 wants the exact phrase "required non-skipped passing test" everywhere, while current docs use equivalent wording such as "required test has status `pass`" and "a required test marked `skipped` blocks strict validation."

## Where The Behavior Lives In Code

Current source code:

- `scripts/validate_phase_record.py`
  - Builds `latest_required` from test rows where `row.get("required")` is true.
  - Counts only required rows with `status == "pass"`.
  - Emits `no required non-skipped passing test result for phase` if the count is below `minimum_required_passes`.
  - Emits `required test skipped: <name>` when a latest required row has `status == "skipped"`.

- `scripts/builder_team_qc_lib.py`
  - Defaults `required_test_policy.minimum_required_passes` to `1`.
  - Defaults `required_test_policy.skipped_required_tests_block` to `true`.
  - Defaults release auto-detection through `release_phase_patterns`.

This confirms Option A is active in current code.

## Three Verification Passes

### Pass 1 - Source Code And Source Docs

Scope:

- `builder-team-qc/scripts/validate_phase_record.py`
- `builder-team-qc/scripts/builder_team_qc_lib.py`
- `builder-team-qc/docs/multi-agent-modes.md`
- `builder-team-qc/docs/phase-loop.md`
- `builder-team-qc/docs/qc-record-schema.md`
- `builder-team-qc/docs/orchestration-notes.md`

Result:

- Source docs are `Version: V03.1`.
- Stale phrase scan returned no matches for:
  - `until implemented`
  - `does not yet support`
  - `until those helpers exist`
  - `currently returns`
  - `unless a matching accepted-risk`
  - `planned but not`
- Required-test wording exists in all four docs.
- Source code contains the required-only count through `latest_required` and `required_pass_count`.

Assessment:

DOC-03's current-state claim that these docs are still V03/partially stale is false for the current source tree.

### Pass 2 - Installed Local Plugin

Scope:

```text
builder-team-qc/.codex/plugins/builder-team-qc/
```

Result:

- Installed docs are `Version: V03.1`.
- Installed stale phrase scan returned no matches.
- Installed docs contain required-test wording in all four files.
- Installed code has the same `latest_required` / `required_pass_count` logic as source.

Assessment:

The local installed `0.2.1-trial` package is aligned with source.

### Pass 3 - Runtime Gate Fixtures

Runtime fixture root:

```text
installer-tests/doc03-required-test-runtime-20260625
```

Executed against the installed local validator:

```text
builder-team-qc/.codex/plugins/builder-team-qc/scripts/validate_phase_record.py
```

Results:

| Case | Expected | Observed |
| --- | --- | --- |
| Optional passing test only | strict gate failure | exit `10`, `no required non-skipped passing test result for phase` |
| Required passing test | strict gate pass | exit `0`, `ok: true` |
| Required skipped test plus accepted-risk decision | strict gate failure | exit `10`, `no required non-skipped passing test result for phase`; `required test skipped: required smoke` |
| Release phase auto-detected with `release-gate.md` not applicable | strict gate failure | exit `10`, `release phase requires release-gate verdict pass, got not_applicable` |

Assessment:

Runtime behavior confirms DOC-03's code-behavior claims. It also confirms current docs describe the same behavior.

## Correctness Assessment Of DOC-03

True:

- The validator requires required-test proof.
- Optional passing tests alone fail strict gate.
- Skipped required tests fail strict gate.
- Accepted risk is not a validator exemption for skipped required tests.
- Release auto-detection exists and `--release-phase` is an override.

False or stale in current workspace:

- The four docs are not currently V03; they are V03.1.
- The listed stale helper-gap phrases are not present in current source docs, installed docs, or package mirror docs.
- `qc-record-schema.md` and `orchestration-notes.md` have already been patched.
- DOC-03 no longer needs to land as a four-doc reconciliation patch unless the goal is wording normalization.

Partially true:

- DOC-03 says all four docs should use the exact phrase "at least one required non-skipped passing test." Current docs use semantically equivalent but not identical wording. This is not a gate correctness issue, but a style/consistency issue.

## Next Way Forward

Recommended action: do not apply DOC-03 as written. Mark it as superseded or already resolved by the current `0.2.1-trial` V03.1 sync.

Action points:

1. Create a small DOC-03 closeout note that changes DOC-03 status from `Proposed` to `Superseded / Already Resolved`.
2. Optionally apply a docs-only wording-normalization patch so all four docs use one canonical phrase:

```text
at least one required test must have status `pass`; any required test with status `skipped` blocks strict validation
```

3. Add a persistent regression fixture for the four runtime cases above so future validator edits cannot accidentally return to "any passing test" behavior.
4. Add the DOC-03 runtime fixture result to the next trial report or stress harness addendum.
5. Keep code unchanged. Current code behavior is correct and matches the intended `0.2.1-trial` contract.

## Decision Recommendation

Decision: supersede DOC-03 as an implementation patch; retain it as historical evidence of the required-test contract.

Reason:

The finding was valid against an earlier state and remains useful as a statement of the desired contract, but the current source, installed package, and mirror docs already satisfy the substantive requirements.
