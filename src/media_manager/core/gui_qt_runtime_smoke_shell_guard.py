from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_GUARD_SCHEMA_VERSION = "1.0"
def _mapping(value: object) -> Mapping[str, Any]: return value if isinstance(value, Mapping) else {}
def build_qt_runtime_smoke_shell_guard(shell_registration: Mapping[str, Any]) -> dict[str, object]:
    summary = _mapping(shell_registration.get("summary")); reasons: list[str] = []
    if not shell_registration.get("enabled"): reasons.append("registration_disabled")
    if int(summary.get("problem_count") or 0) > 0: reasons.append("diagnostics_have_problems")
    if summary.get("local_only") is not True: reasons.append("not_local_only")
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_GUARD_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_guard", "page_id": shell_registration.get("page_id"), "allowed": not reasons, "reasons": reasons, "requires_user_confirmation": True, "opens_window": False, "executes_commands": False, "local_only": True, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_GUARD_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_guard"]
