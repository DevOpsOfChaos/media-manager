from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_WIRING_PLAN_SCHEMA_VERSION = "1.0"
def _m(v: object) -> Mapping[str, Any]: return v if isinstance(v, Mapping) else {}
def build_qt_runtime_smoke_shell_wiring_plan(integration_bundle: Mapping[str, Any], shell_bundle: Mapping[str, Any]) -> dict[str, object]:
    isummary, ssummary = _m(integration_bundle.get("summary")), _m(shell_bundle.get("summary"))
    ready = bool(integration_bundle.get("ready_for_guarded_shell_wiring")) and bool(shell_bundle.get("ready_for_shell"))
    steps = [
        {"id": "verify-integration-gate", "target": "integration_gate", "ready": bool(integration_bundle.get("ready_for_guarded_shell_wiring"))},
        {"id": "register-route", "target": "router", "ready": ready},
        {"id": "register-page-loader", "target": "page_loader", "ready": ready},
        {"id": "register-command-dispatch", "target": "command_dispatch", "ready": ready},
        {"id": "register-status-footer", "target": "status_footer", "ready": ready},
    ]
    problems = int(isummary.get("problem_count") or 0) + int(ssummary.get("problem_count") or 0)
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_WIRING_PLAN_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_wiring_plan", "page_id": "runtime-smoke", "ready": ready, "integration_bundle": dict(integration_bundle), "shell_bundle": dict(shell_bundle), "steps": steps, "summary": {"step_count": len(steps), "ready_step_count": sum(1 for s in steps if s["ready"]), "problem_count": problems, "ready_for_guarded_shell_wiring": ready, "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_WIRING_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_wiring_plan"]
