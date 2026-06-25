# Patch Rationale 01 — Strict-Gate Enforcement Hardening

| Field | Value |
| --- | --- |
| Patch ID | `PATCH-01` |
| Document version | `PATCH-01.V02` |
| Target version | `0.1.0-prototype` → `0.2.0-trial` |
| Supersedes | `PATCH-01.V01` proposed rationale |
| Scope | `scripts/builder_team_qc_lib.py`, `scripts/validate_phase_record.py`, two new recorder scripts, `phase-board.json` schema |
| Status | Implemented in `0.2.0-trial` hardening pass on 2026-06-24 |
| Evidence basis | Live run of the V01 pipeline on a clean target project (init → start → evidence → strict gate), plus a mutation harness (cases `N1`–`N5`, `G1`–`G4`) and a full `grep` of `scripts/*.py`; implementation verified by `hardening-smoke-20260624` |
| Companion | `PATCH-02` (phase-board transition) implements the board half of Change 5 in depth |

---

## 1. Summary

The Builder Team QC skeleton is sound. The coded parts are clean, single-purpose, and deterministic, and the safety scanner and minimal-code (Ponytail) discipline are implemented for real. The problem this patch addresses is narrower and more dangerous than "missing features": **the V01 strict gate can return a passing result in five situations where the V02 documentation says it must not.** Every one of these is a *false negative* — the gate says "green" when the recorded evidence says "stop." For a system whose entire value proposition is *"a green gate means the build is trustworthy,"* a false green is the worst possible failure mode, because it is indistinguishable from a real pass to anyone reading the result.

This patch makes the word "pass" mean what the docs already say it means. It does not invent new behaviour; it closes the gap between the documented contract (V02) and the enforced contract (V01), which currently sits at roughly 60% coverage.

## 2. Why this is a patch and not a feature request

The repository already *states* the target contract. `multi-agent-modes.md` and `orchestration-diagram.md` (both V02) assert that non-pass role verdicts, open blocker issues, all-skipped required tests, and incomplete release gates must block, and that `accepted_with_risk` must be backed by a decision-log entry the controller may not self-approve. The README's "What Is Enforced By Code?" table and "Current Implementation Note" half-acknowledge that some of this is still aspirational.

So this is not a change of intent. It is **completing the intent the project has already committed to in writing.** Until it lands, the diagrams and the agentic-mode docs describe a stricter machine than the one that runs, and a reader comparing the docs to the code will find the docs over-promise. That divergence is itself a defect: it erodes trust in the one artifact (the gate result) the system exists to produce.

The unifying defect across all five items: **the validator only checks for the absence of `pending`, never for the presence of an explicit stop signal, and it never reads three of the `.qc` files it scaffolds (`issue-register.jsonl`, `decision-log.jsonl`) or the policy it ships (`qc-config.json`).** The data is being written and then ignored.

## 3. The five changes

For each: what the code does today (with the evidence that proves it), why that is wrong, how critical it is and the concrete failure mode, and what changes once the patch is applied.

### Change 1 — Scan required reports for `revise` / `block`, not just `pending`

**Current behaviour.** Gate completeness for role reports is decided by `file_has_pending()`, which lower-cases the file and returns true only if it contains the literal substrings `verdict: pending` or `gate decision: pending`. A report whose verdict line reads `Verdict: block` or `Verdict: revise` contains neither substring, so it is treated as a completed, acceptable report.

**Evidence.** Harness case `G1`: starting from a fully green phase, the reviewer report's verdict was changed to `Verdict: block`; the strict gate returned **exit 0 (pass)** before this patch. A pre-patch `grep` for `Verdict: revise` and `Verdict: block` across `scripts/*.py` matched **zero** files.

**Why it is wrong.** Role verdicts are the central output of every reviewing agent. If a reviewer or compliance agent can write the strongest possible objection — `block` — and the gate still passes, then role verdicts are decorative. This directly contradicts the V02 docs, which say `Verdict: revise` and `Verdict: block` in required reports must fail the gate.

**Criticality: CRITICAL.** This is a correctness hole at the dead centre of the system, it is trivially reachable through normal use (any agent that follows the template and writes an honest negative verdict triggers it), and it produces a false green. It is the single highest-severity item in this patch.

**Effect once applied.** The role-report check classifies the verdict explicitly. Proposed logic sketch:

```python
def read_verdict(path: Path) -> str:
    # returns one of: pass | revise | block | pending | missing | unknown
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    for v in ("block", "revise", "pending"):      # check stop-signals first
        if f"verdict: {v}" in text or f"gate decision: {v}" in text:
            return v
    if "verdict: pass" in text or "gate decision: pass" in text:
        return "pass"
    return "unknown"                                # absent/garbled verdict also fails strict
```

