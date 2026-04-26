from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QUICK_ACTION_SCHEMA_VERSION = "1.0"

_PAGE_ACTIONS: dict[str, list[dict[str, object]]] = {
    "dashboard": [
        {"id": "start_preview", "label": "Start preview", "page_id": "new-run", "risk_level": "safe", "icon": "sparkles"},
        {"id": "open_people_review", "label": "Open people review", "page_id": "people-review", "risk_level": "safe", "icon": "users"},
    ],
    "people-review": [
        {"id": "filter_needs_review", "label": "Needs review", "intent": "filter", "risk_level": "safe", "icon": "list-filter"},
        {"id": "preview_apply", "label": "Preview apply", "intent": "people_review_apply_preview", "risk_level": "medium", "icon": "shield-check"},
        {"id": "apply_ready", "label": "Apply ready groups", "intent": "people_review_apply", "risk_level": "high", "requires_confirmation": True, "icon": "check-circle"},
    ],
    "run-history": [
        {"id": "refresh_runs", "label": "Refresh runs", "intent": "refresh", "risk_level": "safe", "icon": "refresh-cw"},
    ],
}


def _text(value: object, default: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def build_quick_action(
    action_id: str,
    label: str,
    *,
    page_id: str | None = None,
    intent: str | None = None,
    risk_level: str = "safe",
    enabled: bool = True,
    requires_confirmation: bool = False,
    icon: str = "circle",
    payload: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": QUICK_ACTION_SCHEMA_VERSION,
        "kind": "quick_action",
        "id": _text(action_id, "action"),
        "label": _text(label, "Action"),
        "page_id": page_id,
        "intent": intent or action_id,
        "risk_level": risk_level,
        "enabled": bool(enabled),
        "requires_confirmation": bool(requires_confirmation or risk_level in {"high", "destructive"}),
        "icon": _text(icon, "circle"),
        "payload": dict(payload or {}),
    }


def build_quick_actions_for_page(page_id: str, *, context: Mapping[str, Any] | None = None) -> dict[str, object]:
    context = context or {}
    actions = []
    for action in _PAGE_ACTIONS.get(str(page_id), []):
        enabled = True
        if action["id"] == "apply_ready":
            enabled = bool(context.get("has_ready_people_groups"))
        action_payload = {**action, "enabled": enabled}
        action_id = str(action_payload.pop("id"))
        label = str(action_payload.pop("label"))
        actions.append(build_quick_action(action_id, label, **action_payload))
    return {
        "schema_version": QUICK_ACTION_SCHEMA_VERSION,
        "kind": "quick_action_bar",
        "page_id": page_id,
        "actions": actions,
        "action_count": len(actions),
        "enabled_action_count": sum(1 for action in actions if action.get("enabled")),
    }


__all__ = ["QUICK_ACTION_SCHEMA_VERSION", "build_quick_action", "build_quick_actions_for_page"]
