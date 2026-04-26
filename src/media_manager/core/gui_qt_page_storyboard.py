from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

STORYBOARD_SCHEMA_VERSION = "1.0"

_PAGE_ALIASES = {
    "home": "dashboard",
    "people": "people-review",
    "runs": "run-history",
    "history": "run-history",
    "doctor": "settings",
}

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

_DEFAULT_ORDER = ("dashboard", "new-run", "people-review", "run-history", "profiles", "settings")


def normalize_storyboard_page_id(page_id: object) -> str:
    value = str(page_id or "dashboard").strip().lower().replace("_", "-")
    return _PAGE_ALIASES.get(value, value or "dashboard")


def build_page_storyboard(
    page_ids: Iterable[object] | None = None,
    *,
    active_page_id: str = "dashboard",
    language: str = "en",
) -> dict[str, object]:
    lang = "de" if str(language).lower().startswith("de") else "en"
    active = normalize_storyboard_page_id(active_page_id)
    seen: set[str] = set()
    ids: list[str] = []
    for raw in page_ids or _DEFAULT_ORDER:
        page_id = normalize_storyboard_page_id(raw)
        if page_id not in seen:
            seen.add(page_id)
            ids.append(page_id)
    scenes = []
    for index, page_id in enumerate(ids, start=1):
        scenes.append(
            {
                "index": index,
                "page_id": page_id,
                "label": _LABELS[lang].get(page_id, page_id.replace("-", " ").title()),
                "active": page_id == active,
                "route": f"/{page_id}",
                "expected_regions": _expected_regions(page_id),
            }
        )
    return {
        "schema_version": STORYBOARD_SCHEMA_VERSION,
        "kind": "qt_page_storyboard",
        "language": lang,
        "active_page_id": active,
        "scene_count": len(scenes),
        "scenes": scenes,
        "complete": all(scene["page_id"] in _DEFAULT_ORDER for scene in scenes),
    }


def _expected_regions(page_id: str) -> list[str]:
    if page_id == "dashboard":
        return ["header", "hero", "cards", "activity"]
    if page_id == "people-review":
        return ["header", "queue", "detail", "face-strip", "apply-bar"]
    if page_id in {"run-history", "profiles"}:
        return ["header", "filters", "table", "details"]
    if page_id == "new-run":
        return ["header", "wizard", "preview"]
    return ["header", "content"]


def storyboard_summary(storyboard: Mapping[str, Any]) -> dict[str, object]:
    scenes = storyboard.get("scenes") if isinstance(storyboard.get("scenes"), list) else []
    return {
        "scene_count": len(scenes),
        "active_page_id": storyboard.get("active_page_id"),
        "routes": [scene.get("route") for scene in scenes if isinstance(scene, Mapping)],
    }


__all__ = ["STORYBOARD_SCHEMA_VERSION", "build_page_storyboard", "normalize_storyboard_page_id", "storyboard_summary"]
