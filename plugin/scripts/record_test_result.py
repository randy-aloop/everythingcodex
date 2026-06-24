from __future__ import annotations

import argparse
import json

from builder_team_qc_lib import append_jsonl, phase_id_arg, qc_path, root_path, utc_now


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a phase test result.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    parser.add_argument("--name", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--status", required=True, choices=["pass", "fail", "skipped"])
    parser.add_argument("--exit-code", type=int, default=None)
    parser.add_argument("--output-file", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    root = root_path(args.root)
    record = {
        "timestamp": utc_now(),
        "phase_id": args.phase_id,
        "name": args.name,
        "command": args.command,
        "status": args.status,
        "exit_code": args.exit_code,
        "output_file": args.output_file,
        "notes": args.notes,
    }
    append_jsonl(qc_path(root) / "test-results" / f"{args.phase_id}.jsonl", record)
    report = qc_path(root) / "phase-runs" / args.phase_id / "test-report.md"
    if report.exists():
        with report.open("a", encoding="utf-8") as handle:
            handle.write("\n## Recorded Check\n\n")
            handle.write("```json\n")
            handle.write(json.dumps(record, indent=2, ensure_ascii=True))
            handle.write("\n```\n")
    print("recorded test result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
