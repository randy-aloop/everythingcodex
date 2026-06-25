# Builder Team QC Docs Changelog

Current docs version: `0.2.1-trial`
Updated: 2026-06-25

## 0.2.1-trial installer - 2026-06-25

Built the project-local installer path for `0.2.1-trial`:

- Bumped `.codex-plugin/plugin.json` to `0.2.1-trial`.
- Updated the canonical installer default expected version to `0.2.1-trial`.
- Added `scripts/install-builder-team-qc-0.2.1-trial.ps1` as the current upgrade wrapper that preserves existing `.qc/` records by default.
- Added installer checks for the V03.1 sync-to-code doc headers, executed patch record, and recovery-pack manifest.
- Updated `docs/installation-and-first-run-guide.md` to V04 with the `0.2.1-trial` install/upgrade path.

## 0.2.0-trial docs V03.1 sync-to-code - 2026-06-25

Applied the expanded sync-to-code patch:

- Reconciled `multi-agent-modes.md`, `phase-loop.md`, `qc-record-schema.md`, and `orchestration-notes.md` with implemented recorder flags.
- Replaced stale manual helper-gap language with the current script contracts.
- Documented classified validator exit codes as current behavior.
- Clarified `accepted_with_risk` as a final gate decision path, not a validator exemption for skipped required tests.
- Documented the remaining `changed-files.json` and `implementation-diff.patch` generator gap.
- Hardened `validate_phase_record.py` so `minimum_required_passes` counts required passing tests, not any passing test.
- Bumped touched live doc headers to `V03.1`.
- Added recovery pack `docs/0.2.0-trial/backups/DOC-V03-SYNC-TO-CODE-EXPANDED-20260625/` with current patched files and recoverable `everythingcodex` Git baselines.

## 0.2.0-trial agent dry-run stress - 2026-06-24

Ran the fable5 agent dry-run and stress harness for `0.2.0-trial`:

- Created a redacted local fable5 stress run.
- Ran a synthetic local install-and-phase sandbox at a redacted local target.
- Passed 10 of 10 stress cases with 0 failures.
- Proved `record_decision.py` accepted-risk decision-log evidence.
- Proved `record_gate_decision.py` final phase-board transition and `gate-summary.md` evidence.
- Proved strict role verdict blocking, skipped required-test blocking, Ponytail stale-diff blocking, builder-scope overbuild blocking, open issue-register blocker blocking, and release-phase auto-detection.
- Updated `docs/agent-dry-run-and-test-report.md` to V02 with the `0.2.0-trial` addendum.

## 0.2.0-trial installer - 2026-06-24

Built the project-local installer path for `0.2.0-trial`:

- Bumped `.codex-plugin/plugin.json` to `0.2.0-trial`.
- Hardened `scripts/install-builder-team-qc.ps1` with expected-version checks, trial helper coverage checks, prototype-upgrade mode, installed-copy validation, and optional `install-report.json` output.
- Added `scripts/install-builder-team-qc-0.2.0-trial.ps1` as the prototype-to-trial upgrade wrapper that preserves existing `.qc/` records by default.
- Updated `docs/installation-and-first-run-guide.md` to V03 with upgrade and fresh-install commands.
- Updated `docs/installation-dry-run-and-stress-test-report.md` to V02 with the trial installer addendum and resolved-helper status.

## 0.2.0-trial doc versioning pass - 2026-06-24

Versioned the documentation touched by the hardening implementation:

- `docs/0.2.0-trial/hardening-implementation-report.md` is now `0.2.0-trial.1`.
- `docs/0.1.0-Trial/patch-01-strict-gate-enforcement.md` is now `PATCH-01.V02`.
- `docs/0.1.0-Trial/patch-02-phase-board-transition.md` is now `PATCH-02.V02`.
- `docs/multi-agent-modes.md` is now V03.
- `docs/orchestration-notes.md` is now V03.
- `docs/phase-loop.md` is now V03.
- `docs/phase-by-phase-run-plan.md` is now V05.
- `docs/installation-and-first-run-guide.md` is now V02.
- `docs/single-run-vs-parallel-runtime.md` is now V03.

