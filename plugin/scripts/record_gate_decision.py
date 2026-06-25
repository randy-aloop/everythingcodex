from __future__ import annotations

import argparse
import json

from builder_team_qc_lib import (
    GATE_TO_STATUS,
    append_gate_summary,
    append_jsonl,
    decision_exists,
    phase_id_arg,
    qc_path,
    read_phase_board,
    read_qc_config,
    root_path,
    update_phase_record_gate,
    utc_now,
    write_phase_board,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a builder-team QC final gate decision.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    parser.add_argument("--gate", required=True, choices=["pass", "revise", "block", "accepted_with_risk"])
    parser.add_argument("--next-phase-id", default="")
    parser.add_argument("--decision-id", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = root_path(args.root)
    board = read_phase_board(root)
    config = read_qc_config(root)
    max_revise = int(board.get("max_revise_attempts") or config.get("default_max_revise_attempts", 3) or 3)
    gate = args.gate
    status = GATE_TO_STATUS[gate]
    exit_code = 0

    if gate == "accepted_with_risk" and not decision_exists(root, args.phase_id, args.decision_id, "accepted_with_risk"):
        print("error: accepted_with_risk requires matching decision-log entry")
        return 10

    revise_attempts = int(board.get("revise_attempts") or 0)
    requested_gate = gate
    if gate == "revise":
        next_attempt = revise_attempts + 1
        if next_attempt >= max_revise:
            gate = "block"
            status = GATE_TO_STATUS[gate]
            revise_attempts = next_attempt
            exit_code = 10
        else:
            revise_attempts = next_attempt
    elif gate in {"pass", "accepted_with_risk"}:
        revise_attempts = 0

    timestamp = utc_now()
    board.update(
        {
            "current_phase_id": args.phase_id,
            "current_phase_status": status,
            "latest_gate_decision": gate,
            "latest_gate_at": timestamp,
            "last_gate_at": timestamp,
            "revise_attempts": revise_attempts,
            "max_revise_attempts": max_revise,
            "accepted_risk_decision_id": args.decision_id if gate == "accepted_with_risk" else "",
        }
    )
    if args.next_phase_id:
        board["next_phase_id"] = args.next_phase_id
    write_phase_board(root, board)

    record = {
        "timestamp": timestamp,
        "phase_id": args.phase_id,
        "requested_gate": requested_gate,
        "gate": gate,
        "status": status,
        "revise_attempts": revise_attempts,
        "max_revise_attempts": max_revise,
        "decision_id": args.decision_id,
        "next_phase_id": board.get("next_phase_id", ""),
        "note": args.note,
    }
    append_jsonl(qc_path(root) / "gate-events.jsonl", record)
    update_phase_record_gate(root, args.phase_id, gate, status, args.note)
    append_gate_summary(root, args.phase_id, record)

    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=True))
    elif exit_code:
        print(f"gate revise cap reached; recorded block for phase {args.phase_id}")
    else:
        print(f"recorded gate decision {gate} for phase {args.phase_id}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
