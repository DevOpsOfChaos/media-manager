from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_COMMAND_DISPATCH_PLAN_SCHEMA_VERSION = "1.0"
def _m(v: object) -> Mapping[str, Any]: return v if isinstance(v, Mapping) else {}
def _lst(v: object) -> list[Any]: return v if isinstance(v, list) else []
def build_qt_runtime_smoke_command_dispatch_plan(wiring_plan: Mapping[str, Any]) -> dict[str, object]:
    commands = [dict(c) for c in _lst(_m(_m(wiring_plan.get("shell_bundle")).get("commands")).get("commands")) if isinstance(c, Mapping)]
    dispatch = []
    for c in commands:
        cid = str(c.get("id"))
        dispatch.append({"dispatch_id": f"dispatch-{cid.replace('.', '-')}", "command_id": cid, "label": c.get("label"), "enabled": bool(c.get("enabled")), "requires_confirmation": bool(c.get("requires_confirmation")), "execute_policy": "manual_confirm" if c.get("requires_confirmation") else "deferred", "executes_immediately": False, "handler_name": f"handle_{cid.replace('.', '_').replace('-', '_')}"})
    return {"schema_version": QT_RUNTIME_SMOKE_COMMAND_DISPATCH_PLAN_SCHEMA_VERSION, "kind": "qt_runtime_smoke_command_dispatch_plan", "page_id": "runtime-smoke", "dispatch": dispatch, "summary": {"dispatch_count": len(dispatch), "enabled_dispatch_count": sum(1 for d in dispatch if d["enabled"]), "confirmation_dispatch_count": sum(1 for d in dispatch if d["requires_confirmation"]), "immediate_execution_count": 0}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_COMMAND_DISPATCH_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_command_dispatch_plan"]
