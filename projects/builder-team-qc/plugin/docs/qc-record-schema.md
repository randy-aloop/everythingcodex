# QC Record Schema

`.qc/phase-board.json` tracks current phase state.

`.qc/ponytail-events.jsonl` records minimal-code evidence.

`.qc/deviation-log.jsonl` records build-plan mismatches.

`.qc/test-results/<phase-id>.jsonl` records checks.

`.qc/phase-runs/<phase-id>/` stores human-readable role reports and evidence.

Records are local files. Do not store secrets, tokens, API keys, OAuth files, or credentials.
