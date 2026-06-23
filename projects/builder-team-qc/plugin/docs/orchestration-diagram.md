# Orchestration Diagram

Version: V02
Updated: 2026-06-23
Supersedes: V01

This diagram shows how `builder-team-qc` runs a phase-controlled multiagent Ponytail build in V01.

The important correction: `ponytail-adapter` is not owned by `test-agent`. Ponytail checks the builder output and contributes gate evidence for the controller, reviewer, and compliance roles. Tests run after Ponytail passes because testing an over-scoped or over-abstracted change is usually wasted work.

V01 uses logical fan-out, not true concurrent agents. Codex executes each role pass sequentially unless a future runtime adds real concurrency.

## System View

```mermaid
flowchart TD
    U["User request"] --> C["Codex conversation"]
    C --> P["builder-team-qc plugin"]
    P --> PC["phase-controller"]

    PC --> PLAN["Read build plan"]
    PLAN --> PRE["Pre-build plan check"]
    PRE --> READY{"Phase ready?"}
    READY -- "no" --> ISSUE["Open blocker in issue-register.jsonl"]
    ISSUE --> STOP
    READY -- "yes" --> INIT["Initialize .qc"]
    INIT --> START["Start phase record"]
    START --> META["Set release_required and max_revise_attempts"]
    META --> B["builder-agent creates candidate change"]
    B --> DIFF["Persist changed-files.json and implementation-diff.patch"]

    DIFF --> PT["ponytail-adapter checks scope and minimal-code discipline"]
    PT --> PTG{"Ponytail verdict"}

    PTG -- "pass" --> FAN["Evidence check fan-out"]
    PTG -- "revise" --> GATE
    PTG -- "block" --> GATE

    FAN --> T["test-agent"]
    FAN --> R["reviewer-agent"]
    FAN --> CMP["compliance-agent"]
    FAN --> I["integration-agent"]
    FAN --> REL{"Runtime or release phase?"}

    REL -- "yes" --> RA["release-agent"]
    REL -- "no" --> JOIN["Evidence join"]

    T --> JOIN
    R --> JOIN
    CMP --> JOIN
    I --> JOIN
    RA --> JOIN

    JOIN --> V1["Validate in-progress"]
    V1 --> V2["Validate strict gate, release-aware when required"]
    V2 --> GATE{"Gate decision"}

    GATE -- "pass" --> SUMMARY["Write gate-summary.md"]
    SUMMARY --> BOARD["Record final phase-board transition"]
    BOARD --> NEXT["Allow next phase"]
    GATE -- "revise" --> CAP{"Revise attempts < 3?"}
    CAP -- "yes" --> FIX["Fix smallest failing item"]
    FIX --> B
    CAP -- "no" --> STOP
    GATE -- "block" --> STOP["Stop and report blocker"]
    GATE -- "accepted_with_risk" --> RISK["Record human decision-log entry"]
    RISK --> SUMMARY
```

## Evidence Responsibility View

```mermaid
flowchart LR
    B["builder-agent"] --> CHANGE["Candidate implementation"]
    CHANGE --> DIFF["changed-files.json + implementation-diff.patch"]
    DIFF --> PT["ponytail-adapter"]
    PT --> PONY["ponytail-events.jsonl"]

    PONY --> PC["phase-controller"]
    PONY --> R["reviewer-agent"]
    PONY --> CMP["compliance-agent"]

    DIFF --> T["test-agent"]
    DIFF --> R
    DIFF --> I["integration-agent"]
    CHANGE --> REL{"Release relevant?"}
    REL -- "yes" --> RA["release-agent"]

    T --> TESTS["test-results/{phase-id}.jsonl"]
    R --> REVIEW["reviewer-report.md"]
    CMP --> COMP["compliance-report.md"]
    CMP --> ISSUES["issue-register.jsonl"]
    I --> SEAM["seam-audit.md"]
    RA --> RELEASE["release-gate.md"]
    PC --> DECISION["decision-log.jsonl when accepted risk"]
    PC --> SUMMARY["gate-summary.md"]
    PC --> BOARD["phase-board.json final gate"]

    PONY --> STRICT["strict gate"]
    TESTS --> STRICT
    REVIEW --> STRICT
    COMP --> STRICT
    ISSUES --> STRICT
    SEAM --> STRICT
    RELEASE --> STRICT
    DECISION --> STRICT
    SUMMARY --> BOARD
    STRICT --> BOARD

    STRICT --> OUT{"pass / revise / block / accepted_with_risk"}
```

Strict gate requires `pass` verdicts for required role reports. `revise`, `block`, missing or conflicting verdicts, open blocker issues, only skipped required tests, or release phases with `release-gate.md` still `not_applicable` must not pass without a matching human accepted-risk record. When release is not required, `not_applicable` still needs a written rationale.

## Shared State View

```mermaid
flowchart LR
    subgraph ROLES["Role skills"]
        B["builder-agent"]
        PT["ponytail-adapter"]
        T["test-agent"]
        R["reviewer-agent"]
        C["compliance-agent"]
        I["integration-agent"]
        RA["release-agent"]
    end

    subgraph QC[".qc shared state"]
        BOARD["phase-board.json"]
        PHASE["phase-runs/{phase-id}/"]
        TESTS["test-results/{phase-id}.jsonl"]
        PONY["ponytail-events.jsonl"]
        ISSUES["issue-register.jsonl"]
        DEV["deviation-log.jsonl"]
        DEC["decision-log.jsonl"]
        LESSONS["lessons-learned.jsonl"]
    end

    B --> PHASE
    PT --> PONY
    T --> TESTS
    R --> PHASE
    C --> PHASE
    C --> ISSUES
    C --> DEV
    C --> DEC
    I --> PHASE
    RA --> PHASE
    PC --> BOARD
    PC --> DEC
    PC --> LESSONS

    BOARD --> PC["phase-controller"]
    PHASE --> PC
    TESTS --> PC
    PONY --> PC
    ISSUES --> PC
    DEV --> PC
    DEC --> PC
    LESSONS --> PC

    PONY --> R
    PONY --> C

    PC --> G{"strict gate"}
    G --> BOARD
```

## ADK-Style Pattern View

```mermaid
flowchart TD
    ROOT["Root controller: phase-controller"] --> LOOP["LoopAgent pattern: bounded revise loop"]
    LOOP --> SEQ["SequentialAgent pattern: phase pipeline"]

    SEQ --> PRE["Pre-build plan check"]
    PRE --> OPEN["Open phase"]
    OPEN --> BUILD["Builder creates candidate change"]
    BUILD --> DIFF["Persist diff evidence"]
    DIFF --> PONY["Ponytail minimal-code gate"]
    PONY --> PASS{"Ponytail pass?"}

    PASS -- "yes" --> PAR["Logical fan-out: sequential in V01"]
    PASS -- "no" --> GATE["Strict gate validator"]

    subgraph CHECKS["Evidence checks"]
        REV["Reviewer"]
        TEST["Test"]
        COMP["Compliance"]
        SEAM["Seam audit"]
        RELEASE["Release when applicable"]
    end

    PAR --> REV
    PAR --> TEST
    PAR --> COMP
    PAR --> SEAM
    PAR --> RELEASE

    REV --> GATE
    TEST --> GATE
    COMP --> GATE
    SEAM --> GATE
    RELEASE --> GATE

    GATE --> GPASS{"Phase pass?"}
    GPASS -- "yes" --> DONE["Complete phase"]
    GPASS -- "no" --> CAP{"Attempts < 3?"}
    CAP -- "yes" --> LOOP
    CAP -- "no" --> BLOCK["Block or require human accepted-risk decision"]
```
