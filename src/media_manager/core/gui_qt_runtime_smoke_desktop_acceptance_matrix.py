from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_MATRIX_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _row(row_id: str, label: str, passed: bool, *, required: bool = True, detail: object = None) -> dict[str, object]:
    return {"id": row_id, "label": label, "passed": bool(passed), "required": bool(required), "detail": detail}


def build_qt_runtime_smoke_desktop_acceptance_matrix(acceptance_input: Mapping[str, Any]) -> dict[str, object]:
    summary = _mapping(acceptance_input.get("summary"))
    rows = [
        _row("start-ready", "Manual desktop start handoff is ready", bool(summary.get("start_ready"))),
        _row("results-accepted", "Desktop smoke results are accepted", bool(summary.get("accepted"))),
        _row("no-result-issues", "Desktop smoke result processing has no issues", int(summary.get("issue_count") or 0) == 0, detail=summary.get("issue_count", 0)),
        _row("no-start-issues", "Desktop start handoff has no issues", int(summary.get("start_problem_count") or 0) == 0, detail=summary.get("start_problem_count", 0)),
        _row("local-only", "All acceptance data remains local-only", summary.get("local_only") is True),
        _row("headless-contract", "Acceptance processing opens no window and executes no command", summary.get("opens_window") is False and summary.get("executes_commands") is False),
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_MATRIX_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_matrix",
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "required_row_count": sum(1 for row in rows if row["required"]),
            "passed_required_count": sum(1 for row in rows if row["required"] and row["passed"]),
            "failed_required_count": sum(1 for row in rows if row["required"] and not row["passed"]),
            "ready": all(row["passed"] for row in rows if row["required"]),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_MATRIX_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_matrix"]
