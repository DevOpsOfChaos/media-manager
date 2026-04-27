from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_WIRING_ROLLBACK_PLAN_SCHEMA_VERSION = "1.0"
def build_qt_runtime_smoke_wiring_rollback_plan(wiring_plan: Mapping[str, Any], router_patch: Mapping[str, Any]) -> dict[str, object]:
    page_id = str(wiring_plan.get("page_id") or "runtime-smoke")
    ops = [{"id": "remove-runtime-smoke-route", "target": "router", "page_id": page_id}, {"id": "remove-runtime-smoke-page-loader", "target": "page_loader", "page_id": page_id}, {"id": "remove-runtime-smoke-commands", "target": "command_dispatch", "page_id": page_id}, {"id": "remove-runtime-smoke-status-slot", "target": "status_footer", "page_id": page_id}]
    return {"schema_version": QT_RUNTIME_SMOKE_WIRING_ROLLBACK_PLAN_SCHEMA_VERSION, "kind": "qt_runtime_smoke_wiring_rollback_plan", "route_count_before_rollback": len(router_patch.get("routes", [])) if isinstance(router_patch.get("routes"), list) else 0, "operations": [{**op, "executes_immediately": False, "manual_only": True} for op in ops], "summary": {"operation_count": len(ops), "immediate_execution_count": 0, "manual_only": True, "opens_window": False, "executes_commands": False, "local_only": True}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_WIRING_ROLLBACK_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_wiring_rollback_plan"]
