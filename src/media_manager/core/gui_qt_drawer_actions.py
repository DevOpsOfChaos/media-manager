from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

DRAWER_ACTIONS_SCHEMA_VERSION = "1.0"

KNOWN_DRAWERS = ("notifications", "diagnostics", "command_palette", "help", "about")


def build_drawer_state(open_drawers: Iterable[str] = ()) -> dict[str, object]:
    open_set = {str(item) for item in open_drawers if str(item) in KNOWN_DRAWERS}
    return {
        "schema_version": DRAWER_ACTIONS_SCHEMA_VERSION,
        "kind": "qt_drawer_state",
        "drawers": [{"id": drawer, "open": drawer in open_set} for drawer in KNOWN_DRAWERS],
        "open_drawers": sorted(open_set),
        "open_count": len(open_set),
    }


def drawer_action(drawer_id: str, action: str) -> dict[str, object]:
    normalized_action = action if action in {"open", "close", "toggle"} else "toggle"
    enabled = drawer_id in KNOWN_DRAWERS
    return {
        "schema_version": DRAWER_ACTIONS_SCHEMA_VERSION,
        "kind": "qt_drawer_action",
        "drawer_id": drawer_id,
        "action": normalized_action,
        "enabled": enabled,
        "intent": {"type": f"{normalized_action}_drawer", "drawer_id": drawer_id},
        "executes_immediately": False,
    }


def apply_drawer_action(state: Mapping[str, Any], action_payload: Mapping[str, Any]) -> dict[str, object]:
    open_set = set(str(item) for item in state.get("open_drawers", []) if str(item) in KNOWN_DRAWERS)
    drawer_id = str(action_payload.get("drawer_id") or "")
    action = str(action_payload.get("action") or "toggle")
    if drawer_id in KNOWN_DRAWERS:
        if action == "open":
            open_set.add(drawer_id)
        elif action == "close":
            open_set.discard(drawer_id)
        else:
            if drawer_id in open_set:
                open_set.remove(drawer_id)
            else:
                open_set.add(drawer_id)
    return build_drawer_state(open_set)


__all__ = ["DRAWER_ACTIONS_SCHEMA_VERSION", "KNOWN_DRAWERS", "apply_drawer_action", "build_drawer_state", "drawer_action"]
