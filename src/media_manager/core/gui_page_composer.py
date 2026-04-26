from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_dashboard_presenter import build_dashboard_presenter
from .gui_people_review_presenter import build_people_review_presenter
from .gui_presenter_state import build_presenter_state

PAGE_COMPOSER_SCHEMA_VERSION = "1.0"


def compose_page_presenter(
    page_model: Mapping[str, Any],
    *,
    shell_model: Mapping[str, Any] | None = None,
    home_state: Mapping[str, Any] | None = None,
    language: str = "en",
) -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "")
    if page_id == "dashboard":
        presenter = build_dashboard_presenter(page_model, home_state=home_state, language=language)
    elif page_id == "people-review":
        presenter = build_people_review_presenter(page_model, language=language)
    else:
        presenter = {
            "schema_version": PAGE_COMPOSER_SCHEMA_VERSION,
            "kind": "generic_page_presenter",
            "page_id": page_id,
            "title": page_model.get("title"),
            "presenter": build_presenter_state(page_model=page_model, shell_model=shell_model, language=language),
        }
    return {
        "schema_version": PAGE_COMPOSER_SCHEMA_VERSION,
        "kind": "composed_page",
        "page_id": page_id,
        "presenter": presenter,
        "layout": page_model.get("layout"),
        "safe_mode": True,
    }


def compose_shell_presenter(shell_model: Mapping[str, Any]) -> dict[str, object]:
    page = shell_model.get("page")
    page_model = page if isinstance(page, Mapping) else {}
    return {
        "schema_version": PAGE_COMPOSER_SCHEMA_VERSION,
        "kind": "composed_shell",
        "active_page_id": shell_model.get("active_page_id"),
        "navigation": shell_model.get("navigation", []),
        "page": compose_page_presenter(page_model, shell_model=shell_model, home_state=shell_model.get("home_state") if isinstance(shell_model.get("home_state"), Mapping) else None, language=str(shell_model.get("language") or "en")),
    }


__all__ = ["PAGE_COMPOSER_SCHEMA_VERSION", "compose_page_presenter", "compose_shell_presenter"]
