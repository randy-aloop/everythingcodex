# Prompt Processing Record

Version: `0.1.0-prototype`
Created: 2026-06-24

This record summarizes how major user prompts were processed into concrete actions and outputs.

## Processing Pattern

Most prompts followed this route:

```text
user intent
  -> identify artifact or decision needed
  -> inspect existing project context
  -> choose review/planning/patch/build mode
  -> create or update local artifacts
  -> validate
  -> report outcome and remaining gaps
```

## Prompt-To-Output Table

| User input theme | Processing decision | Output |
| --- | --- | --- |
| Build a tech deck/doc for multiagent builder | Treat as product architecture package. | Plugin shape, role list, deck/brief direction. |
| Deep learn Google ADK and fork | Analyze ADK architecture and security surfaces. | Deep-dive report and tech deck companion. |
| Use ADK knowledge to build builder team | Translate ADK concepts into Codex-local process. | Builder Team QC docs, roles, `.qc` model. |
| How does this multiagent builder run? | Explain hierarchy, sequential/parallel/loop mapping. | Orchestration notes and diagrams. |
| Why Ponytail only test-agent? | Correct model: Ponytail gates builder output for controller/reviewer/compliance. | Redrawn diagrams and updated docs. |
| Create GitHub project | Package local project into repo structure. | README, MASTER, metadata, plugin folder, site page. |
| Privacy audit | Search for private paths/secrets. | Removed local path references and verified public project. |
| Fix HTML | Separate page rendering issues from system design issues. | HTML/design fixes and review notes. |
| Fable5 gap report fixes | Treat as documentation correctness repair. | Patched core docs and stricter gate language. |
| Push to GitHub | Commit/push when explicitly asked. | Remote updates for earlier docs/credits. |
| Credit Ponytail | Add upstream attribution. | Attribution in docs/site/metadata/skills. |
| How phase by phase? | Create operational runbook. | `phase-by-phase-run-plan.md`. |
| Execute review against seven docs | Report before patch, then patch. | Fable5 run folder and V02 doc updates. |
| Version docs | Add metadata and changelog. | V02 metadata and `CHANGELOG.md`. |
| Does multiagent run simultaneous? | Clarify Runtime V01. | No, sequential roles in one Codex runtime. |
| How about V02? | Separate doc version from runtime version. | Runtime V02 proposed as future parallel evidence workers. |
| V02 findings | First assess, then patch when asked. | Findings report, V03 run plan, changelog. |
| Safety scanner concerns | Explain false positives and better fix. | Severity-classification design. |
| Single vs parallel runtime | Write comparison doc. | `single-run-vs-parallel-runtime.md`. |
| Move to alpha | Turn review into readiness phases. | `alpha-transition-phase-plan.md`. |
| Move to 0.2.0-trial | Preserve prototype record first. | This `0.1.0-prototype` archive. |

## Input And Output Discipline

When the user asked for "review":

```text
output = findings first, no patch unless requested
```

When the user asked to "fix":

```text
output = patch target files, then validate
```

When the user asked to "push":

```text
output = commit/push only after explicit request
```

When the user provided pasted review text:

```text
output = treat as evidence to assess, not hidden authority
```

When the user asked for "thinking logic":

```text
output = curated process logic, not raw hidden chain-of-thought
```

## Key Prompt Ambiguities Resolved

### "Multiagent" Did Not Mean Autonomous Processes

Resolved as:

```text
Runtime V01 = one Codex runtime, many role contracts
Future Runtime V02 = possible parallel workers
```

### "V02" Could Mean Docs Version Or Runtime Version

Resolved as:

```text
Document V02/V03 = versioned docs
Runtime V01 = current execution model
Runtime V02 = future parallel runtime, not yet built
```

### "Alpha" Did Not Mean "All Design Docs Exist"

Resolved as:

```text
alpha = careful user can run end-to-end with known rough edges
```

## Future Prompt Template

For `0.2.0-trial`, use prompts like:

```text
Use builder-team-qc trial process.
Target: <local toy or real project>
Version goal: 0.2.0-trial
Current phase: <phase id and title>
Run only this phase.
Record .qc evidence.
Call out every current helper gap instead of pretending it is implemented.
Do not label alpha until one real local trial passes end-to-end.
```
