from __future__ import annotations

import argparse

from builder_team_qc_lib import ensure_qc, root_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a project-local .qc hierarchy.")
    parser.add_argument("--root", default=None, help="Target project root. Defaults to cwd.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing.")
    parser.add_argument("--force-templates", action="store_true", help="Overwrite existing .qc templates.")
    args = parser.parse_args()

    root = root_path(args.root)
    actions = ensure_qc(root, dry_run=args.dry_run, force_templates=args.force_templates)
    for action in actions:
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
