from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_WIRING_DRY_RUN_SCHEMA_VERSION = "1.0"
def _m(v: object) -> Mapping[str, Any]: return v if isinstance(v, Mapping) else {}
def build_qt_runtime_smoke_wiring_dry_run(router_patch: Mapping[str, Any], page_loader_contract: Mapping[str, Any], command_dispatch_plan: Mapping[str, Any], status_footer_patch: Mapping[str, Any]) -> dict[str, object]:
    actions = [
        {"id": "apply-router-patch", "target": "router", "ready": _m(router_patch.get("summary")).get("runtime_smoke_route_count") == 1},
        {"id": "register-page-loader", "target": "page_loader", "ready": bool(page_loader_contract.get("enabled"))},
        {"id": "register-command-dispatch", "target": "command_dispatch", "ready": int(_m(command_dispatch_plan.get("summary")).get("immediate_execution_count") or 0) == 0},
        {"id": "apply-status-footer", "target": "status_footer", "ready": _m(status_footer_patch.get("summary")).get("local_only") is True},
    ]
    return {"schema_version": QT_RUNTIME_SMOKE_WIRING_DRY_RUN_SCHEMA_VERSION, "kind": "qt_runtime_smoke_wiring_dry_run", "actions": [{**a, "simulated": True, "executes_immediately": False} for a in actions], "summary": {"action_count": len(actions), "ready_action_count": sum(1 for a in actions if a["ready"]), "simulated_action_count": len(actions), "immediate_execution_count": 0, "ready": all(a["ready"] for a in actions), "opens_window": False, "executes_commands": False, "local_only": True}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_WIRING_DRY_RUN_SCHEMA_VERSION", "build_qt_runtime_smoke_wiring_dry_run"]
