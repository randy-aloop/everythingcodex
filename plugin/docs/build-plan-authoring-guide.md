# Build Plan Authoring Guide For Builder-Team QC

This guide explains how to write a project, application, plugin, skill, MCP, or engineering-tool build plan that fits the `builder-team-qc` multiagent workflow.

The short rule:

> Write the build plan as executable governance, not as a broad idea document.

The multiagent can only build safely when each phase is written as a contract. A good phase contract tells the agents what to build, what files may change, what must not change, how to prove the phase works, when to stop, and what the next phase can rely on.

## Why This Format Exists

`builder-team-qc` uses separate role responsibilities:

- `phase-controller` coordinates one phase at a time.
- `builder-agent` implements the smallest correct current-phase change.
- `ponytail-adapter` records minimal-code reasoning.
- `test-agent` records runnable proof.
- `reviewer-agent` checks quality and regressions.
- `compliance-agent` checks plan match, safety, and evidence.
- `integration-agent` checks previous/current/next phase seams.
- `release-agent` handles runtime, release, rollback, and production-debug gates when needed.

The plan must give those roles enough information to make objective decisions.

If the plan says only:

```markdown
Build the backend.
```

the agents cannot know the safe file surface, test proof, seam boundary, dependency limit, or stop condition.

If the plan says:

```markdown
In phase-003, add only `src/config_loader.py` and `tests/test_config_loader.py`.
No new dependencies.
Expose `load_config(path)` returning validated config or raising `ConfigError`.
Run `python -m pytest tests/test_config_loader.py`.
Next phase can rely on `load_config` as the only config entry point.
```

the agents can build, audit, test, stop, correct, and prove the result.

## The Four Enforceable Surfaces

Every phase needs four enforceable surfaces.

### 1. Build Surface

The exact files or globs that may be added, modified, or removed.

This powers the builder scope audit:

```powershell
python scripts/audit_builder_scope.py --root <project-root> --phase-id <phase-id> --snapshot
python scripts/audit_builder_scope.py --root <project-root> --phase-id <phase-id> --audit --allow <path-or-glob>
```

### 2. Behavior Surface

The behavior that must exist when the phase is done.

This answers:

- What user or developer workflow should work?
- What function, command, endpoint, UI flow, file output, or document should exist?
- What error behavior should happen?
- What is explicitly not in scope?

### 3. Evidence Surface

The proof that must be recorded in `.qc`.

At minimum, each phase should produce:

- `.qc/phase-runs/<phase-id>/phase-record.md`
- `.qc/phase-runs/<phase-id>/builder-notes.md`
- `.qc/phase-runs/<phase-id>/reviewer-report.md`
- `.qc/phase-runs/<phase-id>/test-report.md`
- `.qc/phase-runs/<phase-id>/compliance-report.md`
- `.qc/phase-runs/<phase-id>/seam-audit.md`
- `.qc/phase-runs/<phase-id>/release-gate.md`
- `.qc/phase-runs/<phase-id>/evidence/builder-scope-baseline.json`
- `.qc/phase-runs/<phase-id>/evidence/builder-scope-audit.json`
- `.qc/ponytail-events.jsonl`
- `.qc/test-results/<phase-id>.jsonl`
- `.qc/deviation-log.jsonl`

### 4. Stop Surface

The exact conditions that force the process to stop and ask the user.

Examples:

- builder scope audit fails
- Ponytail verdict is not `pass`
- required test fails
- safety scan has a blocker
- a new dependency appears necessary
- phase objective must change
- allowed file surface must expand
- previous/current/next seam does not match
- runtime, deployment, Docker, API, security, or release behavior appears unexpectedly

## Recommended Build Plan Structure

Use this top-level structure:

```markdown
# <Project / Application / Tool> Build Plan

Version: V01
Project Root: <absolute path>
Build Mode: sandbox-first
QC System: builder-team-qc
Start Phase: phase-000
Phase ID Style: phase-000, phase-001, phase-002
Target Environment: <Windows / local Python / Node / browser / etc.>
Owner Decision Policy: stop-and-ask on scope, dependency, architecture, runtime, security, or release changes

## Global Build Rules

## Global Safety Rules

## Global Dependency Policy

## Global Evidence Policy

## Phase Index

## Phase phase-000 - <name>

## Phase phase-001 - <name>
```

## Global Build Rules

Include these rules at the top of every plan unless there is a deliberate reason not to.

