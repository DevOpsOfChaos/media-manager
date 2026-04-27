from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_EVENT_MAP_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_event_map(interaction_plan: Mapping[str, Any]) -> dict[str, object]:
    events = []
    for index, binding in enumerate(_list(interaction_plan.get("bindings"))):
        if not isinstance(binding, Mapping):
            continue
        action_id = str(binding.get("action_id") or f"action-{index + 1}")
        events.append(
            {
                "event_id": f"event-{action_id}",
                "binding_id": binding.get("binding_id"),
                "action_id": action_id,
                "qt_signal": "clicked",
                "handler_name": f"handle_{action_id.replace('-', '_')}",
                "enabled": bool(binding.get("enabled", True)),
                "requires_confirmation": bool(binding.get("requires_confirmation")),
                "executes_immediately": False,
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_EVENT_MAP_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_event_map",
        "page_id": interaction_plan.get("page_id"),
        "events": events,
        "summary": {
            "event_count": len(events),
            "enabled_event_count": sum(1 for event in events if event.get("enabled")),
            "confirmation_event_count": sum(1 for event in events if event.get("requires_confirmation")),
            "immediate_execution_count": 0,
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_EVENT_MAP_SCHEMA_VERSION", "build_qt_runtime_smoke_event_map"]
