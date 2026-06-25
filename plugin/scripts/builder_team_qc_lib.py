from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
TEMPLATE_DIR = PLUGIN_ROOT / "assets" / "qc-templates"

REQUIRED_PHASE_FILES = [
    "phase-record.md",
    "builder-notes.md",
    "reviewer-report.md",
    "test-report.md",
    "compliance-report.md",
    "seam-audit.md",
    "release-gate.md",
]

ROLE_VERDICT_FILES = [
    "reviewer-report.md",
    "test-report.md",
    "compliance-report.md",
    "seam-audit.md",
]

PONYTAIL_BOUND_ARTIFACTS = {
    "changed_files": "changed-files.json",
    "implementation_diff": "implementation-diff.patch",
}

QC_DIRS = [
    "phase-runs",
    "test-results",
    "seam-audits",
    "release-gates",
    "templates",
]

JSONL_FILES = [
    "issue-register.jsonl",
    "deviation-log.jsonl",
    "decision-log.jsonl",
    "ponytail-events.jsonl",
    "builder-scope-audits.jsonl",
    "gate-events.jsonl",
]

BANNED_PATTERNS = [
    ("secret_env", re.compile(r"\b(GOOGLE_API_KEY|GOOGLE_APPLICATION_CREDENTIALS|OPENAI_API_KEY|ANTHROPIC_API_KEY)\b")),
    ("credential_field", re.compile(r"\b(client_secret|refresh_token|private_key|password|api_key)\b", re.IGNORECASE)),
    ("remote_url", re.compile(r"https?://(?!127\.0\.0\.1|localhost)", re.IGNORECASE)),
    ("remote_tool", re.compile(r"\b(RemoteA2aAgent|OpenAPIToolset|RestApiTool|McpToolset|StreamableHTTP|SseConnectionParams|A2A)\b")),
    ("remote_backend", re.compile(r"\b(agentengine://|rag://|gs://|postgresql://|mysql://|postgresql\+asyncpg://|mysql\+aiomysql://)\b", re.IGNORECASE)),
    ("code_executor", re.compile(r"\b(UnsafeLocalCodeExecutor|ContainerCodeExecutor|VertexAiCodeExecutor|AgentEngineSandboxCodeExecutor|GkeCodeExecutor|code_executor)\b")),
    ("remote_docker", re.compile(r"\bbase_url\s*=", re.IGNORECASE)),
]

POLICY_DENY_WORDS = [
    "do not",
    "does not",
    "not allowed",
    "forbidden",
    "deny",
    "blocked",
    "without explicit approval",
    "no remote",
    "no public",
    "no secrets",
    "must not",
    "off by default",
    "default deny",
]

ACTIVE_SECRET_RE = re.compile(
    r"\b("
    r"GOOGLE_API_KEY|GOOGLE_APPLICATION_CREDENTIALS|OPENAI_API_KEY|ANTHROPIC_API_KEY|"
    r"client_secret|refresh_token|private_key|password|api_key"
    r")\b\s*[:=]\s*(?![\"']?(?:$|\.{3}|<|your-|example|placeholder|xxx|redacted|null|none))",
    re.IGNORECASE,
)

PRIVATE_KEY_BLOCK_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE)

ACTIVE_REMOTE_RE = re.compile(
    r"\b(RemoteA2aAgent|OpenAPIToolset|RestApiTool|McpToolset|StreamableHTTP|SseConnectionParams|A2A|"
    r"UnsafeLocalCodeExecutor|ContainerCodeExecutor|VertexAiCodeExecutor|AgentEngineSandboxCodeExecutor|"
    r"GkeCodeExecutor|code_executor)\s*\("
    r"|\bbase_url\s*=\s*[\"']?(?:tcp://|https?://)"
    r"|\b(?:curl|wget|Invoke-WebRequest)\s+https?://",
    re.IGNORECASE,
)

SKIP_DIRS = {
    ".git",
    ".qc",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
}

BUILDER_SCOPE_SKIP_DIRS = SKIP_DIRS | {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
}

BUILDER_SCOPE_SKIP_FILES = {
    ".coverage",
}

SCOPE_HASH_LIMIT_BYTES = 20_000_000