Under `--strict-gate`, any required report returning `revise`, `block`, `pending`, `missing`, or `unknown` fails the gate. (A `block` paired with a matching `accepted_with_risk` decision is handled in Change 5; until that lands, `block`/`revise` simply fail, which is the safe default.) `release-gate.md` keeps its existing exemption outside `--release-phase`.

### Change 2 — Read `issue-register.jsonl` for open blockers

**Current behaviour.** `ensure_qc()` creates an empty `issue-register.jsonl`, and the compliance role is documented to write blocker issues into it. The validator never opens the file.

**Evidence.** Harness case `G2`: appending `{"status":"blocker", ...}` for the phase left the strict gate at **exit 0 (pass)**. `grep` shows `issue-register` appears in exactly one Python file — the `JSONL_FILES` list in `builder_team_qc_lib.py` that *creates* it — and in no read path.

**Why it is wrong.** The `orchestration-diagram.md` "Evidence Responsibility View" draws an explicit `ISSUES → STRICT` edge. The compliance agent's whole mechanism for raising a hard stop is to log a blocker issue. Because nothing reads the register, that entire channel is inert: a compliance agent can correctly identify a blocker, record it as designed, and the gate passes anyway.

**Criticality: HIGH.** It silently neutralises the compliance agent's strongest action and, like Change 1, yields a false green. Lower than Change 1 only because it requires the compliance path to be in use.

**Effect once applied.** The validator reads `issue-register.jsonl`, filters to the current phase (plus any global/unscoped blockers), and fails the gate on any entry with `status` in `{open, blocker}` that lacks a `resolved`/`fixed` transition. This requires fixing a small status vocabulary (`open` | `fixed` | `blocker`) and documenting it in `qc-record-schema.md`.

### Change 3 — Fail all-`skipped` required tests

**Current behaviour.** The test check is two questions: do any test rows exist for the phase (under `--strict-gate`, none is an error), and did any row report `status: fail`. A set of rows that are all `skipped` answers "yes, tests exist" and "no failures," so it passes.

**Evidence.** Harness case `G3`: replacing the passing test with a single `status: skipped` row left the strict gate at **exit 0 (pass)**.

**Why it is wrong.** The README's dry-run section claims "Required test evidence cannot be skipped," and the V02 docs say all-skipped required tests must fail unless a matching accepted-risk decision exists. Today, "we ran tests" is satisfiable by skipping every test.

**Criticality: MEDIUM.** Narrower than Changes 1–2 (it needs deliberate or accidental all-skip), but it defeats an explicitly advertised guarantee and is cheap to close.

**Effect once applied.** Under `--strict-gate`, require at least one recorded test with `status: pass` for the phase; a row set that is exclusively `skipped` (and/or `fail`) fails. This is the simplest deterministic rule and does not depend on the not-yet-implemented per-test `required` field. If the `required` field is added later, the rule tightens to "every required test is `pass`."

### Change 4 — Auto-detect release phases from `qc-config.json`

**Current behaviour.** Release-gate completeness is enforced only when the operator passes `--release-phase`. The shipped `qc-config.json` carries `release_phase_patterns` (`release`, `deploy`, `runtime`, `docker`, `production`), but that field is never read.

**Evidence.** Harness case `G4`: a phase whose record was titled "deploy docker runtime release," validated **without** `--release-phase`, passed with `release-gate.md` still `not_applicable`. `grep` shows `release_phase_patterns` (and the sibling `quick_test_commands` / `docker_smoke_commands`) appear in **zero** Python files.

**Why it is wrong.** Release-touching phases — runtime, Docker, deploy, production debug — are exactly the highest-stakes phases, and they are precisely where the gate is currently weakest, because enforcement depends on a human remembering a flag. The policy to do better already ships in the config and is simply unused.

**Criticality: HIGH (for the affected phases).** A safety-relevant phase can ship with no release-gate evidence purely through human omission. Overall severity is tempered only because the manual flag still works when remembered.

**Effect once applied.** The validator loads `qc-config.json`, matches `release_phase_patterns` against the phase title / `phase-record.md` / (later) changed-file paths, and sets `release_required` automatically; `--release-phase` becomes an override rather than the sole trigger. The computed decision is persisted to the board's `release_required` field (added in Change 5 / `PATCH-02`).

### Change 5 — Ship `record_decision.py` + `record_gate_decision.py`; reconcile the board schema

**Current behaviour.** Both scripts are absent (`ls` confirms). `decision-log.jsonl` is created but never read or written by any code. `phase-board.json` is written only by `start_phase()` — always `current_phase_status: open`, `latest_gate_decision: pending` — and is never updated after the gate. The documented board schema (release requirement, revise-attempt count, final-gate timestamp) is not present in the seeded template or in the board `start_phase` writes.

