# Builder Team QC Master File

This is the canonical project map for Builder Team QC.

## Identity

| Field | Value |
| --- | --- |
| Project name | Builder Team QC |
| Package name | `builder-team-qc` |
| Repository path | Branch root on `Codex-builder-team-multiagents` |
| Version | `0.1.0-prototype` |
| Owner namespace | `randy-aloop/everythingcodex` |
| Primary deliverable | Local Codex plugin/process |
| Secondary deliverable | Static developer article page |

## Description

Builder Team QC coordinates Codex software builds through a local phase-gated multi-agent process. It mimics useful Google ADK orchestration patterns while staying local, explicit, and evidence-first.

The system uses role skills as permanent sub-agent contracts, scripts as explicit tools, and `.qc/` as shared session state. The phase controller owns the gate and does not advance until required evidence is present.

## Attribution

Ponytail credit: the `ponytail-adapter` credits [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), the MIT-licensed Ponytail project by Dietrich Gebert. Builder Team QC uses Ponytail as a local minimal-code discipline/checklist by default and does not vendor or run upstream Ponytail hooks unless they are explicitly reviewed, enabled, and recorded.

## Current Package Map

```text
builder-team-qc/
  README.md
  MASTER.md
  VERSION
  project.json
  STRUCTURE.md
  CHANGELOG.md
  plugin/
    .codex-plugin/
    assets/
    docs/
    scripts/
    skills/
  site/
    index.html
```

## Role Contracts

| Role | Purpose |
| --- | --- |
| `phase-controller` | Opens phase records, routes role checks, validates evidence, and decides gates. |
| `builder-agent` | Implements only the smallest correct current-phase change. |
| `ponytail-adapter` | Applies minimal-code discipline and records the Ponytail verdict. |
| `test-agent` | Runs quick checks and records runnable proof. |
| `reviewer-agent` | Checks architecture fit, minimal code, and implementation quality. |
| `compliance-agent` | Verifies plan adherence, approvals, protected zones, and no-secrets behavior. |
| `integration-agent` | Audits previous/current/next phase seams. |
| `release-agent` | Checks production debug, runtime, Docker, rollback, and readiness evidence. |

## Gate Outcomes

- `pass`
- `revise`
- `block`
- `accepted_with_risk`

## Promotion Checklist

- [x] Local plugin scaffold exists.
- [x] Role skills exist.
- [x] `.qc` templates exist.
- [x] Helper scripts exist.
- [x] Orchestration notes exist.
- [x] Static article page exists.
- [ ] Runtime hook runner exists.
- [ ] Sample project pass/revise/pass trial exists.
- [ ] First real-project trial completed.

## Version Policy

Use semantic-ish project versions:

- `0.1.0-planning`: initial local docs and plugin package.
- `0.1.0-prototype`: branch-installable prototype with installation guide, dry-run/test evidence, and build-plan authoring guide.
- `0.2.0-trial`: sample project trial with pass/revise/pass cycle.
- `0.3.0-plugin-mvp`: plugin ready for repeated local use.
- `1.0.0`: stable reusable workflow with documented promotion gates.