ALLOWED_VERDICTS = {"pending", "pass", "revise", "block", "not_applicable"}
START_ALLOWED_STATUSES = {"", "not_started", "passed", "accepted_with_risk", "complete"}
GATE_TO_STATUS = {
    "pass": "passed",
    "revise": "revising",
    "block": "blocked",
    "accepted_with_risk": "accepted_with_risk",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def root_path(value: str | None) -> Path:
    return Path(value or os.getcwd()).resolve()


def qc_path(root: Path) -> Path:
    return root / ".qc"


def phase_id_arg(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,96}", value):
        raise argparse.ArgumentTypeError("phase id must use letters, digits, dot, underscore, or hyphen")
    return value


def read_json_file(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def default_qc_config() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "default_max_revise_attempts": 3,
        "release_gate_default": "auto",
        "release_phase_patterns": ["release", "deploy", "runtime", "docker", "production"],
        "required_test_policy": {
            "minimum_required_passes": 1,
            "skipped_required_tests_block": True,
        },
        "enforcement": {
            "enforce_role_verdicts": True,
            "enforce_issue_register": True,
            "require_passing_test": True,
            "auto_release_detect": True,
            "require_ponytail_diff_binding": True,
        },
        "ponytail_modes_allowed": [
            "task-scoped",
            "project-agents",
            "contained-workspace",
            "unavailable-fallback",
        ],
    }


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def read_qc_config(root: Path) -> dict[str, Any]:
    loaded = read_json_file(qc_path(root) / "qc-config.json", default={})
    if not isinstance(loaded, dict):
        loaded = {}
    return deep_merge(default_qc_config(), loaded)


def read_phase_board(root: Path) -> dict[str, Any]:
    board = read_json_file(qc_path(root) / "phase-board.json", default={})
    if not isinstance(board, dict):
        board = {}
    defaults = {
        "schema_version": "1.0",
        "current_phase_id": "",
        "current_phase_title": "",
        "current_phase_status": "not_started",
        "next_phase_id": "",
        "latest_gate_decision": "pending",
        "latest_gate_at": "",
        "last_gate_at": "",
        "release_required": False,
        "release_not_applicable_rationale": "",
        "revise_attempts": 0,
        "max_revise_attempts": read_qc_config(root).get("default_max_revise_attempts", 3),
        "required_evidence": REQUIRED_PHASE_FILES + list(PONYTAIL_BOUND_ARTIFACTS.values()) + ["ponytail-events.jsonl"],
        "blocking_issues": [],
        "accepted_risk_decision_id": "",
        "updated_at": "",
    }
    return {**defaults, **board}


def write_phase_board(root: Path, board: dict[str, Any]) -> None:
    board["updated_at"] = utc_now()
    write_json_file(qc_path(root) / "phase-board.json", board)


def ensure_qc(root: Path, dry_run: bool = False, force_templates: bool = False) -> list[str]:
    qc = qc_path(root)
    actions: list[str] = []
    paths = [qc] + [qc / d for d in QC_DIRS]
    for path in paths:
        actions.append(f"mkdir {path}")
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)

    for name in JSONL_FILES:
        path = qc / name
        actions.append(f"touch {path}")
        if not dry_run and not path.exists():
            path.write_text("", encoding="utf-8")

    for template in TEMPLATE_DIR.iterdir():
        if template.is_file():
            dest = qc / "templates" / template.name
            actions.append(f"copy-template {template.name}")
            if not dry_run and (force_templates or not dest.exists()):
                dest.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")

    for name in ["phase-board.json", "qc-config.json", "README.md"]:
        src = TEMPLATE_DIR / name
        dest = qc / name
        if src.exists():
            actions.append(f"seed {name}")
            if not dry_run and (force_templates or not dest.exists()):
                dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return actions


