from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_diagnostics import build_qt_runtime_smoke_diagnostics
from .gui_qt_runtime_smoke_navigation_item import build_qt_runtime_smoke_navigation_item
from .gui_qt_runtime_smoke_page_registry import build_qt_runtime_smoke_page_registry
from .gui_qt_runtime_smoke_route_model import build_qt_runtime_smoke_route_model
from .gui_qt_runtime_smoke_route_validator import validate_qt_runtime_smoke_route

QT_RUNTIME_SMOKE_PAGE_HANDOFF_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_page_handoff(
    adapter_bundle: Mapping[str, Any],
    *,
    existing_pages: list[Mapping[str, Any]] | None = None,
) -> dict[str, object]:
    """Build the full page handoff contract for future shell integration."""

    route = build_qt_runtime_smoke_route_model(adapter_bundle)
    nav = build_qt_runtime_smoke_navigation_item(route)
    route_validation = validate_qt_runtime_smoke_route(route, nav)
    registry = build_qt_runtime_smoke_page_registry(route, nav, existing_pages=existing_pages)
    diagnostics = build_qt_runtime_smoke_diagnostics(adapter_bundle, route_validation)
    ready = bool(diagnostics.get("ready")) and bool(registry.get("summary", {}).get("runtime_smoke_registered"))  # type: ignore[union-attr]
    return {
        "schema_version": QT_RUNTIME_SMOKE_PAGE_HANDOFF_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_page_handoff",
        "adapter_bundle": dict(adapter_bundle),
        "route": route,
        "navigation_item": nav,
        "route_validation": route_validation,
        "page_registry": registry,
        "diagnostics": diagnostics,
        "summary": {
            "ready_for_shell_registration": ready,
            "page_count": registry["summary"]["page_count"],
            "problem_count": diagnostics["summary"]["total_problem_count"],
            "local_only": diagnostics["summary"]["local_only"],
            "opens_window": False,
            "executes_commands": False,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready_for_shell_registration": ready,
    }


__all__ = ["QT_RUNTIME_SMOKE_PAGE_HANDOFF_SCHEMA_VERSION", "build_qt_runtime_smoke_page_handoff"]
