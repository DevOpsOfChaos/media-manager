from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .app_services import build_app_home_state, read_json_object
from .gui_accessibility import build_accessibility_contract
from .gui_actions import build_page_actions
from .gui_command_palette import build_command_palette
from .gui_i18n import localize_navigation_item, normalize_language, translate
from .gui_layout import build_layout_tokens
from .gui_notifications import build_notification, build_notification_center
from .gui_onboarding import build_onboarding_state
from .gui_page_models import build_page_model
from .gui_router import build_gui_router_state, normalize_route
from .gui_safety_center import build_safety_center_state
from .gui_settings_model import load_gui_settings, normalize_gui_settings
from .gui_theme import build_theme_payload, normalize_theme
from .gui_view_state import load_gui_view_state, normalize_gui_view_state

SHELL_SCHEMA_VERSION = "4.0"
DEFAULT_WINDOW_SIZE = {"width": 1440, "height": 940}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _default_icon_for_page(page_id: str) -> str:
    return {
        "dashboard": "home",
        "new-run": "sparkles",
        "people-review": "users",
        "run-history": "clock",
        "profiles": "bookmark",
        "settings": "settings",
    }.get(page_id, "circle")


def _navigation_items(home_state: Mapping[str, Any], *, active_page_id: str, language: str) -> list[dict[str, object]]:
    navigation = _as_mapping(home_state.get("navigation"))
    items = _as_list(navigation.get("items"))
    if not items:
        pages = _as_list(home_state.get("pages"))
        items = [item for item in pages if isinstance(item, Mapping)]
    normalized: list[dict[str, object]] = []
    active = normalize_route(active_page_id)
    for item in items:
        if not isinstance(item, Mapping):
            continue
        page_id = normalize_route(item.get("id") or item.get("page_id") or "")
        if not page_id:
            continue
        localized = localize_navigation_item(item, language=language)
        normalized.append(
            {
                "id": page_id,
                "label": localized.get("label") or page_id.replace("-", " ").title(),
                "enabled": bool(item.get("enabled", True)),
                "active": page_id == active,
                "icon": item.get("icon") or _default_icon_for_page(page_id),
            }
        )
    if not normalized:
        for page_id in ("dashboard", "new-run", "people-review", "run-history", "profiles", "settings"):
            normalized.append({"id": page_id, "label": translate(f"nav.{page_id}", language=language), "enabled": True, "active": page_id == active, "icon": _default_icon_for_page(page_id)})
    return normalized


def build_gui_shell_model(
    *,
    home_state: Mapping[str, Any] | None = None,
    active_page_id: str | None = None,
    title: str = "Media Manager",
    language: str | None = None,
    theme: str | None = None,
    settings: Mapping[str, Any] | None = None,
    view_state: Mapping[str, Any] | None = None,
    density: str | None = None,
) -> dict[str, object]:
    """Build a stable, headless model for the modern desktop GUI."""
    normalized_settings = normalize_gui_settings(settings)
    normalized_view = normalize_gui_view_state(view_state)
    lang = normalize_language(language or str(normalized_settings.get("language")))
    selected_theme = normalize_theme(theme or str(normalized_settings.get("theme")))
    selected_density = density or str(normalized_settings.get("density") or "comfortable")
    active = normalize_route(active_page_id or normalized_view.get("active_page_id") or normalized_settings.get("start_page_id") or "dashboard")
    query = str(normalized_view.get("search_query") or "")
    state = dict(home_state or build_app_home_state(active_page_id=active))
    page_model = build_page_model(
        active,
        state,
        language=lang,
        density=selected_density,
        query=query,
        selected_group_id=normalized_view.get("selected_group_id") if isinstance(normalized_view.get("selected_group_id"), str) else None,
    )
    navigation = _navigation_items(state, active_page_id=active, language=lang)
    status_text = state.get("suggested_next_step") or translate("status.ready", language=lang)
    window_settings = _as_mapping(normalized_settings.get("window"))
    safety_center = build_safety_center_state(page_model=page_model)
    notifications = []
    if safety_center.get("warning_count"):
        notifications.append(build_notification("safety", "Safety notice", "Review safety notices before applying changes.", level="warning", action={"page_id": "settings"}))
    return {
        "schema_version": SHELL_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "application": {
            "id": "media-manager",
            "title": translate("app.title", language=lang, fallback=title),
            "subtitle": translate("app.subtitle", language=lang),
            "mode": "desktop_gui",
            "stage": "modern_qt_shell_v4",
        },
        "window": {
            **DEFAULT_WINDOW_SIZE,
            "title": title,
            "minimum_width": 1180,
            "minimum_height": 760,
            **dict(window_settings),
        },
        "language": lang,
        "theme": build_theme_payload(selected_theme),
        "layout": build_layout_tokens(selected_density),
        "accessibility": build_accessibility_contract(language=lang),
        "settings": normalized_settings,
        "view_state": normalized_view,
        "router": build_gui_router_state(active_page_id=active, language=lang),
        "active_page_id": active,
        "navigation": navigation,
        "page": page_model,
        "page_actions": build_page_actions(page_model, language=lang),
        "command_palette": build_command_palette(language=lang, home_state=state),
        "onboarding": build_onboarding_state(language=lang, dismissed=not bool(normalized_settings.get("show_onboarding", True)) or bool(normalized_settings.get("people_privacy_acknowledged"))),
        "home_state": state,
        "safety_center": safety_center,
        "notifications": build_notification_center(notifications),
        "status_bar": {
            "text": status_text,
            "privacy": translate("privacy.people", language=lang),
        },
        "capabilities": {
            "headless_model": True,
            "qt_shell": True,
            "tkinter_shell": False,
            "modern_ui": True,
            "bilingual_ui": True,
            "people_review_preview": True,
            "interactive_navigation": True,
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
    settings_json: str | Path | None = None,
    view_state_json: str | Path | None = None,
    language: str | None = None,
    theme: str | None = None,
    density: str | None = None,
) -> dict[str, object]:
    settings = load_gui_settings(settings_json)
    view_state = load_gui_view_state(view_state_json)
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
    return build_gui_shell_model(
        home_state=home_state,
        active_page_id=active_page_id,
        settings=settings,
        view_state=view_state,
        language=language,
        theme=theme,
        density=density,
    )


def summarize_gui_shell_model(model: Mapping[str, Any]) -> str:
    app = _as_mapping(model.get("application"))
    page = _as_mapping(model.get("page"))
    nav = _as_list(model.get("navigation"))
    status = _as_mapping(model.get("status_bar"))
    capabilities = _as_mapping(model.get("capabilities"))
    return "\n".join(
        [
            str(app.get("title") or "Media Manager"),
            f"  Active page: {model.get('active_page_id')}",
            f"  Page title: {page.get('title')}",
            f"  Language: {model.get('language')}",
            f"  Theme: {_as_mapping(model.get('theme')).get('theme')}",
            f"  Density: {_as_mapping(model.get('layout')).get('density')}",
            f"  Navigation items: {len(nav)}",
            f"  Modern Qt shell: {capabilities.get('qt_shell')}",
            f"  Interactive navigation: {capabilities.get('interactive_navigation')}",
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
