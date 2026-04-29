from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_ROUTE_RESOLVER_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def resolve_qt_runtime_smoke_route(guarded_integration: Mapping[str, Any], *, route_id: str = "runtime-smoke") -> dict[str, object]:
    """Resolve Runtime Smoke into the existing route/page/visible-plan surfaces."""

    page = _mapping(guarded_integration.get("page_model"))
    visible_surface = _mapping(guarded_integration.get("visible_surface"))
    page_handoff = _mapping(guarded_integration.get("page_handoff"))
    route = _mapping(page_handoff.get("route"))
    page_loader = _mapping(_mapping(guarded_integration.get("wiring_bundle")).get("page_loader_contract"))
    resolved = str(route.get("route_id") or route.get("page_id") or route_id) == route_id
    loader_enabled = bool(page_loader.get("enabled"))
    ready = resolved and page.get("page_id") == "runtime-smoke" and visible_surface.get("ready_for_qt_adapter") is True
    return {
        "schema_version": QT_RUNTIME_SMOKE_ROUTE_RESOLVER_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_route_resolver",
        "route_id": route_id,
        "page_id": page.get("page_id") or "runtime-smoke",
        "resolved": resolved,
        "loader_enabled": loader_enabled,
        "page_model_kind": page.get("kind"),
        "visible_surface_kind": visible_surface.get("kind"),
        "ready": ready,
        "summary": {
            "resolved": resolved,
            "loader_enabled": loader_enabled,
            "ready": ready,
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


__all__ = ["QT_RUNTIME_SMOKE_ROUTE_RESOLVER_SCHEMA_VERSION", "resolve_qt_runtime_smoke_route"]
