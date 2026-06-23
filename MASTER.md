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
      README.md
      MASTER.md
      VERSION
      project.json
      STRUCTURE.md
      CHANGELOG.md
      plugin/
      site/
```

## Projects

### Builder Team QC

Path: `projects/builder-team-qc/`

Description: local phase-controlled multi-agent builder system for Codex. It coordinates builder, reviewer, test, compliance, integration, release, and Ponytail roles through `.qc` evidence records and strict phase gates.

Status: `v0.1.0-planning`

Primary files:

- [Project README](projects/builder-team-qc/README.md)
- [Project master file](projects/builder-team-qc/MASTER.md)
- [Project structure](projects/builder-team-qc/STRUCTURE.md)
- [Version metadata](projects/builder-team-qc/project.json)
- [Static article page](projects/builder-team-qc/site/index.html)
- [Codex plugin package](projects/builder-team-qc/plugin/)

## Promotion Rules

Projects should only be promoted from planning to trial when:

- project README is present
- master file is present
- version metadata is present
- folder structure is documented
- safety defaults are documented
- at least one validation path is recorded
- no secrets or credentials are present
