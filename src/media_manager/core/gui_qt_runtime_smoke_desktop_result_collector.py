from __future__ import annotations
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_COLLECTOR_SCHEMA_VERSION = "1.0"

def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []

def build_qt_runtime_smoke_desktop_result_collector(operator_sheet: Mapping[str, Any]) -> dict[str, object]:
    checks = [check for check in _list(operator_sheet.get("checks")) if isinstance(check, Mapping)]
    results = [{"check_id": check.get("id"), "label": check.get("label"), "required": bool(check.get("required", True)), "passed": None, "note": "", "evidence_path": None} for check in checks]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_COLLECTOR_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_collector",
        "ready_to_collect": bool(operator_sheet.get("ready")),
        "results": results,
        "summary": {"result_count": len(results), "required_result_count": sum(1 for result in results if result["required"]), "completed_result_count": 0, "failed_required_count": 0, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

def apply_qt_runtime_smoke_desktop_results(collector: Mapping[str, Any], results: Mapping[str, bool]) -> dict[str, object]:
    rows = []
    for row in _list(collector.get("results")):
        if not isinstance(row, Mapping):
            continue
        check_id = str(row.get("check_id"))
        rows.append({**dict(row), "passed": results.get(check_id, row.get("passed"))})
    summary = dict(collector.get("summary", {})) if isinstance(collector.get("summary"), Mapping) else {}
    summary.update({
        "completed_result_count": sum(1 for row in rows if row.get("passed") is not None),
        "failed_required_count": sum(1 for row in rows if row.get("required") and row.get("passed") is False),
        "passed_required_count": sum(1 for row in rows if row.get("required") and row.get("passed") is True),
    })
    return {**dict(collector), "results": rows, "summary": summary}

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_COLLECTOR_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_result_collector", "apply_qt_runtime_smoke_desktop_results"]
