from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_INTERACTIONS_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_interaction_plan(visible_surface: Mapping[str, Any]) -> dict[str, object]:
    visible_plan = _mapping(visible_surface.get("visible_plan") or visible_surface)
    action_section = next((section for section in _list(visible_plan.get("sections")) if isinstance(section, Mapping) and section.get("component") == "ActionBar"), {})
    actions = [dict(action) for action in _list(_mapping(action_section).get("items")) if isinstance(action, Mapping)]
    bindings = [
        {
            "binding_id": f"binding-{action.get('id')}",
            "action_id": action.get("id"),
            "label": action.get("label"),
            "enabled": bool(action.get("enabled", True)),
            "requires_confirmation": bool(action.get("requires_confirmation")),
            "execute_policy": "manual_confirm" if action.get("requires_confirmation") else "deferred",
            "executes_immediately": False,
        }
        for action in actions
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_INTERACTIONS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_interaction_plan",
        "page_id": visible_plan.get("page_id"),
        "bindings": bindings,
        "summary": {
            "binding_count": len(bindings),
            "enabled_binding_count": sum(1 for binding in bindings if binding.get("enabled")),
            "confirmation_binding_count": sum(1 for binding in bindings if binding.get("requires_confirmation")),
            "immediate_execution_count": 0,
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_INTERACTIONS_SCHEMA_VERSION", "build_qt_runtime_smoke_interaction_plan"]
