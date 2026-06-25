from __future__ import annotations

import argparse
from pathlib import Path

from builder_team_qc_lib import (
    append_jsonl,
    evidence_dir,
    file_sha256,
    phase_artifact_path,
    phase_id_arg,
    qc_path,
    read_builder_scope_audit,
    root_path,
    utc_now,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Ponytail/minimal-code evidence.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", required=True, type=phase_id_arg)
    parser.add_argument("--mode", required=True, choices=["task-scoped", "project-agents", "contained-workspace", "unavailable-fallback"])
    parser.add_argument("--mode-source", default="controller", choices=["controller", "project-instructions", "contained-workspace", "manual-fallback"])
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--checklist-version", default="local-v1")
    parser.add_argument("--yagni-check", required=True)
    parser.add_argument("--yagni-status", default="pass", choices=["pass", "revise", "block"])
    parser.add_argument("--stdlib-check", required=True)
    parser.add_argument("--stdlib-status", default="pass", choices=["pass", "revise", "block"])
    parser.add_argument("--dependency-check", required=True)
    parser.add_argument("--dependency-status", default="pass", choices=["pass", "revise", "block"])
    parser.add_argument("--abstraction-check", required=True)
    parser.add_argument("--abstraction-status", default="pass", choices=["pass", "revise", "block"])
    parser.add_argument("--minimum-code-verdict", required=True, choices=["pass", "revise", "block"])
    parser.add_argument("--changed-files", default="")
    parser.add_argument("--implementation-diff", default="")
    parser.add_argument("--upstream-hook-enabled", action="store_true")
    parser.add_argument("--upstream-hook-review-id", default="")
    parser.add_argument("--upstream-ponytail-version", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    root = root_path(args.root)
    subcheck_statuses = [
        args.yagni_status,
        args.stdlib_status,
        args.dependency_status,
        args.abstraction_status,
    ]
    if args.minimum_code_verdict == "pass" and any(status != "pass" for status in subcheck_statuses):
        print("error: minimum-code pass requires every Ponytail subcheck status to pass")
        return 2
    if args.upstream_hook_enabled and not args.upstream_hook_review_id:
        print("error: upstream hook mode requires --upstream-hook-review-id")
        return 2
    if args.mode == "unavailable-fallback" and args.mode_source != "manual-fallback":
        print("error: unavailable-fallback mode requires --mode-source manual-fallback")
        return 2

    def artifact_path(value: str, default_name: str) -> Path:
        if not value:
            return phase_artifact_path(root, args.phase_id, default_name)
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        return path.resolve()

    def project_rel(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            return str(path)

    changed_files_path = artifact_path(args.changed_files, "changed-files.json")
    diff_path = artifact_path(args.implementation_diff, "implementation-diff.patch")
    scope_audit = read_builder_scope_audit(root, args.phase_id)
    scope_audit_path = evidence_dir(root, args.phase_id) / "builder-scope-audit.json"
    record = {
        "timestamp": utc_now(),
        "phase_id": args.phase_id,
        "attempt": args.attempt,
        "mode": args.mode,
        "mode_source": args.mode_source,
        "checklist_version": args.checklist_version,
        "upstream_hook_enabled": bool(args.upstream_hook_enabled),
        "upstream_hook_review_id": args.upstream_hook_review_id,
        "upstream_ponytail_version": args.upstream_ponytail_version,
        "yagni_check": args.yagni_check,
        "yagni_status": args.yagni_status,
        "stdlib_check": args.stdlib_check,
        "stdlib_status": args.stdlib_status,
        "dependency_check": args.dependency_check,
        "dependency_status": args.dependency_status,
        "abstraction_check": args.abstraction_check,
        "abstraction_status": args.abstraction_status,
        "minimum_code_verdict": args.minimum_code_verdict,
        "changed_files_path": project_rel(changed_files_path) if changed_files_path.exists() else "",
        "changed_files_hash": file_sha256(changed_files_path) if changed_files_path.exists() else "",
        "implementation_diff_path": project_rel(diff_path) if diff_path.exists() else "",
        "implementation_diff_hash": file_sha256(diff_path) if diff_path.exists() else "",
        "builder_scope_audit_id": scope_audit.get("created_at", "") if scope_audit else "",
        "builder_scope_audit_hash": file_sha256(scope_audit_path) if scope_audit_path.exists() else "",
        "notes": args.notes,
    }
    append_jsonl(qc_path(root) / "ponytail-events.jsonl", record)
    print("recorded ponytail check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