def render_template(name: str, values: dict[str, str]) -> str:
    text = (TEMPLATE_DIR / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def assert_can_start_phase(root: Path, phase_id: str, force: bool = False) -> None:
    board_path = qc_path(root) / "phase-board.json"
    if force or not board_path.exists():
        return
    board = read_phase_board(root)
    current_phase = str(board.get("current_phase_id") or "")
    current_status = str(board.get("current_phase_status") or "")
    if not current_phase or current_phase == phase_id:
        return
    if current_status in START_ALLOWED_STATUSES:
        return
    raise RuntimeError(
        f"cannot start phase {phase_id}: current phase {current_phase} is {current_status}; "
        "record a passing/accepted gate or rerun with --force"
    )


def start_phase(
    root: Path,
    phase_id: str,
    title: str,
    next_phase_id: str,
    build_plan: str,
    dry_run: bool = False,
    force: bool = False,
) -> Path:
    ensure_qc(root, dry_run=dry_run)
    if not dry_run:
        assert_can_start_phase(root, phase_id, force=force)
    run_dir = qc_path(root) / "phase-runs" / phase_id
    if not dry_run:
        (run_dir / "evidence").mkdir(parents=True, exist_ok=True)
    values = {
        "phase_id": phase_id,
        "title": title,
        "timestamp": utc_now(),
        "next_phase_id": next_phase_id,
        "build_plan": build_plan,
    }
    for name in REQUIRED_PHASE_FILES:
        dest = run_dir / name
        if not dry_run and not dest.exists():
            dest.write_text(render_template(name, values), encoding="utf-8")
    board = {
        "schema_version": "1.0",
        "current_phase_id": phase_id,
        "current_phase_title": title,
        "current_phase_status": "open",
        "next_phase_id": next_phase_id,
        "latest_gate_decision": "pending",
        "latest_gate_at": "",
        "last_gate_at": "",
        "release_required": False,
        "release_not_applicable_rationale": "",
        "revise_attempts": 0,
        "max_revise_attempts": read_qc_config(root).get("default_max_revise_attempts", 3),
        "required_evidence": REQUIRED_PHASE_FILES + list(PONYTAIL_BOUND_ARTIFACTS.values()) + ["ponytail-events.jsonl"],
        "blocking_issues": [],
        "accepted_risk_decision_id": "",
        "updated_at": utc_now(),
    }
    if not dry_run:
        write_phase_board(root, board)
    return run_dir


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def phase_run_dir(root: Path, phase_id: str) -> Path:
    return qc_path(root) / "phase-runs" / phase_id


def evidence_dir(root: Path, phase_id: str) -> Path:
    return phase_run_dir(root, phase_id) / "evidence"


def read_verdict(path: Path) -> str:
    if not path.exists():
        return "missing"
    verdicts: list[str] = []
    pattern = re.compile(r"^\s*(?:Verdict|Gate Decision):\s*([A-Za-z_ -]+)\s*$", re.IGNORECASE)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = pattern.match(line)
        if match:
            value = match.group(1).strip().lower().replace(" ", "_").replace("-", "_")
            verdicts.append(value)
    if not verdicts:
        return "unknown"
    unique = set(verdicts)
    if len(unique) > 1:
        return "duplicated"
    value = verdicts[0]
    if value not in ALLOWED_VERDICTS:
        return "unknown"
    return value


def file_has_pending(path: Path) -> bool:
    return read_verdict(path) in {"missing", "pending"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def phase_artifact_path(root: Path, phase_id: str, name: str) -> Path:
    return phase_run_dir(root, phase_id) / name


def phase_artifact_hash(root: Path, phase_id: str, name: str) -> str:
    path = phase_artifact_path(root, phase_id, name)
    if not path.exists():
        return ""
    return file_sha256(path)


def latest_ponytail_event(root: Path, phase_id: str) -> dict[str, Any] | None:
    events = [row for row in read_jsonl(qc_path(root) / "ponytail-events.jsonl") if row.get("phase_id") == phase_id]
    if not events:
        return None
    return events[-1]


def phase_record_text(root: Path, phase_id: str) -> str:
    path = phase_run_dir(root, phase_id) / "phase-record.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def phase_record_title(root: Path, phase_id: str) -> str:
    match = re.search(r"(?im)^Title:\s*(.+?)\s*$", phase_record_text(root, phase_id))
    return match.group(1).strip() if match else ""


def release_required_for_phase(root: Path, phase_id: str, explicit_release_phase: bool = False) -> bool:
    if explicit_release_phase:
        return True
    config = read_qc_config(root)
    default = str(config.get("release_gate_default", "auto")).lower()
    if default == "required":
        return True
    if default == "not_required":
        return False
    if not config.get("enforcement", {}).get("auto_release_detect", True):
        return False
    board = read_phase_board(root)
    text = " ".join(
        [
            str(board.get("current_phase_title", "")),
            str(board.get("current_phase_id", "")),
            phase_record_title(root, phase_id),
        ]
    ).lower()
    return any(str(pattern).lower() in text for pattern in config.get("release_phase_patterns", []))


def update_phase_record_gate(root: Path, phase_id: str, gate: str, status: str, note: str = "") -> None:
    path = phase_run_dir(root, phase_id) / "phase-record.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"(?im)^Status:\s*.*$", f"Status: {status}", text)
    text = re.sub(r"(?im)^Gate Decision:\s*.*$", f"Gate Decision: {gate}", text)
    if note:
        text += f"\n\n## Gate Recorder Note\n\n{note}\n"
    path.write_text(text, encoding="utf-8")


def next_record_id(rows: list[dict[str, Any]], prefix: str, phase_id: str) -> str:
    safe_phase = re.sub(r"[^A-Za-z0-9]+", "-", phase_id).strip("-") or "phase"
    count = sum(1 for row in rows if row.get("phase_id") == phase_id) + 1
    return f"{prefix}-{safe_phase}-{count:03d}"


def decision_exists(root: Path, phase_id: str, decision_id: str, decision_type: str | None = None) -> bool:
    if not decision_id:
        return False
    for row in read_jsonl(qc_path(root) / "decision-log.jsonl"):
        if row.get("decision_id") != decision_id:
            continue
        if row.get("phase_id") not in {phase_id, "", None}:
            continue
        if decision_type and row.get("decision_type") != decision_type:
            continue
        return bool(row.get("accepted_by") or row.get("approved_by"))
    return False


def append_gate_summary(root: Path, phase_id: str, record: dict[str, Any]) -> None:
    path = phase_run_dir(root, phase_id) / "gate-summary.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Gate Summary\n"
    with path.open("w", encoding="utf-8") as handle:
        handle.write(existing.rstrip() + "\n\n")
        handle.write("## Gate Event\n\n")
        handle.write("```json\n")
        handle.write(json.dumps(record, indent=2, ensure_ascii=True))
        handle.write("\n```\n")


def normalize_patterns(patterns: list[str] | tuple[str, ...] | None) -> list[str]:
    if not patterns:
        return []
    return [pattern.replace("\\", "/").strip() for pattern in patterns if pattern.strip()]


def path_matches_patterns(rel: str, patterns: list[str] | tuple[str, ...] | None) -> bool:
    rel = rel.replace("\\", "/")
    for pattern in normalize_patterns(patterns):
        if pattern.endswith("/") and rel.startswith(pattern):
            return True
        if rel == pattern or fnmatch.fnmatchcase(rel, pattern):
            return True
    return False


def should_skip_builder_scope_file(path: Path, root: Path, ignore_patterns: list[str] | tuple[str, ...] | None = None) -> bool:
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        return True
    rel = rel_path.as_posix()
    if any(part in BUILDER_SCOPE_SKIP_DIRS for part in rel_path.parts):
        return True
    if path.name in BUILDER_SCOPE_SKIP_FILES:
        return True
    return path_matches_patterns(rel, ignore_patterns)


def file_signature(path: Path) -> dict[str, Any]:
    stat = path.stat()
    signature: dict[str, Any] = {
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }
    if stat.st_size > SCOPE_HASH_LIMIT_BYTES:
        signature["sha256"] = None
        signature["hash_skipped_reason"] = f"file larger than {SCOPE_HASH_LIMIT_BYTES} bytes"
        return signature

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    signature["sha256"] = digest.hexdigest()
    return signature


def collect_builder_scope_files(root: Path, ignore_patterns: list[str] | tuple[str, ...] | None = None) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_builder_scope_file(path, root, ignore_patterns):
            continue
        try:
            rel = path.relative_to(root).as_posix()
            files[rel] = file_signature(path)
        except OSError:
            continue
    return dict(sorted(files.items()))


def create_builder_scope_baseline(
    root: Path,
    phase_id: str,
    ignore_patterns: list[str] | tuple[str, ...] | None = None,
    label: str = "before-builder",
) -> dict[str, Any]:
    run_dir = phase_run_dir(root, phase_id)
    if not run_dir.exists():
        raise FileNotFoundError(f"missing phase run directory: {run_dir}")
    baseline = {
        "schema_version": "1.0",
        "phase_id": phase_id,
        "label": label,
        "created_at": utc_now(),
        "root": str(root),
        "ignore_patterns": normalize_patterns(ignore_patterns),
        "files": collect_builder_scope_files(root, ignore_patterns),
    }
    dest = evidence_dir(root, phase_id) / "builder-scope-baseline.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(baseline, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return baseline


def read_builder_scope_baseline(root: Path, phase_id: str) -> dict[str, Any] | None:
    path = evidence_dir(root, phase_id) / "builder-scope-baseline.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def signature_changed(before: dict[str, Any], after: dict[str, Any]) -> bool:
    before_hash = before.get("sha256")
    after_hash = after.get("sha256")
    if before_hash is not None and after_hash is not None:
        return before_hash != after_hash
    return before.get("size") != after.get("size") or before.get("mtime_ns") != after.get("mtime_ns")


def create_builder_scope_audit(
    root: Path,
    phase_id: str,
    allow_patterns: list[str] | tuple[str, ...] | None = None,
    allow_remove_patterns: list[str] | tuple[str, ...] | None = None,
    ignore_patterns: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    baseline = read_builder_scope_baseline(root, phase_id)
    if baseline is None:
        raise FileNotFoundError(f"missing builder scope baseline for phase: {phase_id}")

    before_files = baseline.get("files", {})
    after_files = collect_builder_scope_files(root, ignore_patterns)
    before_set = set(before_files)
    after_set = set(after_files)
    added = sorted(after_set - before_set)
    removed = sorted(before_set - after_set)
    modified = sorted(
        rel
        for rel in before_set & after_set
        if signature_changed(before_files[rel], after_files[rel])
    )

    allowed = normalize_patterns(allow_patterns)
    allowed_remove = normalize_patterns(allow_remove_patterns)
    unexpected_added = [rel for rel in added if not path_matches_patterns(rel, allowed)]
    unexpected_modified = [rel for rel in modified if not path_matches_patterns(rel, allowed)]
    unexpected_removed = [rel for rel in removed if not path_matches_patterns(rel, allowed_remove)]
    ok = not unexpected_added and not unexpected_modified and not unexpected_removed

    audit = {
        "schema_version": "1.0",
        "phase_id": phase_id,
        "created_at": utc_now(),
        "baseline_created_at": baseline.get("created_at"),
        "ok": ok,
        "allow_patterns": allowed,
        "allow_remove_patterns": allowed_remove,
        "ignore_patterns": normalize_patterns(ignore_patterns),
        "added_files": added,
        "modified_files": modified,
        "removed_files": removed,
        "unexpected_added_files": unexpected_added,
        "unexpected_modified_files": unexpected_modified,
        "unexpected_removed_files": unexpected_removed,
        "summary": {
            "added": len(added),
            "modified": len(modified),
            "removed": len(removed),
            "unexpected": len(unexpected_added) + len(unexpected_modified) + len(unexpected_removed),
        },
    }
    dest = evidence_dir(root, phase_id) / "builder-scope-audit.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    append_jsonl(qc_path(root) / "builder-scope-audits.jsonl", audit)
    return audit


def read_builder_scope_audit(root: Path, phase_id: str) -> dict[str, Any] | None:
    path = evidence_dir(root, phase_id) / "builder-scope-audit.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def classify_safety_finding(rel: str, line: str, kind: str) -> tuple[str, str]:
    normalized = line.lower()

    if rel == "scripts/builder_team_qc_lib.py" and ("re.compile" in line or kind in {"secret_env", "credential_field", "remote_tool", "remote_backend", "code_executor", "remote_docker"}):
        return "info", "scanner self-definition"

    if ACTIVE_SECRET_RE.search(line) or PRIVATE_KEY_BLOCK_RE.search(line):
        return "blocker", "possible active secret or credential"

    if ACTIVE_REMOTE_RE.search(line):
        return "blocker", "possible active remote or execution capability"

    if rel.endswith(".md"):
        if any(word in normalized for word in POLICY_DENY_WORDS):
            return "info", "policy-deny documentation"
        if "github.com/" in normalized:
            return "info", "reference URL in documentation"
        return "warning", "risky term mentioned in documentation"

    if kind in {"secret_env", "credential_field"}:
        return "blocker", "possible active secret or credential"

    if kind in {"remote_tool", "remote_backend", "code_executor", "remote_docker"}:
        return "blocker", "possible active remote or execution capability"

    if kind == "remote_url":
        return "warning", "remote URL requires review"

    return "warning", "requires review"


def scan_safety(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(text.splitlines(), start=1):
            for name, pattern in BANNED_PATTERNS:
                if pattern.search(line):
                    severity, reason = classify_safety_finding(rel, line, name)
                    findings.append(
                        {
                            "severity": severity,
                            "kind": name,
                            "file": rel,
                            "line": line_no,
                            "reason": reason,
                            "text": line.strip()[:240],
                        }
                    )
    return findings


def validate_templates() -> list[str]:
    errors: list[str] = []
    for name in ["phase-board.json", "qc-config.json"]:
        try:
            json.loads((TEMPLATE_DIR / name).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
    for name in REQUIRED_PHASE_FILES:
        if not (TEMPLATE_DIR / name).exists():
            errors.append(f"missing template: {name}")
    return errors
