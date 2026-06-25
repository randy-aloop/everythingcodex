# Builder Team QC Prototype Archive

Version: `0.1.0-prototype`
Created: 2026-06-24
Status: historical reference package

This folder captures the prototype-era conversation, build process, decision logic, prompt processing, code/build artifact map, and future handoff for Builder Team QC.

It is not a raw hidden reasoning dump. It is a curated engineering record: what was asked, what was produced, what decisions were made, what gates were added, what risks were found, and why the project should advance through `0.2.0-trial` before alpha or beta.

## Contents

| File | Purpose |
| --- | --- |
| `01-chronological-thread-record.md` | Chronological input/output record for the thread. |
| `02-work-process-and-decision-logic.md` | Curated process logic, decisions, constraints, and verification approach. |
| `03-prompt-processing-record.md` | How user prompts were interpreted into build actions and artifacts. |
| `04-code-build-artifact-map.md` | Code, script, docs, web, deck, repo, and gate artifact map. |
| `05-version-rationale.md` | Why this package is `0.1.0-prototype`, not alpha or beta. |
| `06-handoff-to-0.2.0-trial.md` | Recommended next-phase plan for `0.2.0-trial`. |

## Prototype Definition

`0.1.0-prototype` means:

```text
The design, docs, plugin skeleton, role model, .qc schema direction, and local scripts exist.
Some code/docs gaps remain.
The system has not yet completed a clean real local build trial end-to-end.
```

The next intended version is:

```text
0.2.0-trial
```

Trial means the project starts proving the system on a real local target, while still accepting known gaps and rough edges.
