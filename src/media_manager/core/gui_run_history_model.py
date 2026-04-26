from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .gui_i18n import translate
from .gui_modern_components import build_action_button, build_status_badge, build_table_model

RUN_HISTORY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_run_filters(*, language: str = "en") -> dict[str, object]:
    return {
        "schema_version": RUN_HISTORY_SCHEMA_VERSION,
        "search_placeholder": translate("run_history.search", language=language),
        "filters": [
            {"id": "all", "label": translate("filter.all", language=language), "active": True},
            {"id": "needs_review", "label": translate("filter.needs_review", language=language), "active": False},
            {"id": "errors", "label": translate("filter.errors", language=language), "active": False},
            {"id": "people", "label": translate("filter.people", language=language), "active": False},
        ],
    }


def build_run_history_table(runs: Iterable[Mapping[str, Any]], *, language: str = "en") -> dict[str, object]:
    rows = []
    for item in runs:
        rows.append(
            {
                "run_id": item.get("run_id"),
                "command": item.get("command"),
                "mode": item.get("mode"),
                "status": item.get("status"),
                "status_badge": build_status_badge(item.get("status")),
                "exit_code": item.get("exit_code"),
                "review_candidate_count": item.get("review_candidate_count", 0),
                "path": item.get("path"),
            }
        )
    return build_table_model(
        "run_history",
        ["run_id", "command", "mode", "status", "exit_code", "review_candidate_count"],
        rows,
        empty_state=translate("run_history.empty", language=language),
        row_actions=[build_action_button("open_run", translate("action.open", language=language), icon="folder")],
    )


def build_run_history_page_state(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    runs = _mapping(home_state.get("runs"))
    return {
        "schema_version": RUN_HISTORY_SCHEMA_VERSION,
        "kind": "run_history_state",
        "filters": build_run_filters(language=language),
        "table": build_run_history_table([item for item in _list(runs.get("items")) if isinstance(item, Mapping)], language=language),
    }


__all__ = ["RUN_HISTORY_SCHEMA_VERSION", "build_run_filters", "build_run_history_page_state", "build_run_history_table"]
