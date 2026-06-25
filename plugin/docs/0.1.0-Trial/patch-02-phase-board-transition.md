# Patch Rationale 02 — Phase-Board Gate Transition (`record_gate_decision.py`)

| Field | Value |
| --- | --- |
| Patch ID | `PATCH-02` |
| Document version | `PATCH-02.V02` |
| Target version | `0.1.0-prototype` → `0.2.0-trial` |
| Supersedes | `PATCH-02.V01` proposed rationale |
| Scope | New `scripts/record_gate_decision.py`; `phase-board.json` schema; `phase-controller` skill step 13; `.qc/gate-events.jsonl` |
| Status | Implemented in `0.2.0-trial` hardening pass on 2026-06-24 |
| Evidence basis | Live run of the V01 pipeline (the board state after a passing strict gate) plus `grep` of `scripts/*.py` for every board write and any revise/attempt counter; implementation verified by `hardening-smoke-20260624` |
| Parent | `PATCH-01`, Change 5 (this document specifies the board half in full) |

---

## 1. Summary

In the README "Architecture" diagram the workflow terminates with `strict gate validation → {pass / revise / block / accepted_with_risk} → update phase-board.json → user-facing gate result`. That `update phase-board.json` box has **no code behind it.** The phase board is written exactly once, by `start_phase()`, always as `current_phase_status: open` / `latest_gate_decision: pending`, and nothing ever updates it again. A passing gate does not advance it; a blocked gate does not mark it; a revise does not count against it.

This patch adds `record_gate_decision.py` so the controller can durably record the gate outcome it decided, turning the board into live state and making the diagram's final two arrows literally true. It is the single highest-value step for diagram fidelity, because `update phase-board.json` is currently the most misleading arrow in the picture.

## 2. The defect

**The board is write-once.** `start_phase()` is the only writer (`grep` confirms; it is the only function that touches `phase-board.json`). It hard-codes `current_phase_status: "open"` and `latest_gate_decision: "pending"`.

**It does not reflect outcomes.** In the live run, after a phase was driven to a fully green strict gate (`exit 0`, zero errors), the board still read:

```json
{ "current_phase_status": "open", "latest_gate_decision": "pending", ... }
```

The gate passed; the board did not move.

**It cannot even represent a sequence.** Because `start_phase()` *overwrites* the board on every call, the board only ever shows *the most recently started phase, as open/pending.* It has no field and no log recording that, say, `phase-001` passed and the project is now on `phase-002`. There is no phase history anywhere in `.qc` that the board or a reader can consult.

**The revise loop is invisible.** The documented "cap at three failed revise attempts" lives only in prose and the controller skill. No script contains any `revise`/`attempt` counter (`grep` confirms), and the board has no `revise_attempts` field, so the cap cannot be observed, let alone enforced.

