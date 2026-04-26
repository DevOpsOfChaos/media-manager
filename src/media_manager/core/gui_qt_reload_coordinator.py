from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

RELOAD_COORDINATOR_SCHEMA_VERSION = "1.0"

_FULL_REBUILD_CHANGES = {"theme", "language", "density", "settings", "window"}
_PAGE_REFRESH_CHANGES = {"page", "query", "selection", "people_bundle", "profile_dir", "run_dir"}
_LIGHT_REFRESH_CHANGES = {"status", "notifications", "diagnostics", "toolbar"}


def normalize_change_set(changes: Iterable[object]) -> list[str]:
    normalized = sorted({str(item).strip().lower().replace("-", "_") for item in changes if str(item).strip()})
    return normalized


def build_qt_reload_plan(changes: Iterable[object], *, active_page_id: str = "dashboard") -> dict[str, object]:
    normalized = normalize_change_set(changes)
    change_set = set(normalized)
    requires_full = bool(change_set & _FULL_REBUILD_CHANGES)
    requires_page = requires_full or bool(change_set & _PAGE_REFRESH_CHANGES)
    requires_status = requires_page or bool(change_set & _LIGHT_REFRESH_CHANGES)
    if requires_full:
        strategy = "full_rebuild"
    elif requires_page:
        strategy = "page_refresh"
    elif requires_status:
        strategy = "status_refresh"
    else:
        strategy = "noop"
    return {
        "schema_version": RELOAD_COORDINATOR_SCHEMA_VERSION,
        "kind": "qt_reload_plan",
        "active_page_id": str(active_page_id or "dashboard"),
        "changes": normalized,
        "strategy": strategy,
        "requires_full_rebuild": requires_full,
        "requires_page_refresh": requires_page,
        "requires_status_refresh": requires_status,
        "executes_immediately": False,
        "steps": _steps_for_strategy(strategy),
    }


def _steps_for_strategy(strategy: str) -> list[str]:
    if strategy == "full_rebuild":
        return ["save_view_state", "rebuild_shell_model", "rebuild_desktop_plan", "rebind_signals", "refresh_status"]
    if strategy == "page_refresh":
        return ["save_view_state", "rebuild_page_model", "refresh_page_widget", "refresh_status"]
    if strategy == "status_refresh":
        return ["refresh_status", "refresh_drawers"]
    return []


def compare_qt_state_for_reload(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, object]:
    changes: list[str] = []
    for key in ("active_page_id", "language"):
        if previous.get(key) != current.get(key):
            changes.append("page" if key == "active_page_id" else key)
    prev_theme = previous.get("theme") if isinstance(previous.get("theme"), Mapping) else {}
    curr_theme = current.get("theme") if isinstance(current.get("theme"), Mapping) else {}
    if prev_theme.get("theme") != curr_theme.get("theme"):
        changes.append("theme")
    prev_status = previous.get("status_bar") if isinstance(previous.get("status_bar"), Mapping) else {}
    curr_status = current.get("status_bar") if isinstance(current.get("status_bar"), Mapping) else {}
    if prev_status != curr_status:
        changes.append("status")
    return build_qt_reload_plan(changes, active_page_id=str(current.get("active_page_id") or previous.get("active_page_id") or "dashboard"))


__all__ = ["RELOAD_COORDINATOR_SCHEMA_VERSION", "build_qt_reload_plan", "compare_qt_state_for_reload", "normalize_change_set"]
