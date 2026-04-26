from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

KEYBOARD_ROUTER_SCHEMA_VERSION = "1.0"


def _norm_shortcut(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


_DEFAULT_SHORTCUTS = {
    "ctrl+k": {"type": "open_drawer", "drawer": "command_palette"},
    "ctrl+,": {"type": "navigate", "page_id": "settings"},
    "f5": {"type": "refresh_page"},
    "escape": {"type": "close_overlay"},
}


def build_keyboard_route_table(actions: Iterable[Mapping[str, Any]] = ()) -> dict[str, object]:
    routes: dict[str, dict[str, object]] = {key: {"shortcut": key, "intent": intent, "source": "default"} for key, intent in _DEFAULT_SHORTCUTS.items()}
    conflicts: list[dict[str, object]] = []
    for raw in actions:
        action = _mapping(raw)
        shortcut = _norm_shortcut(action.get("shortcut"))
        if not shortcut:
            continue
        intent = action.get("intent") if isinstance(action.get("intent"), Mapping) else {"type": "action", "action_id": action.get("id")}
        row = {"shortcut": shortcut, "intent": dict(intent), "source": "action", "action_id": action.get("id")}
        if shortcut in routes and routes[shortcut].get("action_id") != action.get("id"):
            conflicts.append({"shortcut": shortcut, "existing": routes[shortcut], "incoming": row})
            continue
        routes[shortcut] = row
    return {
        "schema_version": KEYBOARD_ROUTER_SCHEMA_VERSION,
        "kind": "qt_keyboard_route_table",
        "routes": dict(sorted(routes.items())),
        "route_count": len(routes),
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "executes_immediately": False,
    }


def route_keyboard_shortcut(shortcut: str, route_table: Mapping[str, Any]) -> dict[str, object]:
    routes = route_table.get("routes") if isinstance(route_table.get("routes"), Mapping) else {}
    key = _norm_shortcut(shortcut)
    row = routes.get(key) if isinstance(routes, Mapping) else None
    if not isinstance(row, Mapping):
        return {"handled": False, "shortcut": key, "intent": None, "executes_immediately": False}
    return {"handled": True, "shortcut": key, "intent": row.get("intent"), "source": row.get("source"), "executes_immediately": False}


__all__ = ["KEYBOARD_ROUTER_SCHEMA_VERSION", "build_keyboard_route_table", "route_keyboard_shortcut"]
