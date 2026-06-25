# Documentation Patch DOC-V03-SYNC-TO-CODE-EXPANDED - Builder-Team-QC Docs Sync-To-Code

| Field | Value |
| --- | --- |
| Change ID | `DOC-V03-SYNC-TO-CODE-EXPANDED` |
| Thing being versioned | `builder-team-qc documentation patch plan and optional validator policy` |
| Current version | `0.2.0-trial docs V03 with incomplete sync-to-code patch` |
| Target version | `0.2.0-trial docs V03.1 sync-to-code` |
| Version movement | `docs-only patch plan with optional code-hardening companion` |
| Scope | `docs/multi-agent-modes.md`, `docs/phase-loop.md`, `docs/qc-record-schema.md`, `docs/orchestration-notes.md`, `docs/CHANGELOG.md`, optional `scripts/validate_phase_record.py`, package mirror docs, static site scan |
| Status | `Executed` |
| Owner | `Randy / Codex phase-controller` |
| Evidence basis | `fable5 audit, patch review, code/script inspection, stale-language scan, git apply check` |
| Parent / companion | `docs/docs-v03-sync-to-code-expanded-patch-plan.md`; redacted local Fable5 review record; redacted local Fable5 audit record; redacted local Desktop patch |
| Created | `2026-06-25` |
| Last updated | `2026-06-25` |

---

## 1. Summary

This version record converts `docs/docs-v03-sync-to-code-expanded-patch-plan.md` into the standard versioning-anything format. It tracks the proposed expansion of `docs-v03-sync-to-code.patch` from a one-file documentation patch into a coherent V03.1 sync-to-code change for the builder-team-qc system.

The shortest useful version:

- From: `a Desktop patch that applies cleanly but only updates docs/multi-agent-modes.md`
- To: `a complete docs V03.1 sync that aligns all live operating docs with implemented 0.2.0-trial code`
- Because: `agents currently risk reading conflicting instructions about implemented recorder helpers, validator exit codes, release auto-detection, accepted-risk handling, and required-test behavior`

## 2. Version Intent

This version exists to document and prepare a complete sync between the implemented `0.2.0-trial` code and the live operating documentation that agents and operators read during a builder-team-qc run.

It should be considered successful when:

1. Live docs no longer claim implemented recorder helpers are missing.
2. Strict-gate docs describe classified validator exit codes as current behavior.
3. Accepted-risk is documented as a final gate-decision path, not a validator-level exemption for skipped required tests.
4. The required-test policy fork is explicitly resolved or documented.
5. Agent stress evidence is rerun after the expanded patch lands.

It is not intended to:

1. Rewrite historical patch-proposal files under `docs/0.1.0-Trial/`.
2. Apply the patch automatically.
3. Replace the full implementation report or stress harness evidence.

## 3. Why This Is Versioned

This deserves a version boundary because it changes the operational contract read by the multiagent builder roles. The docs are not passive notes: `phase-controller`, `test-agent`, `compliance-agent`, `ponytail-adapter`, and release checks all use them as run guidance.

If this changed silently, agents could disagree about whether to call helpers or hand-edit evidence. That would make `.qc/` records less deterministic and could cause false green or false red gate outcomes.

This version supersedes the incomplete Desktop patch as the recommended patch shape. It does not supersede the historical review records; those remain evidence.

## 4. Current State

Execution note: this section records the pre-landing state that justified the patch. The patch was later executed with the Option A validator fix.

Current behavior:

- The redacted local Desktop patch applies cleanly, but only modifies `docs/multi-agent-modes.md`.
- The patch does not include `docs/phase-loop.md`, even though the rationale said it should.
- `docs/orchestration-notes.md` still contains stale helper-gap statements for `record_test_result.py` (L272) and `record_deviation.py` (L325), plus stale manual `--release-phase` guidance (L363) even though the validator now auto-detects release phases.
- Both `docs/orchestration-notes.md` (L285) and `docs/qc-record-schema.md` (L248) still say a skipped required check is bypassed by an accepted-risk decision, which the validator does not implement. `docs/qc-record-schema.md`'s recorder-flag descriptions are already current ("Confirmed current behavior").
- The validator currently counts any passing test row for `minimum_required_passes`, while the surrounding docs and error text imply a required passing test.

