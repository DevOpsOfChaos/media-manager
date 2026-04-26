from __future__ import annotations

from collections.abc import Mapping
from typing import Any

BREADCRUMB_SCHEMA_VERSION = "1.0"

_LABELS = {
    "en": {
        "dashboard": "Dashboard",
        "new-run": "New run",
        "people-review": "People review",
        "run-history": "Run history",
        "profiles": "Profiles",
        "settings": "Settings",
    },
    "de": {
        "dashboard": "Übersicht",
        "new-run": "Neuer Lauf",
        "people-review": "Personenprüfung",
        "run-history": "Laufhistorie",
        "profiles": "Profile",
        "settings": "Einstellungen",
    },
}

_ALIASES = {
    "people": "people-review",
    "runs": "run-history",
    "history": "run-history",
    "doctor": "settings",
    "new run": "new-run",
}


def normalize_page_id(page_id: object) -> str:
    value = str(page_id or "dashboard").strip().lower().replace("_", "-")
    return _ALIASES.get(value, value or "dashboard")


def _label(page_id: str, *, language: str = "en") -> str:
    lang = "de" if str(language).lower().startswith("de") else "en"
    return _LABELS.get(lang, _LABELS["en"]).get(page_id, page_id.replace("-", " ").title())


def build_breadcrumbs(
    active_page_id: object,
    *,
    parent_page_id: object | None = None,
    detail_label: object | None = None,
    language: str = "en",
) -> dict[str, object]:
    """Build a stable breadcrumb model for GUI navigation."""
    active = normalize_page_id(active_page_id)
    items: list[dict[str, object]] = [
        {"page_id": "dashboard", "label": _label("dashboard", language=language), "active": active == "dashboard", "enabled": True}
    ]
    parent = normalize_page_id(parent_page_id) if parent_page_id else None
    if active != "dashboard":
        if parent and parent not in {"dashboard", active}:
            items.append({"page_id": parent, "label": _label(parent, language=language), "active": False, "enabled": True})
        items.append({"page_id": active, "label": _label(active, language=language), "active": detail_label is None, "enabled": True})
    if detail_label:
        items.append({"page_id": active, "label": str(detail_label), "active": True, "enabled": False})
    return {
        "schema_version": BREADCRUMB_SCHEMA_VERSION,
        "kind": "breadcrumbs",
        "active_page_id": active,
        "items": items,
        "depth": len(items),
        "trail": [item["label"] for item in items],
    }


def breadcrumbs_from_page(page_model: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    page_id = page_model.get("page_id") or page_model.get("id") or "dashboard"
    detail = page_model.get("selected_group_id") or page_model.get("selected_item_label")
    return build_breadcrumbs(page_id, detail_label=detail, language=language)


__all__ = ["BREADCRUMB_SCHEMA_VERSION", "build_breadcrumbs", "breadcrumbs_from_page", "normalize_page_id"]
