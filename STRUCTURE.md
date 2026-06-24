# Builder Team QC Folder Structure

```text
./
  README.md
  MASTER.md
  VERSION
  project.json
  STRUCTURE.md
  CHANGELOG.md
  plugin/
    .codex-plugin/
      plugin.json
    assets/
      qc-templates/
    docs/
    scripts/
    skills/
      phase-controller/
      builder-agent/
      ponytail-adapter/
      test-agent/
      reviewer-agent/
      compliance-agent/
      integration-agent/
      release-agent/
  site/
    index.html
```

## Folder Responsibilities

| Path | Responsibility |
| --- | --- |
| `README.md` | Human entry point and quick start. |
| `MASTER.md` | Canonical project map, role contracts, promotion checklist, version policy. |
| `VERSION` | Current project version string. |
| `project.json` | Machine-readable project metadata. |
| `plugin/` | Codex plugin/process package. |
| `plugin/docs/` | Operational docs and orchestration diagrams. |
| `plugin/scripts/` | Local helper scripts for `.qc` initialization, evidence recording, validation, and summaries. |
| `plugin/skills/` | Codex role skills. |
| `plugin/assets/qc-templates/` | Reusable `.qc` evidence templates. |
| `site/` | Static article page for explaining the system. |

## Versioned Promotion Targets

| Version | Target |
| --- | --- |
| `0.1.0-planning` | Local package and docs are organized. |
| `0.2.0-trial` | Sample project demonstrates pass/revise/pass cycle. |
| `0.3.0-plugin-mvp` | Plugin ready for repeated local use. |
| `1.0.0` | Stable reusable workflow with validation and trial evidence. |
