from __future__ import annotations
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ISSUE_REPORT_SCHEMA_VERSION = "1.0"

def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []

def build_qt_runtime_smoke_desktop_issue_report(result_collector: Mapping[str, Any]) -> dict[str, object]:
    failed = [row for row in _list(result_collector.get("results")) if isinstance(row, Mapping) and row.get("required") and row.get("passed") is False]
    issues = [{"id": f"issue-{row.get('check_id')}", "check_id": row.get("check_id"), "label": row.get("label"), "severity": "error", "note": row.get("note", ""), "local_only": True} for row in failed]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ISSUE_REPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_issue_report",
        "issues": issues,
        "summary": {"issue_count": len(issues), "has_blocking_issues": bool(issues), "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ISSUE_REPORT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_issue_report"]
