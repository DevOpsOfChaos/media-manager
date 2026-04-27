from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DIAGNOSTICS_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_diagnostics(adapter_bundle: Mapping[str, Any], route_validation: Mapping[str, Any]) -> dict[str, object]:
    """Build diagnostics for Runtime Smoke page registration and adapter readiness."""

    adapter_summary = _mapping(adapter_bundle.get("summary"))
    validation = _mapping(adapter_bundle.get("validation"))
    route_summary = _mapping(route_validation.get("summary"))
    adapter_problem_count = int(validation.get("problem_count") or adapter_summary.get("problem_count") or 0)
    route_problem_count = int(route_validation.get("problem_count") or 0)
    ready = bool(adapter_bundle.get("ready_for_qt_runtime")) and bool(route_validation.get("valid"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_DIAGNOSTICS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_diagnostics",
        "ready": ready,
        "adapter": {
            "ready_for_qt_runtime": bool(adapter_bundle.get("ready_for_qt_runtime")),
            "render_step_count": int(adapter_summary.get("render_step_count") or 0),
            "binding_count": int(adapter_summary.get("binding_count") or 0),
            "event_count": int(adapter_summary.get("event_count") or 0),
            "problem_count": adapter_problem_count,
            "local_only": bool(adapter_summary.get("local_only", True)),
        },
        "route": {
            "valid": bool(route_validation.get("valid")),
            "route_id": route_summary.get("route_id"),
            "page_id": route_summary.get("page_id"),
            "problem_count": route_problem_count,
            "local_only": bool(route_summary.get("local_only", True)),
        },
        "summary": {
            "total_problem_count": adapter_problem_count + route_problem_count,
            "ready_for_page_registry": ready,
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


__all__ = ["QT_RUNTIME_SMOKE_DIAGNOSTICS_SCHEMA_VERSION", "build_qt_runtime_smoke_diagnostics"]