Evidence:

- Redacted local Fable5 review record.
- Redacted local Fable5 audit record.
- `docs/docs-v03-sync-to-code-expanded-patch-plan.md`
- Redacted local Desktop patch.

Known gaps:

- The `multi-agent-modes.md` + `phase-loop.md` portion of the patch has now been generated correctly (`docs-v03-sync-to-code-complete.patch`, both files, applies cleanly); the `qc-record-schema.md`, `orchestration-notes.md`, changelog, and optional validator portions have not yet been generated.
- Required-test policy has not yet been decided.
- Static site and packaged GitHub mirror have not yet been resynced for this patch.

## 5. Proposed Target State

After this version lands, the live documentation and code should tell the same story:

- Recorder helpers exist and should be used.
- Classified validator exit codes are current behavior.
- Required test evidence is machine-readable through `record_test_result.py`.
- Deviation decision links are machine-readable through `record_deviation.py`.
- Ponytail attempt and mode-source evidence are supported.
- Release gate auto-detection is documented accurately.
- The remaining changed-files/diff generator gap is explicit.

The target state should make these things true:

- Agents can follow any live doc and arrive at the same QC run behavior.
- Validator evidence expectations match recorder script fields.
- Changelog and version records explain why the patch exists.

## 6. Changes

### Change 1 - Sync Multi-Agent Modes

**Current behavior.** `docs/multi-agent-modes.md` says decision/gate helpers are required before determinism and implies manual record writing until they exist.

**Problem.** Those helpers now exist. Keeping this text tells the controller to avoid the safer implemented path.

**Change.** Replace future-tense helper-gap language with current helper usage guidance for `record_decision.py`, `record_gate_decision.py`, recorder flags, and classified validator exits.

**Effect once applied.** `phase-controller` and human operators call helper scripts instead of hand-editing `.qc/` state.

**Criticality.** `HIGH` - This file explains the role/tool contract for the system.

**Evidence required.** Stale-language scan shows no live "until helpers exist" language in `multi-agent-modes.md`.

**Affected artifacts.**

- `docs/multi-agent-modes.md`

### Change 2 - Sync Phase Loop

**Current behavior.** `docs/phase-loop.md` still lists helper gaps for `record_test_result.py`, `record_deviation.py`, and old `0`/`1` validator exits.

**Problem.** This is a quick-run operational doc. Stale text here can directly mislead an agent during a phase.

**Change.** Replace "Current helper gaps" with implemented helper status, classified exit-code behavior, and the remaining changed-files/diff generator gap.

**Effect once applied.** Phase runs preserve machine-readable test, deviation, and gate outcome evidence.

**Criticality.** `HIGH` - This doc is likely used during actual phase execution.

**Evidence required.** Stale-language scan and spot-check of helper commands.

**Affected artifacts.**

- `docs/phase-loop.md`

### Change 3 - Sync QC Record Schema

**Current behavior.** `docs/qc-record-schema.md` already documents the recorder flags as current behavior ("Confirmed current behavior"). Its stale content is narrower: it says a skipped required check is bypassed by an accepted-risk decision (L248), and it describes the minimum passing-test rule as a *required* passing test (L248, L451), which is stricter than the current code.

**Problem.** Schema docs define the evidence contract. If they are stale, agents can write invalid or incomplete JSONL.

**Change.** Clarify that accepted-risk is a gate-decision path after validation, not a validator exemption for skipped required tests, and align the minimum-pass wording (L248, L451) with the Change 6 required-test decision. The recorder-flag descriptions are already current and need no change.

**Effect once applied.** `.qc/` record producers and validators share the same contract.

**Criticality.** `CRITICAL` - Schema mismatch can corrupt or weaken QC evidence.

**Evidence required.** Script argument inspection and validator skipped-test logic.

**Affected artifacts.**

- `docs/qc-record-schema.md`

### Change 4 - Sync Orchestration Notes

**Current behavior.** `docs/orchestration-notes.md` still contains stale helper-gap statements, older release-gate wording, and accepted-risk wording that can be read as validator bypass behavior.

**Problem.** This doc describes the whole orchestration run. Stale wording can affect role order, release gate usage, and gate decisions.

