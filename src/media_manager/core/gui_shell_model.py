from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .app_services import build_app_home_state, read_json_object
from .gui_actions import build_page_actions
from .gui_command_palette import build_command_palette
from .gui_i18n import localize_navigation_item, normalize_language, translate
from .gui_onboarding import build_onboarding_state
from .gui_page_models import build_page_model
from .gui_settings_model import load_gui_settings, normalize_gui_settings
from .gui_theme import build_theme_payload, normalize_theme

SHELL_SCHEMA_VERSION = "2.0"
DEFAULT_WINDOW_SIZE = {"width": 1320, "height": 860}


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
    for item in items:
        if not isinstance(item, Mapping):
            continue
        page_id = str(item.get("id") or item.get("page_id") or "").strip()
        if not page_id:
            continue
        localized = localize_navigation_item(item, language=language)
        normalized.append(
            {
                "id": page_id,
                "label": localized.get("label") or page_id.replace("-", " ").title(),
                "enabled": bool(item.get("enabled", True)),
                "active": page_id == active_page_id,
                "icon": item.get("icon") or _default_icon_for_page(page_id),
            }
        )
    if not normalized:
        for page_id in ("dashboard", "new-run", "people-review", "run-history", "profiles", "settings"):
            normalized.append({"id": page_id, "label": translate(f"nav.{page_id}", language=language), "enabled": True, "active": page_id == active_page_id, "icon": _default_icon_for_page(page_id)})
    return normalized


def build_gui_shell_model(
    *,
    home_state: Mapping[str, Any] | None = None,
    active_page_id: str | None = None,
    title: str = "Media Manager",
    language: str | None = None,
    theme: str | None = None,
    settings: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Build a stable, headless model for the modern desktop GUI."""
    normalized_settings = normalize_gui_settings(settings)
    lang = normalize_language(language or str(normalized_settings.get("language")))
    selected_theme = normalize_theme(theme or str(normalized_settings.get("theme")))
    active = str(active_page_id or normalized_settings.get("start_page_id") or "dashboard")
    state = dict(home_state or build_app_home_state(active_page_id=active))
    page_model = build_page_model(active, state, language=lang)
    navigation = _navigation_items(state, active_page_id=active, language=lang)
    status_text = state.get("suggested_next_step") or translate("status.ready", language=lang)
    return {
        "schema_version": SHELL_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "application": {
            "id": "media-manager",
            "title": translate("app.title", language=lang, fallback=title),
            "subtitle": translate("app.subtitle", language=lang),
            "mode": "desktop_gui",
            "stage": "modern_qt_shell_v1",
        },
        "window": {**DEFAULT_WINDOW_SIZE, "title": title, "minimum_width": 1040, "minimum_height": 720},
        "language": lang,
        "theme": build_theme_payload(selected_theme),
        "settings": normalized_settings,
        "active_page_id": active,
        "navigation": navigation,
        "page": page_model,
        "page_actions": build_page_actions(page_model, language=lang),
        "command_palette": build_command_palette(language=lang, home_state=state),
        "onboarding": build_onboarding_state(language=lang, dismissed=bool(normalized_settings.get("people_privacy_acknowledged"))),
        "home_state": state,
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
    language: str | None = None,
    theme: str | None = None,
) -> dict[str, object]:
    settings = load_gui_settings(settings_json)
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
        language=language,
        theme=theme,
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
            f"  Navigation items: {len(nav)}",
            f"  Modern Qt shell: {capabilities.get('qt_shell')}",
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