**Evidence.** After a green strict-gate pass in the live run, the board still read `current_phase_status: "open"`, `latest_gate_decision: "pending"`. `grep` confirms only `start_phase` writes the board, and that no script contains any `revise`/`attempt` counter.

**Why it is wrong.** Two coupled defects. (a) `accepted_with_risk` is the system's deliberate gate *bypass* — the one path that most needs a durable, validated audit trail — yet it is currently an honour-system note with no enforced record. (b) The board, the documented single source of truth for "where are we and may the next phase start," never reflects any gate outcome, and the documented schema fields are missing.

**Criticality: HIGH.** A bypass with no audit trail, plus a permanently stale state file, undermines both auditability and sequencing.

**Effect once applied.** `record_decision.py` appends structured `accepted_with_risk`/approval records to `decision-log.jsonl` (impact, owner, rollback, deadline, follow-up, decision id), enabling the validator to enforce "an `accepted_with_risk` gate requires a matching decision-log entry." `record_gate_decision.py` writes the final board transition and increments `revise_attempts`, making the documented "cap at three" observable and enforceable. The board schema gains `release_required`, `revise_attempts`, and `last_gate_at`. **The board half of this change is specified in full in `PATCH-02`.**

## 4. Cross-cutting effects

- **Exit-code contract.** The validator currently returns `0`/`1`. The V02 docs target a richer contract (`0` pass, `10` strict-gate failure, `20` schema/config/invocation error, `30` safety blocker). Changes 1–4 add new strict-gate failure conditions; this is the natural moment to adopt the `10`/`20`/`30` split so the controller can classify outcomes deterministically instead of inferring from a bare `1`.
- **Board schema migration.** Adding `release_required`, `revise_attempts`, and `last_gate_at` requires bumping the board template and tolerating older boards that lack them (read with defaults).
- **Staged rollout.** Because every change makes the gate *stricter*, gate them behind `qc-config.json` toggles (e.g. `enforce_role_verdicts`, `enforce_issue_register`, `require_passing_test`, `auto_release_detect`) defaulting to `true`, so a project can stage adoption and isolate any single change during bring-up.
- **Backward compatibility / expected breakage.** Phases that pass today **may begin to fail** after this patch — specifically any phase that was green only because a `block`/`revise` verdict, an open blocker issue, an all-skipped test set, or a missing release gate was being ignored. **This is the intended outcome**: those were false greens. The migration note for users is simply that previously-passing phases should be re-validated and any newly surfaced stop signal resolved.

## 5. Cost of not applying

Without this patch, "green" is unreliable in named, reproducible ways: a reviewer can say `block`, a compliance agent can file a blocker, a tester can skip everything, and a deploy phase can omit its release gate — and the gate still passes. The system would continue to *look* like a trustworthy QC process while providing assurance it cannot actually back. For a tool whose purpose is to make Codex builds *easier to trust*, that is a direct contradiction of the mission, and it gets more costly as more builds rely on the gate result.

## 6. Acceptance criteria (testable definition of done)

Reuse the audit harness. The patch is complete when, on a clean target project:

1. **Baseline stays green.** A fully-evidenced phase still passes strict (`exit 0`).
2. **Existing enforced gates stay enforced.** Cases `N1`–`N5` still fail: Ponytail latest `revise`; a recorded test `fail`; a planted secret / non-loopback URL; a release phase with `release-gate.md` `not_applicable`; an unaccepted blocker deviation.
3. **The four false greens flip to FAIL.** Cases `G1`–`G4` now fail strict: a required report with `Verdict: block` (and, separately, `Verdict: revise`); an open blocker in `issue-register.jsonl`; an all-`skipped` test set; a release-pattern phase validated **without** `--release-phase`.
4. **Bypass is auditable.** An `accepted_with_risk` gate passes **only** when a matching `decision-log.jsonl` entry exists; absent it, the gate fails.
5. **Exit codes are classified.** Strict-gate failures, schema/invocation errors, and safety blockers return distinct codes (`10`/`20`/`30`).

## 7. Suggested priority order

1. **Change 1** (revise/block scan) — CRITICAL, ~15 lines, highest trust impact.
2. **Change 2** (issue-register read) — HIGH, reactivates the compliance channel.
3. **Change 4** (release auto-detect) — HIGH for the riskiest phases; uses config that already ships.
4. **Change 3** (skipped-test rule) — MEDIUM, cheap, closes an advertised guarantee.
5. **Change 5** (`record_decision.py` / `record_gate_decision.py` + board) — HIGH; larger surface, detailed in `PATCH-02`; unlocks the `accepted_with_risk` enforcement that Changes 1–2 lean on.
