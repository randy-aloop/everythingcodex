from __future__ import annotations

import argparse

from builder_team_qc_lib import append_jsonl, phase_id_arg, qc_path, root_path, utc_now


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a build-plan deviation.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--severity", required=True, choices=["low", "medium", "high", "blocker"])
    parser.add_argument("--resolution", default="")
    parser.add_argument("--accepted-by-user", action="store_true")
    args = parser.parse_args()

    append_jsonl(
        qc_path(root_path(args.root)) / "deviation-log.jsonl",
        {
            "timestamp": utc_now(),
            "phase_id": args.phase_id,
            "expected": args.expected,
            "actual": args.actual,
            "severity": args.severity,
            "resolution": args.resolution,
            "accepted_by_user": bool(args.accepted_by_user),
        },
    )
    print("recorded deviation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
