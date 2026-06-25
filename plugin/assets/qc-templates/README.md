# Builder Team QC Templates

Copy these templates into each target project's `.qc/` folder with `scripts/init_qc.py`.

Required phase evidence:

- phase record
- builder notes
- changed-files.json
- implementation-diff.patch
- reviewer report
- test report
- compliance report
- seam audit
- release gate or explicit `not_applicable`
- Ponytail event in `.qc/ponytail-events.jsonl`
- builder scope baseline and audit under `.qc/phase-runs/<phase-id>/evidence/`
- deviation log, even if empty
- issue register, decision log, and gate-events log, even if empty
