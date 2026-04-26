from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .app_services import build_app_home_state, read_json_object
from .gui_page_models import build_page_model

SHELL_SCHEMA_VERSION = "1.0"
DEFAULT_WINDOW_SIZE = {"width": 1180, "height": 760}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _navigation_items(home_state: Mapping[str, Any], *, active_page_id: str) -> list[dict[str, object]]:
    navigation = _as_mapping(home_state.get("navigation"))
    items = _as_list(navigation.get("items"))
    if not items:
        pages = _as_list(home_state.get("pages"))
        items = [item for item in pages if isinstance(item, Mapping)]
    normalized: list[dict[str, object]] = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        page_id = str(item.get("id") or item.get("page_id") or "").strip()
        if not page_id:
            continue
        normalized.append(
            {
                "id": page_id,
                "label": item.get("label") or item.get("title") or page_id.replace("-", " ").title(),
                "enabled": bool(item.get("enabled", True)),
                "active": page_id == active_page_id,
                "icon": item.get("icon"),
            }
        )
    if not normalized:
        for page_id, label in (
            ("dashboard", "Dashboard"),
            ("new-run", "New run"),
            ("people-review", "People review"),
            ("run-history", "Run history"),
            ("profiles", "Profiles"),
            ("settings", "Settings"),
        ):
            normalized.append({"id": page_id, "label": label, "enabled": True, "active": page_id == active_page_id, "icon": None})
    return normalized


def build_gui_shell_model(
    *,
    home_state: Mapping[str, Any] | None = None,
    active_page_id: str | None = None,
    title: str = "Media Manager",
) -> dict[str, object]:
    """Build a stable, headless GUI shell model for tests and future frontends."""
    state = dict(home_state or build_app_home_state(active_page_id=active_page_id or "dashboard"))
    active = str(active_page_id or state.get("active_page_id") or "dashboard")
    page_model = build_page_model(active, state)
    navigation = _navigation_items(state, active_page_id=active)
    return {
        "schema_version": SHELL_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "application": {
            "id": "media-manager",
            "title": title,
            "mode": "desktop_gui_shell",
            "stage": "shell_v1",
        },
        "window": {**DEFAULT_WINDOW_SIZE, "title": title},
        "active_page_id": active,
        "navigation": navigation,
        "page": page_model,
        "home_state": state,
        "status_bar": {
            "text": state.get("suggested_next_step") or "Ready.",
            "privacy": "People review artifacts are local/private.",
        },
        "capabilities": {
            "headless_model": True,
            "tkinter_shell": True,
            "people_review_preview": True,
            "executes_commands": False,
        },
    }


def build_gui_shell_model_from_paths(
    *,
    profile_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    active_page_id: str = "dashboard",
    home_state_json: str | Path | None = None,
) -> dict[str, object]:
    if home_state_json is not None:
        home_state = read_json_object(home_state_json)
        if profile_dir is not None or run_dir is not None or people_bundle_dir is not None:
            home_state = {
                **home_state,
                **build_app_home_state(
                    profile_dir=profile_dir,
                    run_dir=run_dir,
                    people_bundle_dir=people_bundle_dir,
                    active_page_id=active_page_id,
                ),
            }
    else:
        home_state = build_app_home_state(
            profile_dir=profile_dir,
            run_dir=run_dir,
            people_bundle_dir=people_bundle_dir,
            active_page_id=active_page_id,
        )
    return build_gui_shell_model(home_state=home_state, active_page_id=active_page_id)


def summarize_gui_shell_model(model: Mapping[str, Any]) -> str:
    app = _as_mapping(model.get("application"))
    page = _as_mapping(model.get("page"))
    nav = _as_list(model.get("navigation"))
    status = _as_mapping(model.get("status_bar"))
    return "\n".join(
        [
            str(app.get("title") or "Media Manager"),
            f"  Active page: {model.get('active_page_id')}",
            f"  Page title: {page.get('title')}",
            f"  Navigation items: {len(nav)}",
            f"  Status: {status.get('text')}",
        ]
    )


__all__ = [
    "DEFAULT_WINDOW_SIZE",
    "SHELL_SCHEMA_VERSION",
    "build_gui_shell_model",
    "build_gui_shell_model_from_paths",
    "summarize_gui_shell_model",
]
