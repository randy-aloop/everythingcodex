from __future__ import annotations

import argparse
import json

from builder_team_qc_lib import (
    create_builder_scope_audit,
    create_builder_scope_baseline,
    phase_id_arg,
    root_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot or audit builder-agent phase-relative file scope.")
    parser.add_argument("--root", default=None, help="Target project root. Defaults to cwd.")
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot", action="store_true", help="Record the pre-builder phase baseline.")
    mode.add_argument("--audit", action="store_true", help="Compare current files against the pre-builder baseline.")
    parser.add_argument("--allow", action="append", default=[], help="Allowed added/modified path or glob. Repeatable.")
    parser.add_argument("--allow-remove", action="append", default=[], help="Allowed removed path or glob. Repeatable.")
    parser.add_argument("--ignore", action="append", default=[], help="Ignored path or glob outside .qc/cache defaults. Repeatable.")
    parser.add_argument("--label", default="before-builder", help="Snapshot label.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    root = root_path(args.root)
    try:
        if args.snapshot:
            result = create_builder_scope_baseline(
                root,
                phase_id=args.phase_id,
                ignore_patterns=args.ignore,
                label=args.label,
            )
            ok = True
        else:
            result = create_builder_scope_audit(
                root,
                phase_id=args.phase_id,
                allow_patterns=args.allow,
                allow_remove_patterns=args.allow_remove,
                ignore_patterns=args.ignore,
            )
            ok = bool(result.get("ok"))
    except Exception as exc:  # noqa: BLE001
        result = {"ok": False, "error": str(exc), "phase_id": args.phase_id}
        ok = False

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    elif args.snapshot:
        print("builder scope baseline recorded" if ok else f"failed: {result.get('error')}")
    elif ok:
        print("builder scope audit passed")
    else:
        summary = result.get("summary", {})
        print(f"builder scope audit failed: {summary.get('unexpected', 0)} unexpected changes")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
