# Builder Team QC

Builder Team QC is a local Codex plugin/process for phase-controlled multi-agent software builds.

It turns a normal Codex build into an evidence-first builder-team workflow with stable role contracts, `.qc` phase records, Ponytail minimal-code checks, seam audits, test evidence, compliance review, and strict gate validation.

## Project Status

| Field | Value |
| --- | --- |
| Version | `0.1.0-planning` |
| Package type | Codex plugin/process |
| Runtime mode | Local-only V01 |
| Primary controller | `phase-controller` |
| Evidence store | Project-local `.qc/` folder |
| Safety posture | No secrets, no remote services, no public tunnels by default |

## What It Includes

- Codex plugin package under [`plugin/`](plugin/)
- Static article page under [`site/`](site/)
- Project master file: [`MASTER.md`](MASTER.md)
- Version metadata: [`project.json`](project.json)
- Folder contract: [`STRUCTURE.md`](STRUCTURE.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)

## Role Model

```text
phase-controller
  builder-agent
  ponytail-adapter
  test-agent
  reviewer-agent
  compliance-agent
  integration-agent
  release-agent
```

## Gate Model

```text
builder output
  -> Ponytail minimal-code gate
  -> test/review/compliance/seam/release evidence
  -> strict validation
  -> pass / revise / block / accepted_with_risk
```

## Safety Defaults

Builder Team QC is local-first by default:

- no API keys
- no OAuth files
- no passwords
- no refresh tokens
- no service-account private keys
- no remote MCP/A2A/OpenAPI surfaces by default
- no remote Docker daemon by default
- no public tunnel or exposed server port by default
- no global install requirement for V01

## Quick Start

Use this prompt from Codex in a target project:

```text
Use builder-team-qc for this build.
Target root: <project path>
Build plan: <plan path>
Current phase: <phase id and title>
Run the phase controller with Ponytail minimal-code checks, tests, seam audit, compliance review, and strict gate validation.
```

## Version

Current project version: `0.1.0-planning`
