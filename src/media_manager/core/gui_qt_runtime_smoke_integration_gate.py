from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_INTEGRATION_GATE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def evaluate_qt_runtime_smoke_integration_gate(matrix: Mapping[str, Any]) -> dict[str, object]:
    """Evaluate whether Runtime Smoke can move to guarded shell integration."""

    summary = _mapping(matrix.get("summary"))
    problems: list[dict[str, object]] = []
    if summary.get("all_ready") is not True:
        problems.append({"code": "not_all_layers_ready"})
    if int(summary.get("problem_count_total") or 0) > 0:
        problems.append({"code": "integration_layers_have_problems", "problem_count": summary.get("problem_count_total")})
    if int(summary.get("requires_pyside6_count") or 0) > 0:
        problems.append({"code": "headless_layer_requires_pyside6"})
    if int(summary.get("opens_window_count") or 0) > 0:
        problems.append({"code": "headless_layer_opens_window"})
    if int(summary.get("executes_commands_count") or 0) > 0:
        problems.append({"code": "headless_layer_executes_commands"})
    if summary.get("all_local_only") is not True:
        problems.append({"code": "integration_not_local_only"})
    ready = not problems
    return {
        "schema_version": QT_RUNTIME_SMOKE_INTEGRATION_GATE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_integration_gate",
        "ready": ready,
        "decision": "ready_for_guarded_shell_integration" if ready else "blocked",
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "ready": ready,
            "matrix_row_count": summary.get("row_count", 0),
            "problem_count_total": summary.get("problem_count_total", 0),
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


__all__ = ["QT_RUNTIME_SMOKE_INTEGRATION_GATE_SCHEMA_VERSION", "evaluate_qt_runtime_smoke_integration_gate"]
