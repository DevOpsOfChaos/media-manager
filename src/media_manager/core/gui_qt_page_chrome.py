from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PAGE_CHROME_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_page_header(page_model: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "dashboard")
    title = str(page_model.get("title") or page_id.replace("-", " ").title())
    description = str(page_model.get("description") or "")
    return {
        "schema_version": PAGE_CHROME_SCHEMA_VERSION,
        "kind": "page_header",
        "page_id": page_id,
        "title": title,
        "description": description,
        "language": language,
        "show_search": page_id in {"people-review", "run-history", "profiles"},
        "show_refresh": True,
    }


def build_page_breadcrumbs(page_model: Mapping[str, Any]) -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "dashboard")
    return {
        "schema_version": PAGE_CHROME_SCHEMA_VERSION,
        "kind": "breadcrumbs",
        "items": [
            {"id": "dashboard", "label": "Dashboard", "target_page_id": "dashboard"},
            {"id": page_id, "label": str(page_model.get("title") or page_id), "target_page_id": page_id, "active": True},
        ] if page_id != "dashboard" else [
            {"id": "dashboard", "label": "Dashboard", "target_page_id": "dashboard", "active": True}
        ],
    }


def build_page_action_strip(page_model: Mapping[str, Any]) -> dict[str, object]:
    page_actions = _list(page_model.get("actions")) or _list(page_model.get("quick_actions"))
    normalized: list[dict[str, object]] = []
    for index, raw in enumerate(page_actions):
        action = _mapping(raw)
        action_id = str(action.get("id") or f"action-{index + 1}")
        normalized.append({
            "id": action_id,
            "label": str(action.get("label") or action_id.replace("_", " ").title()),
            "enabled": bool(action.get("enabled", True)),
            "requires_confirmation": bool(action.get("requires_confirmation", False)),
            "risk_level": str(action.get("risk_level") or "safe"),
            "executes_immediately": False,
        })
    return {
        "schema_version": PAGE_CHROME_SCHEMA_VERSION,
        "kind": "page_action_strip",
        "action_count": len(normalized),
        "confirmation_count": sum(1 for item in normalized if item["requires_confirmation"]),
        "actions": normalized,
    }


def build_page_chrome(page_model: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    header = build_page_header(page_model, language=language)
    breadcrumbs = build_page_breadcrumbs(page_model)
    actions = build_page_action_strip(page_model)
    return {
        "schema_version": PAGE_CHROME_SCHEMA_VERSION,
        "kind": "page_chrome",
        "page_id": header["page_id"],
        "header": header,
        "breadcrumbs": breadcrumbs,
        "actions": actions,
        "chrome_slots": ["header", "breadcrumbs", "actions"],
    }


__all__ = [
    "PAGE_CHROME_SCHEMA_VERSION",
    "build_page_action_strip",
    "build_page_breadcrumbs",
    "build_page_chrome",
    "build_page_header",
]
