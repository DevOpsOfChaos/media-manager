from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

TOOLBAR_ACTIONS_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _action(action_id: str, label: str, *, icon: str = "circle", category: str = "secondary", enabled: bool = True, requires_confirmation: bool = False, page_id: str | None = None) -> dict[str, object]:
    return {
        "id": action_id,
        "label": label,
        "icon": icon,
        "category": category,
        "enabled": bool(enabled),
        "requires_confirmation": bool(requires_confirmation),
        "page_id": page_id,
        "executes_immediately": False,
    }


def default_qt_toolbar_actions(page_id: str, *, language: str = "en") -> list[dict[str, object]]:
    labels_de = str(language).lower().startswith("de")
    refresh = "Aktualisieren" if labels_de else "Refresh"
    settings = "Einstellungen" if labels_de else "Settings"
    if page_id == "people-review":
        return [
            _action("refresh_people_review", refresh, icon="refresh", category="secondary", page_id=page_id),
            _action("apply_ready_people_groups", "Bereite Gruppen anwenden" if labels_de else "Apply ready groups", icon="shield", category="danger", requires_confirmation=True, page_id=page_id),
            _action("open_settings", settings, icon="settings", page_id="settings"),
        ]
    if page_id == "dashboard":
        return [
            _action("new_run", "Neuer Lauf" if labels_de else "New run", icon="sparkles", category="primary", page_id="new-run"),
            _action("open_people_review", "Personenprüfung" if labels_de else "People review", icon="users", page_id="people-review"),
            _action("refresh_dashboard", refresh, icon="refresh", page_id=page_id),
        ]
    return [_action("refresh_page", refresh, icon="refresh", page_id=page_id), _action("open_settings", settings, icon="settings", page_id="settings")]


def build_qt_toolbar_actions(page_model: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "dashboard")
    explicit_actions = [dict(item) for item in _list(page_model.get("quick_actions")) if isinstance(item, Mapping)]
    actions = explicit_actions or default_qt_toolbar_actions(page_id, language=language)
    normalized: list[dict[str, object]] = []
    for item in actions:
        category = str(item.get("category") or item.get("variant") or "secondary")
        normalized.append(
            {
                "id": str(item.get("id") or item.get("action_id") or "action"),
                "label": str(item.get("label") or item.get("title") or item.get("id") or "Action"),
                "icon": str(item.get("icon") or "circle"),
                "category": category,
                "enabled": bool(item.get("enabled", True)),
                "requires_confirmation": bool(item.get("requires_confirmation") or category == "danger"),
                "page_id": item.get("page_id") or page_id,
                "executes_immediately": False,
            }
        )
    return {
        "schema_version": TOOLBAR_ACTIONS_SCHEMA_VERSION,
        "kind": "qt_toolbar_actions",
        "page_id": page_id,
        "action_count": len(normalized),
        "primary_count": sum(1 for item in normalized if item.get("category") == "primary"),
        "danger_count": sum(1 for item in normalized if item.get("category") == "danger"),
        "confirmation_count": sum(1 for item in normalized if item.get("requires_confirmation")),
        "actions": normalized,
    }


def merge_qt_toolbar_actions(*action_groups: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    seen: set[str] = set()
    merged: list[dict[str, object]] = []
    for group in action_groups:
        for item in group:
            action_id = str(item.get("id") or "")
            if not action_id or action_id in seen:
                continue
            seen.add(action_id)
            merged.append(dict(item))
    return {
        "schema_version": TOOLBAR_ACTIONS_SCHEMA_VERSION,
        "kind": "qt_toolbar_action_merge",
        "action_count": len(merged),
        "actions": merged,
    }


__all__ = ["TOOLBAR_ACTIONS_SCHEMA_VERSION", "build_qt_toolbar_actions", "default_qt_toolbar_actions", "merge_qt_toolbar_actions"]
