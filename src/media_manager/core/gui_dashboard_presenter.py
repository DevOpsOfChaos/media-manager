from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_action_bar_model import build_action_bar
from .gui_presenter_state import build_presenter_state

DASHBOARD_PRESENTER_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_dashboard_presenter(page_model: Mapping[str, Any], *, home_state: Mapping[str, Any] | None = None, language: str = "en") -> dict[str, object]:
    hero = _mapping(page_model.get("hero"))
    cards = [dict(card) for card in _list(page_model.get("cards")) if isinstance(card, Mapping)]
    quick_actions = [dict(action) for action in _list(page_model.get("quick_actions")) if isinstance(action, Mapping)]
    action_bar = build_action_bar(quick_actions or [{"id": "new_run", "label": "New run", "recommended": True}])
    return {
        "schema_version": DASHBOARD_PRESENTER_SCHEMA_VERSION,
        "kind": "dashboard_presenter",
        "page_id": "dashboard",
        "title": page_model.get("title"),
        "hero": {
            "title": hero.get("title") or page_model.get("title"),
            "subtitle": hero.get("subtitle") or page_model.get("description"),
            "tone": "welcome",
        },
        "cards": cards,
        "card_count": len(cards),
        "action_bar": action_bar,
        "presenter": build_presenter_state(page_model=page_model, actions=quick_actions, language=language),
        "home_summary": {
            "has_people_review": isinstance(_mapping(home_state).get("people_review"), Mapping),
            "suggested_next_step": _mapping(home_state).get("suggested_next_step"),
        },
    }


__all__ = ["DASHBOARD_PRESENTER_SCHEMA_VERSION", "build_dashboard_presenter"]
