from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_i18n import translate

ROUTER_SCHEMA_VERSION = "1.0"
DEFAULT_PAGE_ORDER = ("dashboard", "new-run", "people-review", "run-history", "profiles", "settings")


def normalize_route(page_id: object) -> str:
    text = str(page_id or "dashboard").strip().lower().replace("_", "-")
    return {
        "runs": "run-history",
        "history": "run-history",
        "people": "people-review",
        "person-review": "people-review",
        "new": "new-run",
        "new run": "new-run",
        "doctor": "settings",
        "settings-doctor": "settings",
    }.get(text, text or "dashboard")


def build_route_record(page_id: str, *, language: str = "en", active_page_id: str = "dashboard") -> dict[str, object]:
    route = normalize_route(page_id)
    return {
        "page_id": route,
        "label": translate(f"nav.{route}", language=language, fallback=route.replace("-", " ").title()),
        "active": route == normalize_route(active_page_id),
        "enabled": True,
        "path": f"/{route}",
        "shortcut": {
            "dashboard": "Ctrl+1",
            "new-run": "Ctrl+2",
            "people-review": "Ctrl+3",
            "run-history": "Ctrl+4",
            "profiles": "Ctrl+5",
            "settings": "Ctrl+,",
        }.get(route),
    }


def build_gui_router_state(*, active_page_id: str = "dashboard", language: str = "en") -> dict[str, object]:
    active = normalize_route(active_page_id)
    routes = [build_route_record(page_id, language=language, active_page_id=active) for page_id in DEFAULT_PAGE_ORDER]
    return {
        "schema_version": ROUTER_SCHEMA_VERSION,
        "active_page_id": active,
        "routes": routes,
        "can_go_back": False,
        "can_go_forward": False,
        "breadcrumbs": [{"page_id": active, "label": translate(f"nav.{active}", language=language, fallback=active)}],
    }


def apply_route_to_shell_model(model: Mapping[str, Any], page_id: str) -> dict[str, object]:
    payload = dict(model)
    active = normalize_route(page_id)
    payload["active_page_id"] = active
    navigation = []
    for raw in model.get("navigation", []) if isinstance(model.get("navigation"), list) else []:
        if isinstance(raw, Mapping):
            item = dict(raw)
            item["active"] = normalize_route(item.get("id")) == active
            navigation.append(item)
    payload["navigation"] = navigation
    return payload


__all__ = ["DEFAULT_PAGE_ORDER", "ROUTER_SCHEMA_VERSION", "apply_route_to_shell_model", "build_gui_router_state", "build_route_record", "normalize_route"]
