from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_OPERATOR_REPLAY_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_desktop_acceptance_operator_replay(result_bundle: Mapping[str, Any]) -> dict[str, object]:
    validation = result_bundle.get("validation") if isinstance(result_bundle.get("validation"), Mapping) else {}
    steps = [
        {
            "id": f"replay-{row.get('check_id')}",
            "check_id": row.get("check_id"),
            "status": "passed" if row.get("passed") is True else "failed" if row.get("passed") is False else "missing",
            "manual_only": True,
            "executes_immediately": False,
        }
        for row in _list(validation.get("results"))
        if isinstance(row, Mapping)
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_OPERATOR_REPLAY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_operator_replay",
        "steps": steps,
        "summary": {
            "step_count": len(steps),
            "failed_step_count": sum(1 for step in steps if step["status"] == "failed"),
            "missing_step_count": sum(1 for step in steps if step["status"] == "missing"),
            "immediate_execution_count": 0,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_OPERATOR_REPLAY_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_operator_replay"]
