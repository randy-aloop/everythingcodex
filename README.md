# Everything Codex

Everything Codex is a public index for reusable Codex workflows, plugins, build-control patterns, and operator documentation.

## Current Projects

| Project | Status | Location | Description |
| --- | --- | --- | --- |
| [Builder Team QC](https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents) | `v0.2.1-trial` | [`Codex-builder-team-multiagents`](https://github.com/randy-aloop/everythingcodex/tree/Codex-builder-team-multiagents) branch | Phase-gated local multi-agent trial plugin for Codex with installable project-local QC records, stricter validation helpers, docs, scripts, role skills, seam audits, release gates, and rollback-ready evidence. |

Visual site: [Builder Team QC](https://randy-aloop.github.io/everythingcodex/builder-team-qc/)

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