## 0.2.0-trial hardening implementation - 2026-06-24

Implemented the strict-gate, phase-board, and Ponytail evidence-binding upgrades:

- Hardened `scripts/validate_phase_record.py` for anchored role verdict parsing, issue-register blockers, skipped required tests, release auto-detection, Ponytail diff binding, decision-log proof, and classified exit codes.
- Added `scripts/record_decision.py`.
- Added `scripts/record_gate_decision.py`.
- Updated `scripts/start_phase.py` to refuse a new phase while the current phase board is non-terminal unless `--force` is used.
- Extended `scripts/record_ponytail_check.py` with attempt, mode source, checklist version, structured subcheck statuses, upstream-hook proof fields, changed-files hash, implementation-diff hash, and builder-scope audit hash.
- Extended `scripts/record_test_result.py` and `scripts/record_deviation.py` with attempt/required and decision/issue references.
- Updated `.qc` templates, phase-controller skill, and Ponytail adapter skill for the new enforced flow.
- Updated `docs/qc-record-schema.md` to V03 for implemented exit codes, board fields, decision fields, and Ponytail hash-bound evidence.
- Added `docs/0.2.0-trial/hardening-implementation-report.md`.

## 0.1.0-prototype audit patch - 2026-06-24

Patched the versioned prototype archive after a redacted local fable5 audit:

- Updated `docs/0.1.0-prototype/01-chronological-thread-record.md` with post-V03 evidence coverage for V05 through V09.
- Replaced a generic local storage label with public-safe wording.
- Updated `docs/0.1.0-prototype/02-work-process-and-decision-logic.md` to reflect that builder-scope audit and safety severity classification now exist but still need real-trial validation.
- Updated `docs/0.1.0-prototype/04-code-build-artifact-map.md` so `audit_builder_scope.py` is listed as an existing core script and the current run plan is V04.
- Updated `docs/0.1.0-prototype/06-handoff-to-0.2.0-trial.md` so trial work validates and hardens existing builder-scope and safety-scan classification behavior instead of treating them as absent.

## 0.1.0-prototype - 2026-06-24

Added versioned prototype archive:

- `docs/0.1.0-prototype/README.md`
- `docs/0.1.0-prototype/01-chronological-thread-record.md`
- `docs/0.1.0-prototype/02-work-process-and-decision-logic.md`
- `docs/0.1.0-prototype/03-prompt-processing-record.md`
- `docs/0.1.0-prototype/04-code-build-artifact-map.md`
- `docs/0.1.0-prototype/05-version-rationale.md`
- `docs/0.1.0-prototype/06-handoff-to-0.2.0-trial.md`

Updates included:

- Preserved the prototype conversation and build history in chronological form.
- Captured structured input/output, work process, prompt processing, artifact map, and version rationale.
- Added a future-reference handoff into `0.2.0-trial`.

## V09 - 2026-06-23

Added agent evidence report:

- `docs/agent-dry-run-and-test-report.md`

Updates included:

- Compiled full-loop agent dry-run, builder-agent stress test, builder scope audit proof, and Ponytail gate proof.
- Documented what each role surface proved.
- Added negative and positive Ponytail gate controls.
- Clarified stop/debug/log/correct behavior and current script-level gaps.

## V08 - 2026-06-23

Added installation progress evidence report:

- `docs/installation-dry-run-and-stress-test-report.md`

Updates included:

- Compiled installation dry-run and stress-test evidence from sandbox runs.
- Summarized direct-run installation status, plugin registry gap, dry-run results, full-loop stress, builder-agent stress, builder scope audit proof, and Ponytail enforcement proof.
- Listed intentional failures, corrections, remaining gaps, and current verdicts.

## V07 - 2026-06-23

Added installation/setup documentation:

- `docs/installation-and-first-run-guide.md`

Updates included:

- Compiled direct-run installation and first-run steps from `phase-by-phase-run-plan.md`.
- Clarified the difference between confirmed direct local script use and unconfirmed Codex plugin registry installation.
- Added sandbox-first setup, `.qc` initialization, phase start, builder scope audit, Ponytail, evidence fan-out, validation, revise loop, accepted-risk, phase-board update, summary, and handoff steps.
- Documented current helper gaps that still require manual controller records.

