from __future__ import annotations

import argparse
import json

from builder_team_qc_lib import append_jsonl, next_record_id, phase_id_arg, qc_path, read_jsonl, root_path, utc_now


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a human decision for builder-team QC.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    parser.add_argument("--decision-id", default="")
    parser.add_argument("--decision-type", required=True, choices=["accepted_with_risk", "approval", "override", "revise_cap_change"])
    parser.add_argument("--accepted-by", required=True)
    parser.add_argument("--risk", required=True)
    parser.add_argument("--impact", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--deadline", required=True)
    parser.add_argument("--rollback", required=True)
    parser.add_argument("--follow-up", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = root_path(args.root)
    path = qc_path(root) / "decision-log.jsonl"
    rows = read_jsonl(path)
    decision_id = args.decision_id or next_record_id(rows, "decision", args.phase_id)
    if any(row.get("decision_id") == decision_id for row in rows):
        print(f"error: decision id already exists: {decision_id}")
        return 20

    record = {
        "timestamp": utc_now(),
        "decision_id": decision_id,
        "phase_id": args.phase_id,
        "decision_type": args.decision_type,
        "accepted_by": args.accepted_by,
        "risk": args.risk,
        "impact": args.impact,
        "reason": args.reason,
        "owner": args.owner,
        "deadline": args.deadline,
        "rollback": args.rollback,
        "follow_up": args.follow_up,
        "notes": args.notes,
    }
    append_jsonl(path, record)
    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=True))
    else:
        print(f"recorded decision {decision_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
