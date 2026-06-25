from __future__ import annotations

import argparse
import json

from builder_team_qc_lib import (
    REQUIRED_PHASE_FILES,
    PONYTAIL_BOUND_ARTIFACTS,
    ROLE_VERDICT_FILES,
    decision_exists,
    file_sha256,
    latest_ponytail_event,
    phase_artifact_path,
    phase_id_arg,
    phase_run_dir,
    qc_path,
    read_builder_scope_audit,
    read_phase_board,
    read_qc_config,
    read_jsonl,
    read_verdict,
    release_required_for_phase,
    root_path,
    scan_safety,
    validate_templates,
    write_phase_board,
)

EXIT_GENERAL_FAILURE = 1
EXIT_STRICT_GATE = 10
EXIT_SCHEMA = 20
EXIT_SAFETY = 30

RESOLVED_ISSUE_STATUSES = {"fixed", "resolved", "closed", "accepted_with_risk", "wont_fix"}


def is_open_blocker_issue(row: dict, phase_id: str) -> bool:
    if row.get("phase_id") not in {phase_id, "", None, "global"}:
        return False
    status = str(row.get("status", "open")).lower()
    severity = str(row.get("severity", "")).lower()
    if status in RESOLVED_ISSUE_STATUSES:
        return False
    return severity == "blocker" or status == "blocker"


