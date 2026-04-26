from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

QT_RUNTIME_SMOKE_PERSISTENCE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _json_ready(value: Mapping[str, Any]) -> dict[str, object]:
    return json.loads(json.dumps(dict(value), ensure_ascii=False, sort_keys=True))


def write_json_object_atomic(path: str | Path, payload: Mapping[str, Any]) -> dict[str, object]:
    """Write a JSON object atomically without importing Qt or touching media files."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = _json_ready(payload)
    temp = target.with_name(f"{target.name}.tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(target)
    return {
        "schema_version": QT_RUNTIME_SMOKE_PERSISTENCE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_persistence_write",
        "path": str(target),
        "bytes_written": target.stat().st_size,
        "object_kind": data.get("kind"),
        "local_only": True,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def read_json_object(path: str | Path) -> dict[str, object]:
    """Read a JSON object from disk and reject non-object payloads."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {target}")
    return payload


def save_qt_runtime_smoke_report(path: str | Path, report: Mapping[str, Any]) -> dict[str, object]:
    payload = {
        "schema_version": QT_RUNTIME_SMOKE_PERSISTENCE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_report_file",
        "report": _json_ready(report),
        "local_only": True,
    }
    return write_json_object_atomic(path, payload)


def load_qt_runtime_smoke_report(path: str | Path) -> dict[str, object]:
    payload = read_json_object(path)
    report = _mapping(payload.get("report"))
    if not report:
        raise ValueError(f"Missing smoke report in {path}")
    return dict(report)


def smoke_report_file_summary(path: str | Path) -> dict[str, object]:
    target = Path(path)
    payload = read_json_object(target)
    report = _mapping(payload.get("report"))
    summary = _mapping(report.get("summary"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_PERSISTENCE_SCHEMA_VERSION,
        "path": str(target),
        "exists": target.exists(),
        "object_kind": payload.get("kind"),
        "report_kind": report.get("kind"),
        "active_page_id": report.get("active_page_id"),
        "ready_for_release_gate": bool(report.get("ready_for_release_gate")),
        "problem_count": int(summary.get("problem_count") or 0),
        "local_only": bool(payload.get("local_only", True)),
    }


__all__ = [
    "QT_RUNTIME_SMOKE_PERSISTENCE_SCHEMA_VERSION",
    "load_qt_runtime_smoke_report",
    "read_json_object",
    "save_qt_runtime_smoke_report",
    "smoke_report_file_summary",
    "write_json_object_atomic",
]