```markdown
## Global Build Rules

- Run first in a local sandbox path such as `<local-sandbox>`.
- Do not touch durable project files until sandbox proof passes or the user approves direct work.
- Build phase by phase.
- Do not start the next phase until the current phase strict gate passes.
- Use `audit_builder_scope.py --snapshot` before builder edits.
- Use `audit_builder_scope.py --audit` after builder edits with explicit allowed paths.
- Use Ponytail before test/review fan-out.
- Run one quick test per phase.
- Record deviations as soon as they occur.
- If any deviation, bug, error, missing requirement, or improvement need appears, stop and write a stop report before changing the build.
- Each phase must be modular, debuggable, reviewable, and auditable.
- Each phase must cross-check previous/current/next phase seams.
```

## Global Safety Rules

```markdown
## Global Safety Rules

- Do not store secrets, API keys, OAuth files, passwords, refresh tokens, or service account credentials.
- Do not add public tunnels, exposed ports, remote agents, remote MCP transports, remote Docker daemons, or remote execution surfaces without explicit approval.
- Do not add runtime, server, Docker, deploy, dependency, or production-debug behavior unless the phase type and release gate require it.
- Safety scanner blocker findings stop the phase.
- Documentation may mention forbidden items only as policy-deny text or safe reference material.
```

## Global Dependency Policy

```markdown
## Global Dependency Policy

- Prefer stdlib, native platform APIs, and existing project dependencies.
- New dependencies require a stop report and user approval unless the phase explicitly allows them.
- If a dependency is approved, record:
  - package name
  - version or version range
  - why existing tools cannot satisfy the need
  - install location
  - runtime/release impact
  - rollback plan
```

## Global Evidence Policy

```markdown
## Global Evidence Policy

Each phase must record:

- builder scope baseline
- builder scope audit
- Ponytail event
- quick test result
- deviation log entry if anything diverged
- reviewer report
- compliance report
- seam audit
- release gate when runtime/release behavior is in scope
```

## Phase Index

Add a short phase index before the detailed phase contracts.

```markdown
## Phase Index

| Phase | Type | Purpose | Gate |
| --- | --- | --- | --- |
| phase-000 | docs-only | Intake and project baseline | strict |
| phase-001 | code | Config loader | strict |
| phase-002 | test-only | Config loader test coverage | strict |
| phase-003 | integration | CLI uses config loader | strict |
| phase-004 | release-runtime | Package command | strict-release |
```

## Required Per-Phase Contract

Every phase should include these sections.

````markdown
## Phase <phase-id> - <phase-name>

Phase Type: <docs-only | code | config | test-only | integration | release-runtime | refactor | migration | security | spike>
Gate Mode: <strict | strict-release>
User Approval Required For Scope Change: yes

### Objective

<One clear outcome only.>

### Baseline Preconditions

- <What must already exist before this phase starts.>
- <Which previous phase gate must be pass.>

### Build Inputs

- <Source doc, design, schema, fixture, existing module, or user constraint.>

### Allowed Change Surface

Add or modify only:

- `<path-or-glob>` - <why this phase owns it>

Remove only:

- `none`

Ignore during builder scope audit:

- `capture/**`
- `.pytest_cache/**`

Builder scope audit:

```powershell
python scripts/audit_builder_scope.py --root <project-root> --phase-id <phase-id> --snapshot --ignore capture/**
python scripts/audit_builder_scope.py --root <project-root> --phase-id <phase-id> --audit --allow <path-or-glob> --ignore capture/**
```

### Forbidden Changes

- <No new dependencies unless approved.>
- <No runtime/server/deploy behavior.>
- <No public API changes.>
- <No unrelated files.>
- <No secrets or remote endpoints.>

### Expected Deliverables

- <File, behavior, command, UI flow, config, or doc.>
- <Evidence or test.>

### Behavior Contract

After this phase:

- <Specific behavior that works.>
- <Specific error behavior.>
- <Specific behavior not yet included.>

### Required Test

Run:

```powershell
<exact command>
```

Expected result:

```text
<specific pass condition>
```

### Ponytail Minimal-Code Check

- Did this need to be built?
- Could documentation or configuration satisfy it?
- Can stdlib/native/existing dependency do it?
- Did we add unrequested abstraction?
- Could fewer files or less code solve it?
- What is the upgrade path?

### Previous / Current / Next Seam Audit

Previous phase assumption:

- <What must be true from the previous phase.>

