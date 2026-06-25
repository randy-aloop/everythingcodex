# Alpha Transition Phase Plan

Version: V01
Updated: 2026-06-24
Target Release: `0.1.0-alpha.1`
Current Honest Version: `0.1.0-planning`

Public archive note: this plan is retained as historical planning context only. It was superseded by the prototype/trial path; the current public bump target is `0.2.1-trial`, not `0.1.0-alpha.1`.

This plan turns the review findings into a phase-by-phase path for moving Builder Team QC from planning/prototype status into an honest alpha.

## Version Decision

Do not label the project beta yet.

Use this meaning:

```text
planning = design exists, but code/docs do not fully align
alpha = careful early user can run one build end-to-end with known rough edges
beta = multiple real builds prove repeatability
```

Current call:

```text
0.1.0-planning
```

Alpha target:

```text
0.1.0-alpha.1
```

Alpha is allowed only after one real local build trial completes through install, phase start, builder/Ponytail/test/review/compliance/seam, strict gate, and final phase-board transition.

## Alpha Scope

Alpha should stay single-run multiagent.

It does not need true parallel Runtime V02 yet. The alpha goal is to make Runtime V01 honest and reproducible:

```text
one Codex controller
sequential role passes
durable .qc records
strict validator enforcing the claims the docs make
one successful local trial
```

## Phase A0 - Freeze The Alpha Contract

Goal: define exactly what alpha means before changing scripts.

Inputs:

- Current docs.
- Current scripts.
- Review findings.
- Existing `.qc` schema intent.

Actions:

1. Keep package/repo version at `0.1.0-planning`.
2. Create an alpha checklist.
3. Mark all unsupported deterministic claims as either `implemented`, `manual fallback`, or `planned`.
4. Decide whether builder scope audit will be implemented for alpha or deferred.

Deliverables:

- Alpha readiness checklist.
- List of claims that must be made true before alpha.

Gate:

- No alpha label until every public claim is either implemented or clearly documented as manual/planned.

## Phase A1 - Documentation Truth Alignment

Goal: remove or soften claims that current scripts do not enforce.

Review findings addressed:

- Dry-run report overstates reproducible repo capability.
- Docs mention builder scope proof that is not shipped.
- README path mismatch.
- Docs claim stricter validator behavior than code provides.

Actions:

1. Fix README path from `.qc/phases/<phase-id>/` to `.qc/phase-runs/<phase-id>/`.
2. Search docs for `audit_builder_scope.py` and `--require-builder-scope`.
3. If scope audit is not implemented in Phase A2, relabel those references as planned/manual.
4. Search docs for claims that phase-board final completion is automatically recorded.
5. Relabel final phase-board update as manual until `record_gate_decision.py` exists.
6. Update dry-run/test report language so sandbox/manual proof is not presented as packaged repo proof.

Deliverables:

- Corrected README path.
- Corrected builder-scope docs.
- Corrected dry-run report claims.

Gate:

- A new user does not encounter a documented command or path that does not exist.

## Phase A2 - Builder Scope Audit Decision

Goal: make builder scope control honest.

Problem:

Docs reference `audit_builder_scope.py` and `validate_phase_record.py --require-builder-scope`, but the reviewed script set does not include that capability.

Option 1: Implement for alpha.

Minimum script behavior:

```text
audit_builder_scope.py
  --root <target-project>
  --phase-id <phase-id>
  --allowed-files <file or comma-list>
  --changed-files .qc/phase-runs/<phase-id>/changed-files.json
```

Required checks:

- Every changed file is project-relative.
- Every changed file is allowed by phase scope or explicitly recorded as deviation.
- Deleted/renamed files are represented.
- Out-of-scope changes produce a blocker issue.

Validator integration:

```text
validate_phase_record.py --require-builder-scope
```

Strict gate behavior:

- Missing scope audit blocks when required.
- Failed scope audit blocks.
- Out-of-scope files require deviation plus accepted-risk decision.

