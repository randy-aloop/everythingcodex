# Everything Codex Master Index

This file is the canonical map for the repository.

## Repository Metadata

| Field | Value |
| --- | --- |
| Repository | `randy-aloop/everythingcodex` |
| Version | `0.1.0` |
| Default branch | `main` |
| License | MIT |
| Bootstrap date | 2026-06-23 |
| Primary purpose | Reusable Codex systems, plugins, docs, and build-control patterns |

## Folder Structure

```text
/
  README.md
  MASTER.md
  VERSION
  LICENSE
  projects/
    builder-team-qc/
      README.md  # pointer to standalone branch
```

## Projects

### Builder Team QC

Branch: [`Codex-builder-team-multiagents`](https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents)

Main pointer: `projects/builder-team-qc/README.md`

Description: local phase-controlled multi-agent builder system for Codex. It coordinates builder, reviewer, test, compliance, integration, release, and Ponytail roles through `.qc` evidence records and strict phase gates.

Status: `v0.1.0-prototype`

Primary files:

- [Project README](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/README.md)
- [Project master file](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/MASTER.md)
- [Project structure](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/STRUCTURE.md)
- [Version metadata](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/project.json)
- [Static article page](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/site/index.html)
- [Codex plugin package](https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents/plugin)

## Promotion Rules

Projects should only be promoted from planning to trial when:

- project README is present
- master file is present
- version metadata is present
- folder structure is documented
- safety defaults are documented
- at least one validation path is recorded
- no secrets or credentials are present
