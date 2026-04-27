from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_ROUTER_PATCH_SCHEMA_VERSION = "1.0"
def _lst(v: object) -> list[Any]: return v if isinstance(v, list) else []
def build_qt_runtime_smoke_router_patch(wiring_plan: Mapping[str, Any], *, existing_routes: list[Mapping[str, Any]] | None = None) -> dict[str, object]:
    routes = [dict(r) for r in (existing_routes or []) if isinstance(r, Mapping)]
    before = len(routes); routes = [r for r in routes if r.get("route_id") != "runtime-smoke" and r.get("page_id") != "runtime-smoke"]
    route = {"route_id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": bool(wiring_plan.get("ready")), "loader_id": "runtime-smoke-page-loader", "manual_only": True, "local_only": True, "opens_window": False, "executes_commands": False}
    routes.append(route)
    return {"schema_version": QT_RUNTIME_SMOKE_ROUTER_PATCH_SCHEMA_VERSION, "kind": "qt_runtime_smoke_router_patch", "operation": "upsert_route", "route": route, "routes": routes, "summary": {"before_count": before, "after_count": len(routes), "replaced_existing": before == len(routes), "runtime_smoke_route_count": sum(1 for r in routes if r.get("route_id") == "runtime-smoke"), "enabled": route["enabled"], "opens_window": False, "executes_commands": False, "local_only": True}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
def collect_qt_runtime_smoke_route_ids(router_patch: Mapping[str, Any]) -> list[str]:
    return [str(r.get("route_id")) for r in _lst(router_patch.get("routes")) if isinstance(r, Mapping)]
__all__ = ["QT_RUNTIME_SMOKE_ROUTER_PATCH_SCHEMA_VERSION", "build_qt_runtime_smoke_router_patch", "collect_qt_runtime_smoke_route_ids"]