Option 2: Defer for alpha.

Documentation requirement:

- Say builder scope audit is manual in alpha.
- Remove command examples that imply shipped automation.
- Keep `audit_builder_scope.py` in the Runtime V02/backlog section.

Recommendation:

Implement the minimal scope audit for alpha if time allows. It is central to phase discipline.

Gate:

- Either the command works, or no alpha docs claim it works.

## Phase A3 - Decision And Gate Recording Scripts

Goal: remove manual ambiguity around accepted risk and final phase state.

Scripts:

```text
record_decision.py
record_gate_decision.py
```

`record_decision.py` must:

- Append to `.qc/decision-log.jsonl`.
- Require or generate `decision_id`.
- Require or generate UTC `timestamp`.
- Capture human approver, risk, impact, owner, deadline, rollback, and follow-up.
- Print machine-readable output containing `decision_id`.

`record_gate_decision.py` must:

- Update `.qc/phase-board.json`.
- Write or update `.qc/phase-runs/<phase-id>/gate-summary.md`.
- Record final decision: `pass`, `block`, or `accepted_with_risk`.
- Require accepted-risk decision id when final decision is `accepted_with_risk`.
- Ensure phase board does not remain `open` with `latest_gate_decision=pending`.

Gate:

- Accepted risk cannot be represented by a boolean alone.
- A phase cannot be reported complete while phase-board still says pending/open.

## Phase A4 - Strict Validator Hardening

Goal: make `validate_phase_record.py` enforce the core promises in docs.

Required enforcement:

- Parse role verdicts exactly.
- Fail `Verdict: revise`.
- Fail `Verdict: block`.
- Fail missing or duplicate role verdicts.
- Allow `release-gate.md` `Verdict: not_applicable` only when `release_required=false` and rationale exists.
- Enforce at least one required non-skipped passing test.
- Fail skipped required tests unless accepted-risk decision exists.
- Fail accepted-risk claims without matching `.qc/decision-log.jsonl`.
- Fail open blocker issues in `.qc/issue-register.jsonl`.
- Fail unaccepted blocker deviations.
- Preserve non-strict validation as warning-friendly.

Target exit codes:

| Exit code | Meaning |
| --- | --- |
| `0` | Pass or warnings-only non-strict validation. |
| `10` | Strict gate failure. |
| `20` | Schema/config/invocation error. |
| `30` | Safety blocker. |

Gate:

- Validator behavior matches `qc-record-schema.md` and `phase-by-phase-run-plan.md`.

## Phase A5 - Schema And Template Synchronization

Goal: make seeded files match the schema the docs require.

Current mismatch:

- Docs require rich `phase-board.json`, `qc-config.json`, test fields, Ponytail fields, decision ids, final gate fields.
- Current templates/start phase create smaller records.
- Current start phase does not create `changed-files.json`, `implementation-diff.patch`, or `gate-summary.md`.

Actions:

1. Update `assets/qc-templates/phase-board.json`.
2. Update `assets/qc-templates/qc-config.json`.
3. Update `start_phase()` to seed required phase-run support files or document exact manual fallback.
4. Add schema validation for required fields.
5. Ensure generated phase-board includes:
   - `schema_version`
   - `current_phase_id`
   - `current_phase_status`
   - `next_phase_id`
   - `latest_gate_decision`
   - `latest_gate_at`
   - `release_required`
   - `release_not_applicable_rationale`
   - `revise_attempts`
   - `max_revise_attempts`
   - `required_evidence`
   - `blocking_issues`
   - `accepted_risk_decision_id`
   - `updated_at`

Gate:

- Fresh `init_qc.py` and `start_phase.py` output does not contradict the schema docs.

## Phase A6 - Safety Scanner Classification

Goal: stop false positives from blocking normal docs while preserving blocker detection.

Problem:

Current safety scan can overblock:

- Documentation policy text.
- README links.
- GitHub attribution URLs.
- Scanner regex definitions inside `builder_team_qc_lib.py`.