**The fallback is hand-editing.** `phase-controller` SKILL.md step 13 instructs Codex to "Update `.qc/phase-board.json` with the final gate transition" — i.e. hand-edit a JSON file. That is error-prone (a single malformed edit silently corrupts the project's only state file) and inconsistent with the project's own "scripts record evidence, the controller decides" division of labour.

## 3. Why this is critical

**Criticality: HIGH.** This is the terminal node of the entire workflow. If it does not fire correctly, the *recorded outcome of every phase is wrong or stale*, regardless of how well every upstream step ran.

- **Single source of truth is permanently stale.** The board is documented as the at-a-glance answer to "current phase, status, latest gate, next phase." A board frozen at `open`/`pending` answers that question incorrectly for every completed phase. Any human — or any future automation — that reads the board to decide what to do next is reading fiction.
- **A documented safety rule is unenforceable.** The docs state "No next phase should start until the current gate allows it" and "update phase-board final state before allowing the next phase." Both depend on the board reflecting the gate. Since it never does, the sequencing guard cannot be derived from state; it survives only as controller goodwill.
- **The revise cap cannot be enforced.** "Stop after three failed attempts" is a safety mechanism against blind retry loops. With no durable counter, nothing can stop the loop or even report how many attempts have occurred.
- **Manual edits invite silent corruption.** Hand-editing the one JSON file that represents project state is exactly the kind of unaudited, side-effect-prone action the rest of the system is designed to avoid.
- **It is the most visible doc-vs-code divergence.** A reader comparing the architecture diagram to the running system will see every other terminal step behave roughly as drawn, then find the final state-update box does nothing. That single dead arrow disproportionately damages confidence in the whole diagram.

## 4. Design of the fix

Add `record_gate_decision.py`, a thin recorder consistent with the existing `record_*` scripts.

**Design principle (this matters for the local-control posture):** the script does **not decide** the gate. The validator remains binary (`pass`/`fail`); the controller still performs the four-way classification (`pass` / `revise` / `block` / `accepted_with_risk`). `record_gate_decision.py` only *durably records the decision the controller already made*, with a fixed schema and a timestamp. This strengthens the "scripts record, controller decides" boundary rather than weakening it, and it removes the hand-editing step without moving any authority into code.

Proposed interface:

```text
record_gate_decision.py
  --root <project>
  --phase-id <id>
  --gate {pass|revise|block|accepted_with_risk}
  --next-phase-id <id>            # used when gate=pass to advance
  --decision-id <id>              # REQUIRED when gate=accepted_with_risk
  --note "<short rationale>"
```

Behaviour:

1. Update `phase-board.json`:
   - `latest_gate_decision` = `--gate`
   - `current_phase_status` = terminal status derived from the gate (`passed` / `revising` / `blocked` / `accepted_with_risk`)
   - `last_gate_at` = UTC timestamp
   - on `pass`/`accepted_with_risk`, set `next_phase_id` and mark the phase ready to hand off
2. On `--gate revise`, increment `revise_attempts`. If it reaches the cap from `qc-config.json` (default 3), refuse the transition and emit a `block`-class result so the loop cannot silently exceed the cap.
3. On `--gate accepted_with_risk`, refuse unless `--decision-id` resolves to an existing entry in `decision-log.jsonl` (created by `record_decision.py` from `PATCH-01`, Change 5). This preserves the rule that the controller must not self-approve a bypass.
4. Append an immutable record to `.qc/gate-events.jsonl` (phase id, gate, attempt number, decision id, timestamp). Because `start_phase()` overwrites the board, this append-only log is what preserves true phase-by-phase history.

**Board schema additions** (also referenced by `PATCH-01`, Change 4/5):

```json
{
  "release_required": false,
  "revise_attempts": 0,
  "last_gate_at": null
}
```

Older boards lacking these fields are read with defaults.

**Controller change.** Replace SKILL.md step 13 ("hand-edit the board") with "call `record_gate_decision.py` with the decided gate." Step 14 ("do not start the next phase unless the current gate allows it") then has real state to check.

## 5. Effects once applied

- **The diagram becomes literally true.** `update phase-board.json` is now a real action, and the board reflects the gate decision that preceded it, so the final two arrows describe what actually happens.
- **The board is live, queryable state.** "Where are we, what was the last gate, what is next" is answerable from the file at any time.
- **The sequencing guard becomes enforceable.** A wrapper (or the validator invoked by the controller) can refuse to start a new phase unless the prior phase's board status is a terminal `passed` or `accepted_with_risk`.
- **The revise cap becomes real.** `revise_attempts` is durable and checked; the third failed attempt is stopped rather than merely discouraged.
- **The bypass is auditable.** `accepted_with_risk` cannot be recorded without a linked decision-log entry, closing the honour-system gap for the system's only deliberate gate bypass.
- **Corruption risk drops.** A fixed-schema recorder replaces freehand JSON editing.

## 6. Relationship to `PATCH-01`

This document is the detailed specification of the board half of `PATCH-01`, Change 5. The two recorders are siblings: `record_decision.py` makes `accepted_with_risk` *justifiable* (the decision-log entry), and `record_gate_decision.py` makes the gate outcome *durable* (the board transition + history). `PATCH-02` can land independently and deliver immediate diagram-fidelity value; the `accepted_with_risk` decision-link in step 3 above only becomes enforceable once `record_decision.py` exists, so if shipped first, that single check is staged in as a follow-up.

## 7. Acceptance criteria

On a clean target project:

1. After a passing strict gate, `record_gate_decision.py --gate pass --next-phase-id <next>` leaves the board with `current_phase_status` terminal-pass, `latest_gate_decision: pass`, and a non-null `last_gate_at`; the board no longer reads `open`/`pending`.
2. A `--gate revise` increments `revise_attempts`; a third consecutive `revise` is refused and reported as a block-class outcome.
3. `--gate accepted_with_risk` without a resolvable `--decision-id` is refused; with one, it succeeds and links the decision id.
4. `.qc/gate-events.jsonl` contains one append per gate decision, preserving multi-phase history even though `start_phase()` overwrites the board's `current_*` fields.
5. Attempting to `start_phase` a new phase while the prior phase's board status is non-terminal is refused or warned, per the wired guard.

## 8. Backward compatibility

The new board fields are additive and read with defaults, so existing boards remain valid. Flows that previously hand-edited the board continue to work; the script standardises and timestamps that edit rather than forbidding the old path. No upstream script changes behaviour as a result of this patch alone.