**Change.** Update recorder support, release auto-detection, accepted-risk semantics, and required-test guidance.

**Effect once applied.** Agent role orchestration matches the implemented `0.2.0-trial` code.

**Criticality.** `HIGH` - It is a primary controller reference.

**Evidence required.** Live-doc scan shows no stale helper-gap or manual `--release-phase` guidance in live sections.

**Affected artifacts.**

- `docs/orchestration-notes.md`

### Change 5 - Add Changelog Entry

**Current behavior.** The changelog records prior hardening and doc versioning but does not record this V03.1 sync-to-code correction.

**Problem.** Without a changelog entry, future readers cannot tell why the docs changed or what evidence justified the patch.

**Change.** Add `0.2.0-trial docs V03.1 sync-to-code - 2026-06-25`.

**Effect once applied.** Version history shows the docs/code reconciliation.

**Criticality.** `MEDIUM` - Important for traceability.

**Evidence required.** Changelog entry exists and references the sync.

**Affected artifacts.**

- `docs/CHANGELOG.md`

### Change 6 - Optional Validator Required-Test Fix

**Current behavior.** `validate_phase_record.py` counts any passing test for `minimum_required_passes`.

**Problem.** The config name and docs imply a required passing test. Any optional passing test can currently satisfy the minimum pass count if no required passing test exists.

**Change.** Count only latest required test rows for the `minimum_required_passes` threshold.

**Effect once applied.** The strict gate requires phase-required test proof, not just any passing test.

**Criticality.** `HIGH` - This controls whether the gate can false-green on optional tests.

**Evidence required.** New stress case proves optional pass without required pass fails.

**Affected artifacts.**

- `scripts/validate_phase_record.py`
- stress harness / dry-run report if updated

### Change 7 - Mirror And Site Scan

**Current behavior.** Source docs and package mirror can drift; static site may still contain old helper-planned wording.

**Problem.** Published or packaged docs can keep misleading operators even after source docs are fixed.

**Change.** Mirror updated docs to `everythingcodex/plugin/docs/` and scan `everythingcodex/site/index.html` for stale helper-planned language.

**Effect once applied.** Source, package, and site surfaces align.

**Criticality.** `MEDIUM` - Important if the package/site are distributed.

**Evidence required.** Mirror diff and stale-language scan.

**Affected artifacts.**

- `06_agent-work/codex/everythingcodex/plugin/docs/`
- `06_agent-work/codex/everythingcodex/site/index.html`

## 7. Compatibility And Migration

Backward compatibility:

- Existing `.qc/` records remain readable.
- Historical patch notes remain unchanged unless explicitly marked superseded.
- Existing helper scripts are reused.

Expected breakage:

- If the optional validator fix lands, phases with only optional passing tests and no required passing tests should fail strict gate.
- This failure is acceptable because it enforces the intended phase-required proof contract.

Migration path:

1. Apply expanded docs patch.
2. Decide and optionally apply the validator required-test fix.
3. Run stale-language scan.
4. Run compile/tests/stress harness.
5. Mirror docs to package checkout and scan the static site.

Rollback path:

1. Revert the expanded patch files.
2. Revert `scripts/validate_phase_record.py` only if the optional code fix caused unacceptable breakage.
3. Confirm rollback by rerunning the stale-language scan and targeted stress cases against the prior expected behavior.

## 8. Acceptance Criteria

The version is complete when:

1. Existing stress cases still pass.
2. Live docs no longer contain stale helper-gap language.
3. Validator exit codes are documented as current behavior.
4. Accepted-risk wording is corrected across live docs.
5. Required-test behavior is either fixed in code or explicitly documented as current behavior.
6. Changelog records the V03.1 sync.
7. A reviewer/operator can reproduce the evidence.

Exact checks:

```text
rg -n "Until those helpers exist|do not yet support|Current helper gaps|currently returns `0`|Until implemented|until implemented|accepted-risk decision exists|at least one required non-skipped" docs
Expected: no hits in live docs; archive hits only under docs/0.1.0-Trial/ are allowed.
```

```text
python -m compileall scripts
Expected: compile succeeds.
```

```text
0.2.0-trial agent dry-run/stress harness
Expected: all existing stress cases pass; optional-pass-without-required-pass fails if Change 6 lands.
```

