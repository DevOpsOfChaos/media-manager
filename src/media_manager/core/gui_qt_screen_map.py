from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

SCREEN_MAP_SCHEMA_VERSION = "1.0"

_DEFAULT_ORDER = ["dashboard", "new-run", "people-review", "run-history", "profiles", "settings", "execution"]
_ALIASES = {"people": "people-review", "runs": "run-history", "doctor": "settings", "home": "dashboard"}


def normalize_screen_id(page_id: str | None) -> str:
    value = str(page_id or "dashboard").strip().lower().replace("_", "-")
    return _ALIASES.get(value, value or "dashboard")


def build_qt_screen_map(pages: Iterable[Mapping[str, Any]] | None = None, *, active_page_id: str = "dashboard") -> dict[str, object]:
    active = normalize_screen_id(active_page_id)
    seen: set[str] = set()
    screens: list[dict[str, object]] = []
    for index, page_id in enumerate(_DEFAULT_ORDER):
        seen.add(page_id)
        screens.append({
            "id": page_id,
            "index": index,
            "title": page_id.replace("-", " ").title(),
            "active": page_id == active,
            "enabled": True,
            "route": f"/{page_id}",
        })
    for page in pages or ():
        raw_id = normalize_screen_id(str(page.get("page_id") or page.get("id") or ""))
        if not raw_id or raw_id in seen:
            continue
        seen.add(raw_id)
        screens.append({
            "id": raw_id,
            "index": len(screens),
            "title": str(page.get("title") or raw_id.replace("-", " ").title()),
            "active": raw_id == active,
            "enabled": bool(page.get("enabled", True)),
            "route": f"/{raw_id}",
        })
    return {
        "schema_version": SCREEN_MAP_SCHEMA_VERSION,
        "active_page_id": active,
        "screen_count": len(screens),
        "screens": screens,
        "active_screen": next((item for item in screens if item["active"]), screens[0] if screens else None),
    }


__all__ = ["SCREEN_MAP_SCHEMA_VERSION", "build_qt_screen_map", "normalize_screen_id"]
