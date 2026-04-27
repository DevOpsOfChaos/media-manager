from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_ADAPTER_VALIDATION_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def validate_qt_runtime_smoke_adapter_bundle(bundle: Mapping[str, Any]) -> dict[str, object]:
    problems: list[dict[str, object]] = []
    widget_summary = _mapping(_mapping(bundle.get("widget_tree")).get("summary"))
    render_summary = _mapping(_mapping(bundle.get("render_plan")).get("summary"))
    interaction_summary = _mapping(_mapping(bundle.get("interaction_plan")).get("summary"))
    event_summary = _mapping(_mapping(bundle.get("event_map")).get("summary"))
    surface_summary = _mapping(_mapping(bundle.get("visible_surface")).get("summary"))
    if int(widget_summary.get("unsupported_component_count") or 0) > 0:
        problems.append({"code": "unsupported_components", "components": widget_summary.get("unsupported_components", [])})
    if int(render_summary.get("executable_step_count") or 0) > 0:
        problems.append({"code": "render_plan_executes_immediately"})
    if int(interaction_summary.get("immediate_execution_count") or 0) > 0:
        problems.append({"code": "interaction_plan_executes_immediately"})
    if int(event_summary.get("immediate_execution_count") or 0) > 0:
        problems.append({"code": "event_map_executes_immediately"})
    if surface_summary.get("local_only") is not True:
        problems.append({"code": "surface_not_local_only"})
    if int(render_summary.get("render_step_count") or 0) <= 0:
        problems.append({"code": "empty_render_plan"})
    return {
        "schema_version": QT_RUNTIME_SMOKE_ADAPTER_VALIDATION_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_adapter_validation",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "unsupported_component_count": int(widget_summary.get("unsupported_component_count") or 0),
            "render_step_count": int(render_summary.get("render_step_count") or 0),
            "binding_count": int(interaction_summary.get("binding_count") or 0),
            "event_count": int(event_summary.get("event_count") or 0),
            "local_only": bool(surface_summary.get("local_only", True)),
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_ADAPTER_VALIDATION_SCHEMA_VERSION", "validate_qt_runtime_smoke_adapter_bundle"]
