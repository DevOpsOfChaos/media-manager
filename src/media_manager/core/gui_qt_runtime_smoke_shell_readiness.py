from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_READINESS_SCHEMA_VERSION = "1.0"
def _mapping(value: object) -> Mapping[str, Any]: return value if isinstance(value, Mapping) else {}
def evaluate_qt_runtime_smoke_shell_readiness(shell_registration: Mapping[str, Any], navigation_patch: Mapping[str, Any], command_surface: Mapping[str, Any], toolbar: Mapping[str, Any], guard: Mapping[str, Any]) -> dict[str, object]:
    problems: list[dict[str, object]] = []
    reg_summary = _mapping(shell_registration.get("summary")); nav_summary = _mapping(navigation_patch.get("summary")); cmd_summary = _mapping(command_surface.get("summary")); tb_summary = _mapping(toolbar.get("summary"))
    if shell_registration.get("enabled") is not True: problems.append({"code": "registration_not_enabled"})
    if int(reg_summary.get("problem_count") or 0) > 0: problems.append({"code": "registration_has_problems"})
    if int(nav_summary.get("runtime_smoke_item_count") or 0) != 1: problems.append({"code": "navigation_item_not_unique"})
    if int(cmd_summary.get("immediate_execution_count") or 0) > 0: problems.append({"code": "commands_execute_immediately"})
    if int(tb_summary.get("immediate_execution_count") or 0) > 0: problems.append({"code": "toolbar_executes_immediately"})
    if guard.get("allowed") is not True: problems.append({"code": "guard_blocks_route", "reasons": list(guard.get("reasons", [])) if isinstance(guard.get("reasons"), list) else []})
    if reg_summary.get("local_only") is not True: problems.append({"code": "registration_not_local_only"})
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_READINESS_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_readiness", "ready": not problems, "problem_count": len(problems), "problems": problems, "summary": {"navigation_item_count": int(nav_summary.get("runtime_smoke_item_count") or 0), "command_count": int(cmd_summary.get("command_count") or 0), "toolbar_button_count": int(tb_summary.get("button_count") or 0), "local_only": bool(reg_summary.get("local_only", True)), "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_READINESS_SCHEMA_VERSION", "evaluate_qt_runtime_smoke_shell_readiness"]
