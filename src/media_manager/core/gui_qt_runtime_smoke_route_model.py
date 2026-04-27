from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_ROUTE_MODEL_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_qt_runtime_smoke_route_model(adapter_bundle: Mapping[str, Any], *, route_id: str = "runtime-smoke") -> dict[str, object]:
    """Build a route model for the runtime smoke page without opening Qt."""

    surface = _mapping(adapter_bundle.get("visible_surface"))
    surface_summary = _mapping(surface.get("summary"))
    validation = _mapping(adapter_bundle.get("validation"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_ROUTE_MODEL_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_route_model",
        "route_id": _text(route_id, "runtime-smoke"),
        "page_id": adapter_bundle.get("page_id") or surface.get("page_id") or "runtime-smoke",
        "active_page_id": surface.get("active_page_id"),
        "label": "Runtime Smoke",
        "description": "Inspect Qt runtime smoke readiness before opening a window.",
        "enabled": bool(adapter_bundle.get("ready_for_qt_runtime")),
        "visible": True,
        "badge": {
            "state": "ready" if adapter_bundle.get("ready_for_qt_runtime") else "blocked",
            "problem_count": int(_mapping(adapter_bundle.get("summary")).get("problem_count") or 0),
        },
        "guards": {
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "local_only": bool(surface_summary.get("local_only", True)),
            "requires_user_confirmation": True,
            "validation_valid": bool(validation.get("valid")),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_ROUTE_MODEL_SCHEMA_VERSION", "build_qt_runtime_smoke_route_model"]
