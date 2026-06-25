# Chronological Thread Record

Version: `0.1.0-prototype`
Created: 2026-06-24

Public archive note: this is a sanitized historical record for the `0.1.0-prototype` line. It is not current operating guidance for `0.2.1-trial`; use the live docs and changelog for current installer, validator, and gate behavior.

This record reconstructs the project thread in chronological order from the available conversation context and local artifacts. It is structured as input, interpretation, output, and resulting decision.

## 1. Initial Builder-Team Concept

Input:

The project began with a request to build a tech deck and documentation for a multiagent builder. The starting plan was a separate-scope build plan for a reusable `builder-team-qc` plugin/process.

Interpretation:

The desired system was not just a document. It was a reusable Codex builder-control method with roles, phase gates, Ponytail discipline, and `.qc/` audit records.

Output:

- Recommendation to shape the work as a Codex plugin.
- Proposed plugin names: `builder-team-qc` or `ponytail-builder-teams`.
- Role set: phase-controller, builder-agent, reviewer-agent, test-agent, compliance-agent, integration-agent, release-agent.
- Script and template categories for `.qc/` records.

Decision:

Start with an instruction-plus-scripts plugin, not a heavy MCP/runtime system.

## 2. Google ADK Deep Dive

Input:

The user provided Google ADK multiagent codelab material and a forked ADK Python repo reference.

Interpretation:

The project needed a deep technical understanding of ADK concepts: agent hierarchy, workflow agents, shared state, routing, API surfaces, remote/tool risks, and hardening.

Output:

- Deep-dive report on ADK/fork internals.
- Tech deck companion.
- Security/hardening notes around API keys, remote services, A2A, MCP, OpenAPI, Docker/cloud hooks, and credential surfaces.

Decision:

Use ADK concepts as architecture inspiration, but keep Builder Team QC local-first and Codex-controlled.

## 3. Builder Team QC Deck And Brief

Input:

The user asked to use the ADK knowledge to mimic/build the builder-team multiagent system and improve the deck/brief.

Interpretation:

Create artifacts that explain how Builder Team QC works as a Codex multiagent process, not as a Google ADK runtime.

Output:

- PowerPoint tech deck.
- Technical brief.
- QA notes for deck and document structure.

Decision:

Keep the docs separate from unrelated prompt-harness docs and treat the builder team as its own reusable product.

## 4. Orchestration Notes And Diagrams

Input:

The user asked how the multiagent builder runs, provided ADK diagrams, and asked for orchestration notes and drawings.

Interpretation:

Translate ADK concepts into Builder Team QC flow:

```text
Sequential phase pipeline
parallel-style evidence checks
bounded revise loop
.qc as shared state
Codex as phase-controller
```

Output:

- `docs/orchestration-notes.md`
- `docs/orchestration-diagram.md`
- Clarification that Ponytail is a gate/check across builder output, not only part of test-agent.

Decision:

In Runtime V01, "parallel" means logical fan-out only. Codex still executes roles sequentially.

## 5. Web Page And GitHub Project Creation

Input:

The user asked for an identical/reference-style page for Builder Team QC and then asked to create the project under `randy-aloop/everythingcodex`.

Interpretation:

Package the system as a project with README, MASTER file, metadata, folder structure, plugin package, docs, and static site.

Output:

- Static article page.
- Repository README and MASTER.
- Project metadata.
- Plugin package structure.
- GitHub remote under `projects/builder-team-qc`.

Known commits from the thread:

- `320ff5c Bootstrap builder-team-qc project`
- `d789dd0 Harden builder-team-qc gate docs`
- `9a8d907 Credit upstream Ponytail project`

Decision:

Use GitHub as public project packaging, but keep local source under the local durable project area as the working source of truth.

## 6. Privacy And Path Cleanup

Input:

The user asked whether private/person data was published and requested fable5 audit.

Interpretation:

Search for workstation paths, local machine references, secrets, and personal data before relying on the public repo.

Output:

- Identified full and partial workstation path leaks.
- Replaced local path references with online GitHub project paths.
- Verified no intentional secrets were found.

Decision:

Public docs should use repository URLs or project-relative paths, not workstation paths.

## 7. HTML Review And Fixes

Input:

The user asked to fix the HTML documentation page after a review identified issues.

Interpretation:

The page itself needed frontend/document polish, while the system design also needed precision around gates, soft constraints, accepted risk, Ponytail definition, and deterministic validation.

Output:

- Review notes identified raw markdown backticks, missing font loading, sticky anchor offset, heading hierarchy, and SVG `rx` misuse.
- Later page/docs were adjusted in related work.

Decision:

Separate visual/document issues from the underlying system correctness issues.

## 8. Fable5 Gap Report And Docs Hardening

Input:

The user asked to run fable5-enhance on core docs and then fix gaps from a gap report.

Interpretation:

The docs needed to stop overclaiming and make the strict gate more deterministic.

Output:

Patched docs:

- `multi-agent-modes.md`
- `orchestration-diagram.md`
- `orchestration-notes.md`
- `phase-loop.md`
- `production-debug-gate.md`
- `qc-record-schema.md`

Key fixes:

- Accepted-risk requires decision-log proof.
- Role verdicts `revise` and `block` are failures.
- Skipped tests cannot satisfy required proof.
- Release phases require release-aware validation.
- Phase-controller ordering puts Ponytail before deeper checks.
- Loop cap is explicit.
- Schema was expanded.
- Final gate transition became a required record.

Decision:

Strict-gate claims must either be implemented or clearly documented as manual/current gaps.

## 9. Ponytail Attribution

Input:

The user asked to credit `DietrichGebert/ponytail`.

Interpretation:

The project uses Ponytail discipline conceptually and should credit the upstream source.

Output:

- Attribution added across docs, metadata, site, and Ponytail adapter skill.
- Clarified that Builder Team QC does not vendor or run upstream Ponytail by default.

Decision:

Ponytail is a credited discipline/fallback adapter unless upstream hooks are explicitly reviewed and enabled.

## 10. Phase-By-Phase Run Plan

Input:

The user asked how the builder team works phase by phase and requested a latest detailed plan.

Interpretation:

Create an operational runbook for one phase at a time.

Output:

- `docs/phase-by-phase-run-plan.md`

Core flow:

```text
intake
init .qc
start phase
builder
persist diff evidence
Ponytail
evidence fan-out
strict gate
revise/block/pass/accepted risk
phase-board update
handoff
```

Decision:

One product phase is the unit of control.

## 11. Review Execution Against Seven Docs

Input:

The user provided review files and asked to execute against seven docs.

Interpretation:

Use fable5-style process: report before patching, then patch docs, without pushing to GitHub.

Output:

- Redacted local Fable5 run record.
- Prepatch report.
- Patched seven docs.
- Added helper gap disclosures.
- Added V02 metadata and `docs/CHANGELOG.md`.

Decision:

Documented target contracts must say what is current helper behavior versus future helper behavior.

## 12. Runtime Usage And Agent Count

Input:

The user asked how to use/call the builder multiagent team and how many agents run.

Interpretation:

Explain invocation and distinguish roles from actual autonomous processes.

Output:

Normal phase roles:

```text
phase-controller
builder-agent
ponytail-adapter
test-agent
reviewer-agent
compliance-agent
integration-agent
```

Runtime/release phase adds:

```text
release-agent
```

Decision:

Runtime V01 has 7 logical roles for normal phases and 8 for release phases, but they run sequentially in one Codex runtime.

## 13. V02 Run Plan Findings And V03 Fix

Input:

The user provided detailed V02 findings against `phase-by-phase-run-plan.md`.

Interpretation:

First assess findings read-only, then apply all approved fixes.

Output:

- `phase-by-phase-run-plan-V02-findings-assessment.md`
- `phase-by-phase-run-plan.md` bumped to V03.
- Changelog updated for V03.

Key fixes:

- Phase 0 no longer writes durable `.qc` records before `.qc` exists.
- One-Page Run Order matches body phase numbering.
- `release-gate.md` `not_applicable` path clarified.
- `required_evidence` completed.
- Target layouts distinguish helper output from manual records.
- Lessons feed forward into future Phase 0 intake.
- `record_decision.py` target id/timestamp behavior defined.
- Non-strict validator warning/error behavior clarified.
- `release_not_applicable_rationale` behavior for release phases defined.

Decision:

Document V03 describes current Runtime V01 unless a later runtime version is explicitly named.

## 14. Post-V03 Evidence And Packaging Docs

Input:

After the V03 run-plan fix, the project added several evidence and usability documents that moved parts of the prototype beyond the earlier "planned only" state.

Interpretation:

These documents should be read as post-V03 evidence. They do not make the project alpha by themselves, but they changed the current-state baseline for `0.2.0-trial`.

Output:

- V05 added first-class builder-scope audit support across scripts, validator wiring, role guidance, and docs.
- V06 added `build-plan-authoring-guide.md` for writing enforceable phase contracts.
- V07 added `installation-and-first-run-guide.md` for direct local use.
- V08 added `installation-dry-run-and-stress-test-report.md`.
- V09 added `agent-dry-run-and-test-report.md`.

Decision:

For future trial work, use the changelog plus these post-V03 docs as current evidence. Older V03 references in this archive are historical unless a later section says they describe current behavior.

## 15. Safety Scanner False Positives

Input:

The user asked about safety scanner findings and whether Codex can run the multiagent system.

Interpretation:

Explain effect and better fix.

Output:

- Codex can run the system.
- Strict gate may block if safety scan treats docs/scanner definitions as blockers.
- Better fix: severity classification, not deleting banned markers.

Decision:

Do not remove scanner patterns. Make scanner context-aware:

```text
blocker = active risky behavior or possible secret
warning = risky term needing review
info = policy/reference/scanner self-definition
```

Later current-state note:

The scanner now has severity classification logic. `0.2.0-trial` should validate and tune it against a real project rather than treat severity classification as entirely unimplemented.

## 16. Single-Run Vs Parallel Runtime

Input:

The user asked to compile the reason for single-run multiagent versus parallel.

Interpretation:

Create a dedicated doc explaining Runtime V01 and future Runtime V02 trade-offs.

Output:

- `docs/single-run-vs-parallel-runtime.md`

Decision:

Runtime V01 remains single-run multiagent. Future Runtime V02 may use a hybrid model:

```text
sequential build
parallel evidence checks
sequential strict gate
```

## 17. Alpha Transition Planning

Input:

The user wanted to move into alpha and supplied review guidance saying not to bump beta and only use alpha after contradictions are fixed.

Interpretation:

Turn review findings into a detailed alpha readiness plan.

Output:

- `docs/alpha-transition-phase-plan.md`

Phases:

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

Decision:

Current honest version remains planning/prototype until a real local trial proves end-to-end usability.

## 18. Move Toward 0.2.0-Trial

Input:

The user now wants to advance into `0.2.0-trial` and requested this full prototype conversation/process archive.

Interpretation:

Before trial work begins, preserve the prototype history in a versioned package.

Output:

- This `docs/0.1.0-prototype/` archive.

Decision:

`0.1.0-prototype` is the historical foundation. `0.2.0-trial` should focus on making the tool run on a real local target and resolving script/doc mismatches.