## 9. Verification Record

| Check | Evidence | Result | Date |
| --- | --- | --- | --- |
| Desktop patch review | Redacted local Fable5 review record | `pass with incompleteness finding` | `2026-06-25` |
| Expanded plan doc written | `docs/docs-v03-sync-to-code-expanded-patch-plan.md` | `pass` | `2026-06-25` |
| Fable5 authoring audit | Redacted local Fable5 audit record | `pass` | `2026-06-25` |
| Expanded patch applied | `docs/multi-agent-modes.md`; `docs/phase-loop.md`; `docs/qc-record-schema.md`; `docs/orchestration-notes.md`; `scripts/validate_phase_record.py` | `pass` | `2026-06-25` |
| Installer robustness fix | `scripts/install-builder-team-qc.ps1` uses resilient bundle directory copy | `pass` | `2026-06-25` |
| Script compile | `python -m compileall scripts` | `pass` | `2026-06-25` |
| Installer parse check | PowerShell parser over `scripts/install-builder-team-qc.ps1` | `pass` | `2026-06-25` |
| Required-test policy smoke | Optional-only pass failed strict gate with exit `10`; required pass succeeded with exit `0` | `pass` | `2026-06-25` |
| Stale-language scan after patch | Source docs, package mirror docs, and `site/index.html` returned no live-doc hits | `pass` | `2026-06-25` |
| Stress harness after patch | Redacted local stress-harness run | `10/10 pass` | `2026-06-25` |
| Per-file doc header bump | `multi-agent-modes.md`, `phase-loop.md`, `qc-record-schema.md`, `orchestration-notes.md` | `V03.1` | `2026-06-25` |
| Recovery pack | `docs/0.2.0-trial/backups/DOC-V03-SYNC-TO-CODE-EXPANDED-20260625/` | `created` | `2026-06-25` |

## 10. Release / Adoption Plan

Priority order:

1. Decide required-test policy because it determines whether this is docs-only or docs-plus-code.
2. Patch live docs and changelog.
3. Apply optional validator fix if approved.
4. Verify and mirror package/site docs.

Rollout:

1. Prepare expanded patch.
2. Apply locally.
3. Run stale-language scan and compile checks.
4. Run agent stress harness.
5. Mirror package docs and scan site.
6. Record final verification in changelog or fable5 run.

Communication needed:

- `phase-controller` needs to know helpers are implemented and should be called.
- `test-agent` needs to record `--required` and `--attempt`.
- `compliance-agent` needs to record `--issue-id` and `--decision-id`.
- Human operators need to know accepted-risk is a gate decision path, not a validator exemption.

## 11. Risks And Open Questions

Risks:

- Applying only the Desktop patch leaves conflicting docs. Mitigation: use the expanded patch.
- A code fix for required tests could break existing synthetic phases that did not mark any tests as required. Mitigation: update harness and docs together.
- Package mirror or static site can stay stale. Mitigation: include mirror/site scan in acceptance criteria.

Open questions:

- Should `minimum_required_passes` count only required tests? Recommendation: yes.
- Should historical `docs/0.1.0-Trial/` files get superseded notes? Recommendation: only if readers are confused by archive hits.
- Should a dedicated changed-files/diff generator script be added next? Recommendation: yes, but it is outside this patch unless explicitly scoped.

Decision needed before landing:

- Approve Option A validator fix or choose Option B doc-only current-code sync.

## 12. Version Ledger

| Date | Version | Change ID | Status | Notes |
| --- | --- | --- | --- | --- |
| `2026-06-25` | `0.2.0-trial docs V03.1 executed` | `DOC-V03-SYNC-TO-CODE-EXPANDED` | `Executed` | Applied expanded docs patch, Option A validator fix, installer robustness fix, package mirror sync, static site sync, stale scan, and stress harness verification. |

## 13. Changelog Entry