## V06 - 2026-06-23

Added user-facing documentation:

- `docs/build-plan-authoring-guide.md`

Updates included:

- Created a full authoring guide for writing project, application, plugin, skill, MCP, and engineering-tool build plans for `builder-team-qc`.
- Documented the four enforceable surfaces: build, behavior, evidence, and stop.
- Added global build, safety, dependency, and evidence policy sections.
- Added a full per-phase contract template.
- Added phase-type guidance, stop-and-ask policy, stop report template, and preflight checklist.
- Added application, engineering-tool, and plugin/skill/MCP build-plan add-ons.

## V05 - 2026-06-23

Updated plugin files:

- `scripts/builder_team_qc_lib.py`
- `scripts/audit_builder_scope.py`
- `scripts/validate_phase_record.py`
- `skills/builder-agent/SKILL.md`
- `skills/phase-controller/SKILL.md`
- `docs/builder-scope-audit.md`
- `assets/qc-templates/README.md`

Updates included:

- Added first-class phase-relative builder scope auditing.
- Added pre-builder baseline evidence at `.qc/phase-runs/<phase-id>/evidence/builder-scope-baseline.json`.
- Added post-builder audit evidence at `.qc/phase-runs/<phase-id>/evidence/builder-scope-audit.json`.
- Added `.qc/builder-scope-audits.jsonl` audit history.
- Added `validate_phase_record.py --require-builder-scope` so strict gates can require a passing builder scope audit.
- Updated builder-agent and phase-controller contracts to snapshot before edits, audit after edits, and stop on unexpected scope drift.

## V04 - 2026-06-23

Updated documentation file:

- `phase-by-phase-run-plan.md`

Updates included:

- Bumped `phase-by-phase-run-plan.md` from V03 to V04.
- Logged the `phase-002` Phase 6 safety scan blocker caused by context-blind banned-pattern matching.
- Added the V04 context-aware scanner solution: findings carry `severity` and `reason`.
- Defined safety scan gate behavior: strict and in-progress validation fail only on `severity=blocker` findings.
- Documented non-blocking `warning` and `info` safety findings for policy-deny docs, reference URLs, and scanner self-definitions.
- Added the controller rule to stop, report, get approval, then rerun the full proof set after safety-policy changes.

## V03 - 2026-06-23

Updated documentation file:

- `phase-by-phase-run-plan.md`

Updates included:

- Bumped `phase-by-phase-run-plan.md` from V02 to V03.
- Fixed Phase 0 sequencing so pre-build checks do not write durable `.qc/` records before `.qc/` and phase-run files exist.
- Aligned the One-Page Run Order with the body phase numbers.
- Clarified valid `release-gate.md` `Verdict: not_applicable` handling when `release_required=false`.
- Completed the phase-board `required_evidence` example with test report, release gate, and gate summary evidence.
- Relabeled helper output trees as target layouts and marked manual files.
- Added lessons intake so `lessons-learned.jsonl` feeds later phases.
- Added `record_decision.py` decision-id and timestamp target behavior.
- Clarified non-strict validator warning/error exit behavior.
- Defined `release_not_applicable_rationale` behavior when `release_required=true`.

## V02 - 2026-06-23

Versioned documentation set:

- `multi-agent-modes.md`
- `orchestration-diagram.md`
- `orchestration-notes.md`
- `phase-by-phase-run-plan.md`
- `phase-loop.md`
- `production-debug-gate.md`
- `qc-record-schema.md`
- `single-run-vs-parallel-runtime.md`

Updates included:

- Added stricter `.qc/` record contracts.
- Added phase-board, issue-register, changed-file, diff, gate-summary, and lessons evidence expectations.
- Clarified current helper gaps versus target helper contracts.
- Tightened strict-gate, accepted-risk, release-gate, and revise-loop rules.
- Updated orchestration diagrams and quick-run references to match the V02 control model.
- Added the single-run versus parallel-runtime explanation, including ADK verification notes and the Runtime V03 graph/dynamic workflow nuance.
