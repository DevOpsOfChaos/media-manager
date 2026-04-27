from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_GATE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_gate(matrix: Mapping[str, Any]) -> dict[str, object]:
    summary = matrix.get("summary") if isinstance(matrix.get("summary"), Mapping) else {}
    problems = []
    failed = int(summary.get("failed_required_count") or 0)
    if failed:
        problems.append({"code": "failed_required_acceptance_rows", "count": failed})
    if summary.get("local_only") is not True:
        problems.append({"code": "acceptance_not_local_only"})
    ready = not problems
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_GATE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_gate",
        "ready": ready,
        "decision": "accepted_for_guarded_desktop_runtime" if ready else "blocked",
        "problem_count": len(problems),
        "problems": problems,
        "requires_user_confirmation": True,
        "executes_immediately": False,
        "summary": {
            "ready": ready,
            "failed_required_count": failed,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_GATE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_gate"]
