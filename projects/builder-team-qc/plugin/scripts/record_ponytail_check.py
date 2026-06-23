from __future__ import annotations

import argparse

from builder_team_qc_lib import append_jsonl, phase_id_arg, qc_path, root_path, utc_now


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Ponytail/minimal-code evidence.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    parser.add_argument("--mode", required=True, choices=["task-scoped", "project-agents", "contained-workspace", "unavailable-fallback"])
    parser.add_argument("--yagni-check", required=True)
    parser.add_argument("--stdlib-check", required=True)
    parser.add_argument("--dependency-check", required=True)
    parser.add_argument("--abstraction-check", required=True)
    parser.add_argument("--minimum-code-verdict", required=True, choices=["pass", "revise", "block"])
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    root = root_path(args.root)
    record = {
        "timestamp": utc_now(),
        "phase_id": args.phase_id,
        "mode": args.mode,
        "yagni_check": args.yagni_check,
        "stdlib_check": args.stdlib_check,
        "dependency_check": args.dependency_check,
        "abstraction_check": args.abstraction_check,
        "minimum_code_verdict": args.minimum_code_verdict,
        "notes": args.notes,
    }
    append_jsonl(qc_path(root) / "ponytail-events.jsonl", record)
    print("recorded ponytail check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