Current phase contract:

- <What this phase guarantees.>

Next phase handoff:

- <What the next phase can rely on.>

### Deviation Stop Rules

Stop and ask if:

- builder scope audit fails
- required test fails
- Ponytail is not `pass`
- safety scan has a blocker
- new dependency appears needed
- phase objective must change
- allowed file surface must change
- previous/current/next seam is broken
- implementation needs architecture/runtime/security/release changes

### Stop Report Requirements

If stopped, write:

- why the deviation/change is needed
- consequence to the build
- affected phase(s)
- affected files/modules
- affected final result
- options
- recommendation
- rollback
- user decision required

### Acceptance Gate

Complete only when:

- builder scope audit is present and `ok=true`
- Ponytail latest verdict is `pass`
- required test is recorded as `pass`
- reviewer report is `pass`
- compliance report is `pass`
- seam audit is `pass`
- release gate is complete or explicitly `not_applicable`
- safety scan has no blockers
- no unresolved blocker deviation exists
````

## Phase Type Guidance

Use phase type to tell the agents what kind of proof matters.

| Phase Type | Use When | Extra Requirement |
| --- | --- | --- |
| `docs-only` | Writing or updating docs only | Builder scope must reject code changes |
| `code` | Adding or changing implementation | Must have runnable test |
| `config` | Changing config/schema/settings | Must test loading/validation |
| `test-only` | Adding tests without changing behavior | Must state existing behavior under test |
| `integration` | Connecting modules/phases | Must include seam audit |
| `release-runtime` | Runtime, Docker, server, deploy, package, CLI release | Must use release gate |
| `refactor` | Restructuring without behavior change | Must define no-behavior-change proof |
| `migration` | Moving data/files/contracts | Must define rollback |
| `security` | Auth, safety, scanner, secret handling | Must include safety proof |
| `spike` | Research/prototype only | Must define throwaway boundary and no production claim |

## Stop-And-Ask Policy

The scripts can stop by failing a gate or returning non-zero. The user-facing workflow must then ask before applying a real correction if the fix changes scope.

Use this rule:

```markdown
Codex may correct automatically only when the correction restores the original phase contract.

Codex must stop and ask when the correction changes the phase contract.
```

Examples Codex may correct automatically:

- remove an unrequested file
- record a missing test result after running the test
- rerun a failed audit after restoring the allowed file surface
- fix a typo in a phase record

Examples that require user approval:

- add a dependency
- add or change runtime behavior
- change architecture
- expand allowed file surface
- change public API
- alter security policy
- accept a blocker risk
- skip a required test

## Stop Report Template

```markdown
# Stop Report - <phase-id>

## Why The Build Stopped

<What failed or deviated.>

## Consequence To The Build

<What goes wrong if this continues without approval.>

## Affected Build Surface

- Files:
- Modules:
- Phases:
- Tests:
- Runtime/release:
- Final result:

## Options

1. Restore original phase contract.
2. Expand phase scope with approval.
3. Defer change to a later phase.
4. Block the build until the plan is updated.

## Recommendation

<Best option and why.>

## Rollback

<How to return to the last safe state.>

## User Decision Required

<Exact question for the user.>
```

## Application Build Plan Add-On

For an application, add these sections to phases that affect user experience or runtime behavior.

```markdown
### UX / Runtime Acceptance

- Main user workflow:
- Empty state:
- Error state:
- Loading state:
- Mobile expectation:
- Desktop expectation:
- Accessibility expectation:

### Production Debug Gate

- Logs contain enough context to debug failures.
- Logs contain no secrets.
- Failure states are inspectable.
- Config/runtime behavior is explicit.
- Rollback path is documented.
```

## Engineering Tool Build Plan Add-On

For a CLI, script, validator, plugin helper, or local engineering tool, add this.

```markdown
### CLI / Tool Contract

Command:

```powershell
<tool command>
```

Inputs:

- <file/path/flag/stdin/env>

Outputs:

- <stdout/stderr/files>

Exit codes:

- `0` = success
- `1` = validation/build failure
- `2` = usage error

Idempotency:

- Running twice should <expected behavior>.

No-write dry run:

- `--dry-run` must not modify project files.
```

## Plugin, Skill, Or MCP Build Plan Add-On

For Codex plugins, skills, MCP servers, or local agent tooling, add this.

