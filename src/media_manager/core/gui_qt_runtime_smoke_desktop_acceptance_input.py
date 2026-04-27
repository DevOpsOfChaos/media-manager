from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_INPUT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_desktop_acceptance_input(
    result_bundle: Mapping[str, Any],
    start_bundle: Mapping[str, Any],
    *,
    operator: str = "manual",
) -> dict[str, object]:
    result_summary = _mapping(result_bundle.get("summary"))
    start_summary = _mapping(start_bundle.get("summary"))
    accepted = bool(result_bundle.get("accepted"))
    start_ready = bool(start_bundle.get("ready_for_manual_desktop_start"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_INPUT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_input",
        "operator": operator,
        "result_bundle": dict(result_bundle),
        "start_bundle": dict(start_bundle),
        "accepted": accepted,
        "start_ready": start_ready,
        "summary": {
            "accepted": accepted,
            "start_ready": start_ready,
            "result_count": int(result_summary.get("result_count") or 0),
            "issue_count": int(result_summary.get("problem_count") or 0),
            "start_problem_count": int(start_summary.get("problem_count") or 0),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_INPUT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_input"]