```markdown
## 0.2.0-trial docs V03.1 sync-to-code - 2026-06-25

### Added
- Versioned sync-to-code record for the expanded V03 docs patch.

### Changed
- Reconciled multi-agent modes, phase loop, QC record schema, and orchestration notes with implemented recorder flags.
- Documented classified validator exit codes as current behavior.
- Clarified accepted_with_risk as a final gate decision path, not a validator exemption for skipped required tests.

### Fixed
- Removed stale helper-gap language for record_decision.py, record_gate_decision.py, record_test_result.py, record_deviation.py, and record_ponytail_check.py.
- Documented the remaining changed-files/diff generator gap.

### Deprecated
- Manual decision-log and phase-board editing guidance for implemented helper paths.

### Removed
- No runtime behavior removed unless the optional required-test validator fix is approved.

### Migration Notes
- Agents should call recorder helpers for machine-readable evidence.
- If the validator fix lands, required tests must be marked with --required and at least one required test must pass.
```

## 14. Final Decision

| Field | Value |
| --- | --- |
| Decision | `Landed with Option A validator required-test fix` |
| Decider | `Randy / Codex phase-controller` |
| Decision date | `2026-06-25` |
| Conditions | `Option A selected; expanded patch applied; stale scan and stress harness passed` |
| Supersedes | `redacted local Desktop patch as final patch candidate` |
| Superseded by | `none` |

Decision note:

The Desktop patch was useful seed material but incomplete. The executed patch expands the live documentation sync, applies the validator required-test fix so the strict gate enforces required phase proof, and updates the package mirror/static site surfaces.

## Appendix B - Corrections Applied 2026-06-25

An external review against the implemented `0.2.0-trial` scripts corrected the statements below. Each correction is evidence-backed.

| Location | Was | Corrected to | Evidence |
| --- | --- | --- | --- |
| §4 and Change 3 | `qc-record-schema.md` "still says some recorder flags do not exist" | Its recorder-flag lines already read "Confirmed current behavior"; the only stale content is the accepted-risk-skipped-test clause (L248) and the required-vs-any minimum-pass wording (L248, L451) | `qc-record-schema.md` L33/368/431/443 read "Confirmed current behavior"; no "does not yet support" lines exist in that file |
| §4 Known gaps | Patch "has not yet been generated or applied" | The `multi-agent-modes.md` + `phase-loop.md` portion is now generated correctly as `docs-v03-sync-to-code-complete.patch` (both files, `git apply --check` clean); the remaining portions are still pending | Patch regenerated and apply-checked against fresh copies of both files |

Findings from the original plan that were re-verified and retained as correct:

- The original Desktop patch did modify only `docs/multi-agent-modes.md`; its `phase-loop.md` hunk was lost to a patch-write error. §4 was right to flag this.
- `orchestration-notes.md` L272 (`record_test_result.py`) and L325 (`record_deviation.py`) helper-gap statements are genuinely stale; the flags exist.
- `orchestration-notes.md` L363 manual `--release-phase` guidance is stale: the validator auto-detects release phases via `release_phase_patterns` (`builder_team_qc_lib.py` L430-449).
- Both `orchestration-notes.md` L285 and `qc-record-schema.md` L248 carry the accepted-risk-exempts-skipped-required-test over-claim, which the validator's test logic does not implement.
- The validator counts any passing test row for `minimum_required_passes`, so the required-vs-any fork (Change 6) is real and must be decided before the `qc-record-schema.md`/`orchestration-notes.md` minimum-pass wording can be finalized.

## Appendix A - Included Fable5 Audit Report

Source:

```text
Internal audit source redacted. Public record:
https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/plugin/docs/docs-v03-sync-to-code-expanded-version-record-CORRECTED.md
```

Included audit:

```markdown
# Fable5 Audit Report

Run id: `<redacted-local-run-id>`

## Verdict

Pass. A new detailed patch-plan document was created.

## Confirmed

- The prior fable5 review report was available and read.
- The Desktop patch was available and read.
- Both newly attached rationale files were available and read.
- The target doc did not already exist before creation.
- The new document was written to `docs/docs-v03-sync-to-code-expanded-patch-plan.md`.

## Inferred

- The user wants a planning/reference document before applying a new patch, not immediate implementation, because the request said "write a new doc" and referenced the review report.

## Error-Catch Pass

Potential error checked: writing the patch itself instead of a documentation plan. I kept the change to one new doc plus fable5 run records.

Potential remaining issue: if the user wanted the actual expanded `.patch` file rather than the plan document, that should be the next artifact.
```