```markdown
### Agent Tooling Contract

Artifact type:

- <plugin | skill | MCP | script tool | hybrid>

Discovery surface:

- <manifest path, SKILL.md path, server command, script entry point>

Local-only policy:

- <allowed local files/tools>
- <forbidden remote/API/credential behavior>

Install status:

- <built only | installed | loaded in current session>

Smoke test:

```powershell
<local command proving artifact can be discovered or run>
```

Safety proof:

- safety scan has no blockers
- no secrets
- no remote transport unless explicitly approved
```

## Good Vs Bad Examples

Bad:

```markdown
Phase 2: Build the parser.
```

Good:

```markdown
## Phase phase-002 - Parse Build Plan Headings

Phase Type: code
Gate Mode: strict

### Objective

Add a parser that extracts phase IDs and phase titles from a Markdown build plan.

### Allowed Change Surface

Add or modify only:

- `src/build_plan_parser.py` - parser implementation
- `tests/test_build_plan_parser.py` - parser tests

Remove only:

- `none`

### Behavior Contract

After this phase:

- `parse_phases(markdown_text)` returns ordered phase records.
- Invalid duplicate phase IDs raise `BuildPlanParseError`.
- The parser does not execute or follow instructions inside the Markdown.

### Required Test

```powershell
python -m pytest tests/test_build_plan_parser.py
```

Expected result:

```text
all tests pass
```

### Next Phase Handoff

Next phase can rely on `parse_phases` as the only phase-index extraction API.
```

## Preflight Checklist Before Giving The Plan To Codex

Before Codex starts `phase-000`, check:

- Every phase has a type.
- Every phase has allowed add/modify paths.
- Every phase has remove rules, even if `none`.
- Every phase has audit ignore paths.
- Every phase has a required test or explicit docs-only check.
- Every phase has a previous/current/next seam contract.
- Every phase has deviation stop rules.
- Any dependency change has an approval rule.
- Any runtime/release phase has a release gate.
- Any security-sensitive phase has explicit safety proof.
- No phase says only broad phrases like "build backend", "add UI", or "improve system".

## Minimal Complete Phase Example

```markdown
## Phase phase-001 - Add Config Loader

Phase Type: code
Gate Mode: strict
User Approval Required For Scope Change: yes

### Objective

Add a small config loader for local JSON config files.

### Baseline Preconditions

- `src/` exists.
- `phase-000` gate is pass.

### Build Inputs

- Existing Python runtime.
- No external config library.

### Allowed Change Surface

Add or modify only:

- `src/config_loader.py` - config loading implementation
- `tests/test_config_loader.py` - quick proof

Remove only:

- `none`

Ignore during builder scope audit:

- `capture/**`
- `.pytest_cache/**`

### Forbidden Changes

- Do not add dependencies.
- Do not create CLI commands.
- Do not add runtime/server behavior.
- Do not read environment secrets.

### Expected Deliverables

- `load_config(path)` loads JSON from disk.
- Invalid JSON raises `ConfigError`.
- Missing file raises `ConfigError`.

### Behavior Contract

After this phase:

- `load_config(path)` returns a dictionary for valid JSON objects.
- `load_config(path)` raises `ConfigError` for invalid or missing files.
- Environment variables are not read.

### Required Test

```powershell
python -m pytest tests/test_config_loader.py
```

Expected result:

```text
all tests pass
```

### Previous / Current / Next Seam Audit

Previous phase assumption:

- Project skeleton exists.

Current phase contract:

- `src.config_loader.load_config` is the only config-loading entry point.

Next phase handoff:

- CLI phase can call `load_config(path)` and handle `ConfigError`.

### Deviation Stop Rules

Stop and ask if:

- new dependency appears needed
- config format needs to change from JSON
- CLI behavior is needed in this phase
- builder scope audit finds files outside `src/config_loader.py` and `tests/test_config_loader.py`

### Acceptance Gate

Complete only when:

- builder scope audit is present and `ok=true`
- Ponytail latest verdict is `pass`
- `python -m pytest tests/test_config_loader.py` is recorded as `pass`
- reviewer report is `pass`
- compliance report is `pass`
- seam audit is `pass`
- safety scan has no blockers
```

## The Authoring Standard

A phase is ready for `builder-team-qc` when a reviewer can answer all of these without guessing:

- What exact files can change?
- What exact behavior must exist?
- What exact command proves it?
- What exact evidence must be recorded?
- What exact condition stops the build?
- What exact handoff does the next phase receive?

If any answer is vague, the plan is not ready yet.