Required fix:

Add severity classification:

```text
blocker = active risky behavior or likely secret
warning = risky term needing review
info = policy/reference/scanner self-definition
```

Gate behavior:

- Strict gate fails on `blocker`.
- Strict gate warns on `warning`.
- Strict gate records but does not block on `info`.

Examples:

| Finding | Severity |
| --- | --- |
| Actual API key assignment | blocker |
| `client_secret = ...` | blocker |
| `RemoteA2aAgent(...)` in source code | blocker |
| Docs saying "Remote A2A is not allowed" | info |
| GitHub attribution link | info |
| Scanner regex pattern inside scanner implementation | info |

Gate:

- Normal docs and scanner self-definitions do not block alpha trial.
- Actual secrets and active remote/tooling config still block.

## Phase A7 - Controller Usability

Goal: reduce manual orchestration burden for alpha users.

Current usability risk:

There is no single command that runs one phase controller flow. Codex must manually coordinate roles and scripts.

Alpha minimum:

- Keep Codex prompt-driven orchestration if needed.
- Provide one canonical "run this phase" prompt.
- Provide one command checklist.
- Provide exact manual fallback steps.

Better alpha target:

```text
run_phase.py
  --root <target-project>
  --phase-id <phase-id>
  --title "<phase title>"
  --build-plan "<plan path>"
  --next-phase-id <next-phase-id>
  --release-required auto|true|false
```

If `run_phase.py` is too much for alpha, defer it clearly to post-alpha.

Gate:

- A careful user can follow one README path without guessing which script to call next.

## Phase A8 - Real Local Build Trial

Goal: prove alpha usability on a real target, not only docs or dry-run claims.

Use a tiny local project.

Example:

```text
toy-alpha-build/
  README.md
  src/math_utils.py
  tests/test_math_utils.py
```

Trial phases:

```text
phase-000: initialize project README
phase-001: add one Python function
phase-002: add one test
phase-003: run strict gate and close phase-board
```

Required proof:

- Installer works from a clean local path.
- `.qc/` initializes.
- Phase run starts.
- Builder changes are scoped.
- Ponytail record is written.
- Test result is written.
- Reviewer/compliance/seam reports are written.
- Strict gate blocks when evidence is missing.
- Strict gate passes after required evidence exists.
- Final phase-board transition is recorded.
- Safety scan does not overblock harmless docs.

Gate:

- The trial produces a reusable `.qc/` evidence folder.
- The trial can be repeated from README instructions.

## Phase A9 - Alpha Cut

Goal: tag or label `0.1.0-alpha.1` honestly.

Before alpha:

- All alpha gates above pass.
- Changelog explains what is implemented and what remains manual.
- README says this is alpha, not beta.
- Known limitations are explicit.

Alpha release notes should include:

- Runtime is still single-run multiagent.
- Parallel Runtime V02 is planned, not shipped.
- Some manual Codex coordination may remain.
- `.qc` records are the source of truth.
- Strict gate is enforced by scripts for core alpha promises.

Gate:

- A careful early user can install, run a toy phase, inspect `.qc`, and understand failures without reading internal design docs.

## Beta Bar

Do not call this beta until:

- At least one non-toy real project build succeeds.
- At least two independent phase runs complete.
- Install and run instructions work from a clean checkout.
- Validator and safety scanner have low false-positive rates.
- Final phase-board transitions are deterministic.
- Known manual steps are either automated or clearly acceptable for beta.

## Summary Plan

```text
A0 freeze alpha contract
A1 align docs with shipped behavior
A2 implement or defer builder scope audit
A3 add decision and gate recording scripts
A4 harden strict validator
A5 sync schema and templates
A6 classify safety scanner findings
A7 improve controller usability
A8 run real local build trial
A9 cut 0.1.0-alpha.1
```

The core rule:

```text
Do not move to alpha because the design is strong.
Move to alpha when the shipped repo can prove one real phase loop end-to-end.
```
