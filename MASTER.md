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

Visual site: [`https://randy-aloop.github.io/everythingcodex/builder-team-qc/`](https://randy-aloop.github.io/everythingcodex/builder-team-qc/)

Main pointer: `projects/builder-team-qc/README.md`

Description: Builder Team QC is a local, phase-controlled multi-agent trial plugin for Codex that helps make builds easier to trust. It was built from a real non-coder workflow: turning scattered ideas, requirements, app notes, and rough specs into working tools.

The system breaks a build into auditable phases. Each phase uses role skills, script tools, Ponytail minimal-code checks, and `.qc` evidence records to track scoped changes, tests, reviews, compliance checks, seam audits, release gates, and strict validation.

The current `0.2.1-trial` line is intentionally local-first. It installs into a target project, runs as a Codex-controlled workflow rather than remote autonomous agents, and avoids public tunnels, remote services, and hidden API access by default.

Status: `v0.2.1-trial`

Primary files:

- [Project README](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/README.md)
- [Project master file](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/MASTER.md)
- [Project structure](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/STRUCTURE.md)
- [Version metadata](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/project.json)
- [Static article page](https://github.com/randy-aloop/everythingcodex/blob/Codex-builder-team-multiagents/site/index.html)
- [Published visual site](https://randy-aloop.github.io/everythingcodex/builder-team-qc/)
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
