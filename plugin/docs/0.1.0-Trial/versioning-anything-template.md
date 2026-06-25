# Versioning Template - Anything

Use this for any versioned change: product releases, patches, docs, schemas, skills, prompts, datasets, workflows, tools, or operational processes.

Copy the template, replace bracketed placeholders, and delete sections that do not apply.

---

# [Change Type] [ID] - [Short Title]

| Field | Value |
| --- | --- |
| Change ID | `[PATCH-00 / RELEASE-00 / DOC-00 / SCHEMA-00 / SKILL-00]` |
| Thing being versioned | `[product / package / document / skill / workflow / dataset / API / schema / other]` |
| Current version | `[0.0.0-state-name]` |
| Target version | `[0.0.0-state-name]` |
| Version movement | `[major / minor / patch / prerelease / docs-only / operational]` |
| Scope | `[files, folders, modules, processes, teams, or artifacts affected]` |
| Status | `[Draft / Proposed / Approved / In Progress / Landed / Rejected / Superseded]` |
| Owner | `[person, team, or agent role]` |
| Evidence basis | `[audit, run log, user request, bug report, diff, benchmark, incident, decision record]` |
| Parent / companion | `[related change IDs or none]` |
| Created | `[YYYY-MM-DD]` |
| Last updated | `[YYYY-MM-DD]` |

---

## 1. Summary

[One to three paragraphs explaining what changes, why it matters, and what the reader should remember.]

The shortest useful version:

- From: `[current behavior / state]`
- To: `[target behavior / state]`
- Because: `[reason this change is needed now]`

## 2. Version Intent

This version exists to [complete / harden / fix / simplify / document / migrate / deprecate / release] [the thing].

It should be considered successful when:

1. [Observable outcome 1]
2. [Observable outcome 2]
3. [Observable outcome 3]

It is not intended to:

1. [Explicit non-goal 1]
2. [Explicit non-goal 2]

## 3. Why This Is Versioned

[Explain why this deserves a version boundary instead of being an untracked edit.]

Useful prompts:

- What contract changes?
- What downstream users, agents, systems, docs, or workflows need to know?
- What would become confusing if this changed silently?
- What previous artifact does this supersede?

## 4. Current State

[Describe the current behavior, artifact, schema, workflow, or document.]

Evidence:

- [Evidence item 1: command, file, log, screenshot, test, quote, run ID]
- [Evidence item 2]
- [Evidence item 3]

Known gaps:

- [Gap 1]
- [Gap 2]

## 5. Proposed Target State

[Describe the desired future state after the version lands.]

The target state should make these things true:

- [Invariant or guarantee 1]
- [Invariant or guarantee 2]
- [Invariant or guarantee 3]

## 6. Changes

Repeat this block for each concrete change.

### Change 1 - [Short Name]

**Current behavior.** [What happens now.]

**Problem.** [Why the current behavior is incomplete, risky, confusing, wrong, or outdated.]

**Change.** [What will change.]

**Effect once applied.** [What will be observably different.]

**Criticality.** `[CRITICAL / HIGH / MEDIUM / LOW]` - [short rationale]

**Evidence required.** [What proves the change was made correctly.]

**Affected artifacts.**

- `[path / artifact / process]`
- `[path / artifact / process]`

### Change 2 - [Short Name]

**Current behavior.** [What happens now.]

**Problem.** [Why it matters.]

**Change.** [What will change.]

**Effect once applied.** [What will be observably different.]

**Criticality.** `[CRITICAL / HIGH / MEDIUM / LOW]` - [short rationale]

**Evidence required.** [What proves the change was made correctly.]

**Affected artifacts.**

- `[path / artifact / process]`

## 7. Compatibility And Migration

Backward compatibility:

- [What remains compatible]
- [What older consumers/artifacts need to tolerate]

Expected breakage:

- [What may fail after the change]
- [Why that failure is acceptable or intended]

Migration path:

1. [Step 1]
2. [Step 2]
3. [Step 3]

Rollback path:

1. [How to revert or disable]
2. [What data/state must be preserved]
3. [How to confirm rollback worked]

## 8. Acceptance Criteria

The version is complete when:

1. [Baseline or existing behavior still works.]
2. [New behavior is present and verified.]
3. [Known failure mode now fails safely or is resolved.]
4. [Docs, schema, changelog, or dependent artifacts are updated.]
5. [A reviewer/operator can reproduce the evidence.]

If testable, include exact checks:

```text
[command or manual check]
Expected: [specific result]
```

## 9. Verification Record

Fill this section as work is completed.

| Check | Evidence | Result | Date |
| --- | --- | --- | --- |
| [Check name] | `[command / file / run ID / screenshot]` | `[pass/fail/n/a]` | `[YYYY-MM-DD]` |
| [Check name] | `[command / file / run ID / screenshot]` | `[pass/fail/n/a]` | `[YYYY-MM-DD]` |

## 10. Release / Adoption Plan

Priority order:

1. [First change to land and why]
2. [Second change]
3. [Third change]

Rollout:

1. [Prepare]
2. [Apply]
3. [Verify]
4. [Announce or document]
5. [Monitor]

Communication needed:

- [Who needs to know]
- [What they need to do differently]

## 11. Risks And Open Questions

Risks:

- [Risk 1 and mitigation]
- [Risk 2 and mitigation]

Open questions:

- [Question 1]
- [Question 2]

Decision needed before landing:

- [Decision]

## 12. Version Ledger

Use this as a compact history once the document starts changing.

| Date | Version | Change ID | Status | Notes |
| --- | --- | --- | --- | --- |
| `[YYYY-MM-DD]` | `[0.0.0-state]` | `[ID]` | `[Draft/Proposed/Landed]` | `[short note]` |

## 13. Changelog Entry

Use this if the change needs a public or team-facing changelog.

```markdown
## [Target version] - [YYYY-MM-DD]

### Added
- [New capability, artifact, or guarantee]

### Changed
- [Changed behavior, schema, process, or documentation]

### Fixed
- [Bug, mismatch, or false assumption corrected]

### Deprecated
- [Old behavior or artifact being phased out]

### Removed
- [Removed behavior or artifact]

### Migration Notes
- [Required action for users/operators/agents]
```

## 14. Final Decision

| Field | Value |
| --- | --- |
| Decision | `[Approve / Reject / Supersede / Defer]` |
| Decider | `[person/team/agent role]` |
| Decision date | `[YYYY-MM-DD]` |
| Conditions | `[required follow-up, expiry, owner, or none]` |
| Supersedes | `[older change IDs or none]` |
| Superseded by | `[newer change ID or none]` |

Decision note:

[Short final rationale.]
