from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_action_bar_model import build_action_bar
from .gui_breadcrumbs import breadcrumbs_from_page
from .gui_filter_bar import build_status_filter_bar
from .gui_search_model import build_search_state

PRESENTER_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_presenter_state(
    *,
    page_model: Mapping[str, Any],
    shell_model: Mapping[str, Any] | None = None,
    actions: list[Mapping[str, Any]] | None = None,
    language: str = "en",
) -> dict[str, object]:
    rows = _list(page_model.get("rows") or page_model.get("groups") or [])
    status_bar = build_status_filter_bar([row for row in rows if isinstance(row, Mapping)])
    search = build_search_state(query=page_model.get("query", ""), fields=("title", "display_label", "status"))
    action_bar = build_action_bar(actions or _list(page_model.get("actions")))
    shell = _mapping(shell_model)
    return {
        "schema_version": PRESENTER_SCHEMA_VERSION,
        "kind": "presenter_state",
        "page_id": page_model.get("page_id"),
        "title": page_model.get("title"),
        "language": language,
        "breadcrumbs": breadcrumbs_from_page(page_model, language=language),
        "search": search,
        "filters": status_bar,
        "action_bar": action_bar,
        "status_text": _mapping(shell.get("status_bar")).get("text"),
        "safe_mode": not bool(shell.get("executes_commands", False)),
    }


__all__ = ["PRESENTER_SCHEMA_VERSION", "build_presenter_state"]
