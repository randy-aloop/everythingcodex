from __future__ import annotations

import argparse
import json

from builder_team_qc_lib import phase_id_arg, phase_run_dir, qc_path, read_jsonl, root_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a builder-team QC phase.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    args = parser.parse_args()

    root = root_path(args.root)
    run_dir = phase_run_dir(root, args.phase_id)
    summary = {
        "phase_id": args.phase_id,
        "run_dir": str(run_dir),
        "files": sorted(p.name for p in run_dir.glob("*.md")) if run_dir.exists() else [],
        "ponytail_events": [row for row in read_jsonl(qc_path(root) / "ponytail-events.jsonl") if row.get("phase_id") == args.phase_id],
        "test_results": read_jsonl(qc_path(root) / "test-results" / f"{args.phase_id}.jsonl"),
        "deviations": [row for row in read_jsonl(qc_path(root) / "deviation-log.jsonl") if row.get("phase_id") == args.phase_id],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
