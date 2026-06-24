# Everything Codex

Everything Codex is a public index for reusable Codex workflows, plugins, build-control patterns, and operator documentation.

## Current Projects

| Project | Status | Description |
| --- | --- | --- |
| [Builder Team QC](https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents) | `v0.1.0-planning` | Local, phase-controlled multi-agent builder process for Codex with Ponytail minimal-code gates, `.qc` evidence records, role contracts, and strict phase validation. |

Builder Team QC now lives on the standalone [`Codex-builder-team-multiagents`](https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents) branch. The `main` branch keeps the repository description and project index.

## Repository Purpose

This repository collects Codex-native systems in a way that is easy to inspect, version, trial, and promote:

- project master files
- project READMEs
- version metadata
- folder structure contracts
- orchestration notes
- local-first safety policies
- build and validation records

## Safety Baseline

Unless a project explicitly says otherwise, Everything Codex projects default to:

- local-first operation
- no secrets in repo
- no API keys, OAuth files, passwords, refresh tokens, or service account keys
- no public tunnel or remote server exposure by default
- no global install requirement for V01 artifacts
- evidence-first validation before reuse

## Versioning

Repository version: `0.1.0`

Project versions are tracked inside each project branch or folder with a local `VERSION` file and `project.json` metadata.

## Master Index

See [MASTER.md](MASTER.md) for the canonical repository map.
