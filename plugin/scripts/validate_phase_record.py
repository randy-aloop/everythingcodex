from __future__ import annotations

import argparse
import json

from builder_team_qc_lib import (
    REQUIRED_PHASE_FILES,
    file_has_pending,
    phase_id_arg,
    phase_run_dir,
    qc_path,
    read_jsonl,
    root_path,
    scan_safety,
    validate_templates,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate builder-team QC phase evidence.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--phase-id", type=phase_id_arg)
    parser.add_argument("--template-only", action="store_true")
    parser.add_argument("--release-phase", action="store_true")
    parser.add_argument("--scan-safety", action="store_true")
    parser.add_argument("--strict-gate", action="store_true", help="Fail pending verdicts and missing test evidence.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(validate_templates())
    if not args.template_only:
        if not args.phase_id:
            errors.append("--phase-id is required unless --template-only is used")
        else:
            root = root_path(args.root)
            run_dir = phase_run_dir(root, args.phase_id)
            if not run_dir.exists():
                errors.append(f"missing phase run directory: {run_dir}")
            for name in REQUIRED_PHASE_FILES:
                path = run_dir / name
                if not path.exists():
                    errors.append(f"missing required phase file: {name}")
                elif name != "release-gate.md" and file_has_pending(path):
                    message = f"pending verdict remains in {name}"
                    if args.strict_gate:
                        errors.append(message)
                    else:
                        warnings.append(message)
            events = [row for row in read_jsonl(qc_path(root) / "ponytail-events.jsonl") if row.get("phase_id") == args.phase_id]
            if not events:
                errors.append("missing ponytail event for phase")
            elif events[-1].get("minimum_code_verdict") != "pass":
                errors.append("latest ponytail event is not pass")
            tests = read_jsonl(qc_path(root) / "test-results" / f"{args.phase_id}.jsonl")
            if not tests:
                if args.strict_gate:
                    errors.append("no recorded test result for phase")
                else:
                    warnings.append("no recorded test result for phase")
            elif any(row.get("status") == "fail" for row in tests):
                errors.append("one or more recorded tests failed")
            deviations = [row for row in read_jsonl(qc_path(root) / "deviation-log.jsonl") if row.get("phase_id") == args.phase_id]
            for row in deviations:
                if row.get("severity") == "blocker" and not row.get("accepted_by_user"):
                    errors.append("unaccepted blocker deviation exists")
            if args.release_phase:
                release = run_dir / "release-gate.md"
                if file_has_pending(release) or "Verdict: not_applicable" in release.read_text(encoding="utf-8", errors="replace"):
                    errors.append("release phase requires a completed release gate")
            if args.scan_safety:
                findings = scan_safety(root)
                if findings:
                    errors.append(f"safety scan found {len(findings)} banned markers")
                    (qc_path(root) / "safety-scan-findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")

    result = {"errors": errors, "warnings": warnings, "ok": not errors}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for warning in warnings:
            print(f"warning: {warning}")
        for error in errors:
            print(f"error: {error}")
        print("ok" if not errors else "failed")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
