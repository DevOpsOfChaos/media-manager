from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_STATUS_SLOT_SCHEMA_VERSION = "1.0"
def _mapping(value: object) -> Mapping[str, Any]: return value if isinstance(value, Mapping) else {}
def build_qt_runtime_smoke_shell_status_slot(shell_registration: Mapping[str, Any]) -> dict[str, object]:
    diag = _mapping(shell_registration.get("diagnostics")); problem_count = int(_mapping(diag.get("summary")).get("total_problem_count") or _mapping(shell_registration.get("summary")).get("problem_count") or 0)
    state = "ready" if shell_registration.get("enabled") and problem_count == 0 else "blocked"
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_STATUS_SLOT_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_status_slot", "slot_id": "runtime-smoke-status", "page_id": shell_registration.get("page_id"), "state": state, "text": "Runtime Smoke ready" if state == "ready" else "Runtime Smoke needs attention", "problem_count": problem_count, "local_only": True, "opens_window": False, "executes_commands": False, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_STATUS_SLOT_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_status_slot"]
