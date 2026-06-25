from __future__ import annotations

import argparse

from builder_team_qc_lib import phase_id_arg, root_path, start_phase


def main() -> int:
    parser = argparse.ArgumentParser(description="Open or resume a builder-team QC phase.")
    parser.add_argument("--root", default=None, help="Target project root. Defaults to cwd.")
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    parser.add_argument("--title", required=True)
    parser.add_argument("--next-phase-id", default="")
    parser.add_argument("--build-plan", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Override non-terminal phase-board guard.")
    args = parser.parse_args()

    try:
        run_dir = start_phase(
            root_path(args.root),
            phase_id=args.phase_id,
            title=args.title,
            next_phase_id=args.next_phase_id,
            build_plan=args.build_plan,
            dry_run=args.dry_run,
            force=args.force,
        )
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 10
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