def check_ponytail_binding(root, phase_id: str, event: dict, require_builder_scope: bool) -> list[str]:
    errors: list[str] = []
    for field_prefix, artifact_name in PONYTAIL_BOUND_ARTIFACTS.items():
        path = phase_artifact_path(root, phase_id, artifact_name)
        expected_hash = event.get(f"{field_prefix}_hash") or ""
        if not path.exists():
            errors.append(f"missing {artifact_name} for Ponytail diff binding")
        elif not expected_hash:
            errors.append(f"latest Ponytail event is missing {field_prefix}_hash")
        else:
            current_hash = file_sha256(path)
            if current_hash != expected_hash:
                errors.append(f"latest Ponytail event is stale for {artifact_name}")

    if require_builder_scope:
        audit_path = phase_run_dir(root, phase_id) / "evidence" / "builder-scope-audit.json"
        expected_hash = event.get("builder_scope_audit_hash") or ""
        if not audit_path.exists():
            errors.append("missing builder scope audit for Ponytail binding")
        elif not expected_hash:
            errors.append("latest Ponytail event is missing builder_scope_audit_hash")
        elif file_sha256(audit_path) != expected_hash:
            errors.append("latest Ponytail event is stale for builder scope audit")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate builder-team QC phase evidence.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", type=phase_id_arg)
    parser.add_argument("--template-only", action="store_true")
    parser.add_argument("--release-phase", action="store_true")
    parser.add_argument("--scan-safety", action="store_true")
    parser.add_argument("--require-builder-scope", action="store_true", help="Require a passing builder scope audit.")
    parser.add_argument("--strict-gate", action="store_true", help="Fail pending verdicts and missing test evidence.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    schema_errors: list[str] = []
    gate_errors: list[str] = []
    safety_errors: list[str] = []
    release_required = False

    schema_errors.extend(validate_templates())
    if not args.template_only:
        if not args.phase_id:
            schema_errors.append("--phase-id is required unless --template-only is used")
        else:
            root = root_path(args.root)
            config = read_qc_config(root)
            enforcement = config.get("enforcement", {})
            run_dir = phase_run_dir(root, args.phase_id)
            if not run_dir.exists():
                gate_errors.append(f"missing phase run directory: {run_dir}")
            for name in REQUIRED_PHASE_FILES:
                path = run_dir / name
                if not path.exists():
                    gate_errors.append(f"missing required phase file: {name}")

            if enforcement.get("enforce_role_verdicts", True):
                for name in ROLE_VERDICT_FILES:
                    verdict = read_verdict(run_dir / name)
                    if verdict != "pass":
                        message = f"{name} verdict is {verdict}, not pass"
                        if args.strict_gate:
                            gate_errors.append(message)
                        else:
                            warnings.append(message)
                phase_record_verdict = read_verdict(run_dir / "phase-record.md")
                if phase_record_verdict in {"revise", "block"}:
                    gate_errors.append(f"phase-record gate decision is {phase_record_verdict}")

            event = latest_ponytail_event(root, args.phase_id)
            if not event:
                gate_errors.append("missing ponytail event for phase")
            elif event.get("minimum_code_verdict") != "pass":
                gate_errors.append("latest ponytail event is not pass")
            elif args.strict_gate:
                subcheck_fields = [
                    "yagni_status",
                    "stdlib_status",
                    "dependency_status",
                    "abstraction_status",
                ]
                for field in subcheck_fields:
                    if event.get(field, "pass") != "pass":
                        gate_errors.append(f"latest Ponytail event has non-pass {field}")
                if event.get("upstream_hook_enabled") and not event.get("upstream_hook_review_id"):
                    gate_errors.append("upstream Ponytail hook requires review id")
                if event.get("mode") == "unavailable-fallback" and event.get("mode_source") != "manual-fallback":
                    gate_errors.append("unavailable-fallback Ponytail mode requires manual-fallback mode_source")
                if enforcement.get("require_ponytail_diff_binding", True):
                    gate_errors.extend(check_ponytail_binding(root, args.phase_id, event, args.require_builder_scope))

            tests = read_jsonl(qc_path(root) / "test-results" / f"{args.phase_id}.jsonl")
            if not tests:
                if args.strict_gate:
                    gate_errors.append("no recorded test result for phase")
                else:
                    warnings.append("no recorded test result for phase")
            elif any(row.get("status") == "fail" for row in tests):
                gate_errors.append("one or more recorded tests failed")
            elif args.strict_gate and enforcement.get("require_passing_test", True):
                latest_required: dict[str, dict] = {}
                for row in tests:
                    if row.get("required"):
                        latest_required[str(row.get("name") or row.get("command") or "<unnamed>")] = row
                required_pass_count = sum(1 for row in latest_required.values() if row.get("status") == "pass")
                if required_pass_count < int(config.get("required_test_policy", {}).get("minimum_required_passes", 1)):
                    gate_errors.append("no required non-skipped passing test result for phase")
                if config.get("required_test_policy", {}).get("skipped_required_tests_block", True):
                    for name, row in latest_required.items():
                        if row.get("status") == "skipped":
                            gate_errors.append(f"required test skipped: {name}")

            deviations = [row for row in read_jsonl(qc_path(root) / "deviation-log.jsonl") if row.get("phase_id") == args.phase_id]
            for row in deviations:
                if row.get("severity") == "blocker":
                    if not row.get("accepted_by_user"):
                        gate_errors.append("unaccepted blocker deviation exists")
                    elif not decision_exists(root, args.phase_id, str(row.get("decision_id", "")), "accepted_with_risk"):
                        gate_errors.append("accepted blocker deviation lacks matching decision-log entry")

            if enforcement.get("enforce_issue_register", True):
                blockers = [
                    row for row in read_jsonl(qc_path(root) / "issue-register.jsonl")
                    if is_open_blocker_issue(row, args.phase_id)
                ]
                if blockers:
                    gate_errors.append(f"open blocker issue exists: {blockers[0].get('issue_id', '<unidentified>')}")

            if args.require_builder_scope:
                audit = read_builder_scope_audit(root, args.phase_id)
                if audit is None:
                    gate_errors.append("missing builder scope audit")
                elif not audit.get("ok"):
                    summary = audit.get("summary", {})
                    gate_errors.append(f"builder scope audit found {summary.get('unexpected', 0)} unexpected changes")

            release_required = release_required_for_phase(root, args.phase_id, explicit_release_phase=args.release_phase)
            board = read_phase_board(root)
            board["release_required"] = release_required
            write_phase_board(root, board)
            if release_required:
                release = run_dir / "release-gate.md"
                release_verdict = read_verdict(release)
                if release_verdict != "pass":
                    gate_errors.append(f"release phase requires release-gate verdict pass, got {release_verdict}")

            if args.scan_safety:
                findings = scan_safety(root)
                blockers = [finding for finding in findings if finding.get("severity") == "blocker"]
                if findings:
                    (qc_path(root) / "safety-scan-findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
                if blockers:
                    safety_errors.append(f"safety scan found {len(blockers)} blocker findings")
                elif findings:
                    warnings.append(f"safety scan found {len(findings)} non-blocking findings")

    errors = schema_errors + gate_errors + safety_errors
    result = {
        "errors": errors,
        "warnings": warnings,
        "schema_errors": schema_errors,
        "gate_errors": gate_errors,
        "safety_errors": safety_errors,
        "release_required": release_required,
        "ok": not errors,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for warning in warnings:
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
        print("ok" if not errors else "failed")
    if not errors:
        return 0
    if schema_errors:
        return EXIT_SCHEMA
    if safety_errors:
        return EXIT_SAFETY
    if args.strict_gate:
        return EXIT_STRICT_GATE
    return EXIT_GENERAL_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
