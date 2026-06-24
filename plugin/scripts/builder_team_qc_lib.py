from __future__ import annotations

import argparse
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


def start_phase(root: Path, phase_id: str, title: str, next_phase_id: str, build_plan: str, dry_run: bool = False) -> Path:
    ensure_qc(root, dry_run=dry_run)
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
        "current_phase_status": "open",
        "next_phase_id": next_phase_id,
        "latest_gate_decision": "pending",
        "required_evidence": REQUIRED_PHASE_FILES + ["ponytail-events.jsonl"],
        "blocking_issues": [],
        "updated_at": utc_now(),
    }
    if not dry_run:
        (qc_path(root) / "phase-board.json").write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")
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


def file_has_pending(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return "verdict: pending" in text or "gate decision: pending" in text


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
                    findings.append({"kind": name, "file": rel, "line": line_no, "text": line.strip()[:240]})
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
