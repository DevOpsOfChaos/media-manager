from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .gui_qt_runtime_smoke_desktop_result_bundle import build_qt_runtime_smoke_desktop_result_bundle
from .gui_qt_runtime_smoke_result import normalize_qt_runtime_smoke_results, summarize_qt_runtime_smoke_results

QT_RUNTIME_SMOKE_RESULT_PAYLOAD_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _result_rows_from_payload(payload: object) -> Mapping[str, bool] | list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, Mapping)]
    if isinstance(payload, Mapping):
        for key in ("results", "runtime_smoke_results", "manual_results"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [item for item in rows if isinstance(item, Mapping)]
        bool_rows = {str(key): value for key, value in payload.items() if isinstance(value, bool)}
        if bool_rows:
            return bool_rows
    return []


def build_qt_runtime_smoke_result_payload_report(
    payload: object,
    *,
    source_path: str = "",
) -> dict[str, object]:
    rows = _result_rows_from_payload(payload)
    normalized = normalize_qt_runtime_smoke_results(rows)
    smoke_summary = summarize_qt_runtime_smoke_results(normalized)
    desktop_bundle = build_qt_runtime_smoke_desktop_result_bundle(normalized)
    desktop_summary = _mapping(desktop_bundle.get("summary"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_RESULT_PAYLOAD_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_result_payload_report",
        "source_path": _text(source_path),
        "result_shape": "mapping" if isinstance(rows, Mapping) else "rows",
        "results": normalized,
        "desktop_result_bundle": desktop_bundle,
        "accepted": bool(desktop_bundle.get("accepted")),
        "summary": {
            "result_count": smoke_summary.get("result_count", 0),
            "passed_count": smoke_summary.get("passed_count", 0),
            "failed_count": smoke_summary.get("failed_count", 0),
            "required_result_count": smoke_summary.get("required_result_count", 0),
            "failed_required_count": smoke_summary.get("failed_required_count", 0),
            "privacy_result_count": smoke_summary.get("privacy_result_count", 0),
            "accepted": bool(desktop_bundle.get("accepted")),
            "desktop_problem_count": desktop_summary.get("problem_count", 0),
            "desktop_missing_required_count": desktop_summary.get("missing_required_count", 0),
            "desktop_failed_required_count": desktop_summary.get("failed_required_count", 0),
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def load_qt_runtime_smoke_result_payload_file(path: str | Path) -> dict[str, object]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Runtime Smoke results file does not exist: {source}")
    if not source.is_file():
        raise IsADirectoryError(f"Runtime Smoke results path is not a file: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Runtime Smoke results file is not valid JSON: {source}") from exc
    if not isinstance(payload, (Mapping, list)):
        raise ValueError("Runtime Smoke results JSON must be an object or a list.")
    return build_qt_runtime_smoke_result_payload_report(payload, source_path=str(source))


def build_qt_runtime_smoke_result_collector_template(plan: Mapping[str, Any]) -> dict[str, object]:
    start_bundle = _mapping(plan.get("start_bundle"))
    collector = _mapping(start_bundle.get("result_collector"))
    rows = [
        {
            "check_id": row.get("check_id"),
            "label": row.get("label"),
            "required": bool(row.get("required", True)),
            "passed": None,
            "note": "",
            "evidence_path": "",
        }
        for row in _list(collector.get("results"))
        if isinstance(row, Mapping)
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_RESULT_PAYLOAD_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_result_payload_template",
        "results": rows,
        "summary": {
            "result_count": len(rows),
            "required_result_count": sum(1 for row in rows if row.get("required")),
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def summarize_qt_runtime_smoke_result_payload_report(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    return "\n".join(
        [
            "Qt Runtime Smoke manual result payload",
            f"  Source: {_text(report.get('source_path'), '<in-memory>')}",
            f"  Results: {summary.get('result_count', 0)}",
            f"  Passed: {summary.get('passed_count', 0)}",
            f"  Failed: {summary.get('failed_count', 0)}",
            f"  Accepted: {summary.get('accepted')}",
            f"  Desktop problems: {summary.get('desktop_problem_count', 0)}",
            f"  Opens window now: {summary.get('opens_window')}",
            f"  Executes commands now: {summary.get('executes_commands')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_SMOKE_RESULT_PAYLOAD_SCHEMA_VERSION",
    "build_qt_runtime_smoke_result_collector_template",
    "build_qt_runtime_smoke_result_payload_report",
    "load_qt_runtime_smoke_result_payload_file",
    "summarize_qt_runtime_smoke_result_payload_report",
]
