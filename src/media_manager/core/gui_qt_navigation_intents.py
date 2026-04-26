from __future__ import annotations

from collections.abc import Mapping
from typing import Any

NAVIGATION_INTENT_SCHEMA_VERSION = "1.0"

_PAGE_ALIASES = {
    "dashboard": "dashboard",
    "home": "dashboard",
    "new": "new-run",
    "new-run": "new-run",
    "people": "people-review",
    "people-review": "people-review",
    "review": "people-review",
    "runs": "run-history",
    "run-history": "run-history",
    "history": "run-history",
    "profiles": "profiles",
    "settings": "settings",
    "doctor": "settings",
    "execution": "execution",
    "jobs": "execution",
}


def normalize_qt_page_id(page_id: object, *, fallback: str = "dashboard") -> str:
    value = str(page_id or fallback).strip().lower().replace("_", "-").replace(" ", "-")
    return _PAGE_ALIASES.get(value, value or fallback)


def build_qt_navigation_intent(
    target_page_id: object,
    *,
    source_page_id: object | None = None,
    reason: str = "user_navigation",
    replace_history: bool = False,
) -> dict[str, object]:
    target = normalize_qt_page_id(target_page_id)
    source = normalize_qt_page_id(source_page_id, fallback="") if source_page_id is not None else None
    return {
        "schema_version": NAVIGATION_INTENT_SCHEMA_VERSION,
        "kind": "qt_navigation_intent",
        "intent_id": f"navigate:{target}",
        "action": "navigate",
        "source_page_id": source,
        "target_page_id": target,
        "reason": str(reason),
        "replace_history": bool(replace_history),
        "executes_immediately": False,
        "requires_confirmation": False,
        "safe_for_preview": True,
    }


def build_qt_reload_intent(*, page_id: object = "dashboard", reason: str = "manual_refresh") -> dict[str, object]:
    target = normalize_qt_page_id(page_id)
    return {
        "schema_version": NAVIGATION_INTENT_SCHEMA_VERSION,
        "kind": "qt_reload_intent",
        "intent_id": f"reload:{target}",
        "action": "reload_page",
        "target_page_id": target,
        "reason": str(reason),
        "executes_immediately": False,
        "requires_confirmation": False,
        "safe_for_preview": True,
    }


def build_qt_history_intent(action: str, *, current_page_id: object = "dashboard") -> dict[str, object]:
    normalized_action = str(action or "back").strip().lower()
    if normalized_action not in {"back", "forward"}:
        normalized_action = "back"
    return {
        "schema_version": NAVIGATION_INTENT_SCHEMA_VERSION,
        "kind": "qt_history_intent",
        "intent_id": f"history:{normalized_action}",
        "action": normalized_action,
        "current_page_id": normalize_qt_page_id(current_page_id),
        "executes_immediately": False,
        "requires_confirmation": False,
        "safe_for_preview": True,
    }


def navigation_intent_from_action(action: Mapping[str, Any], *, current_page_id: object = "dashboard") -> dict[str, object]:
    action_id = str(action.get("id") or action.get("action") or "").strip().lower()
    page_id = action.get("page_id") or action.get("target_page_id")
    if page_id is not None:
        return build_qt_navigation_intent(page_id, source_page_id=current_page_id, reason=action_id or "action")
    if action_id in {"reload", "refresh", "reload_page"}:
        return build_qt_reload_intent(page_id=current_page_id, reason=action_id)
    if action_id in {"back", "forward"}:
        return build_qt_history_intent(action_id, current_page_id=current_page_id)
    return {
        "schema_version": NAVIGATION_INTENT_SCHEMA_VERSION,
        "kind": "qt_unknown_intent",
        "intent_id": f"unknown:{action_id or 'action'}",
        "action": action_id or "unknown",
        "current_page_id": normalize_qt_page_id(current_page_id),
        "executes_immediately": False,
        "requires_confirmation": False,
        "safe_for_preview": True,
        "blocked_reason": "Action does not map to a known navigation intent.",
    }


__all__ = [
    "NAVIGATION_INTENT_SCHEMA_VERSION",
    "build_qt_history_intent",
    "build_qt_navigation_intent",
    "build_qt_reload_intent",
    "navigation_intent_from_action",
    "normalize_qt_page_id",
]
