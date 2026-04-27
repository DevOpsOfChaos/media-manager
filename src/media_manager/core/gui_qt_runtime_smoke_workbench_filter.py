from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_WORKBENCH_FILTER_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def filter_qt_runtime_smoke_history(
    history: Mapping[str, Any] | list[Mapping[str, Any]],
    *,
    active_page_id: str | None = None,
    ready: bool | None = None,
    limit: int | None = None,
) -> dict[str, object]:
    entries = _list(history.get("entries")) if isinstance(history, Mapping) else list(history)
    filtered = [dict(entry) for entry in entries if isinstance(entry, Mapping)]
    if active_page_id:
        filtered = [entry for entry in filtered if entry.get("active_page_id") == active_page_id]
    if ready is not None:
        filtered = [entry for entry in filtered if bool(entry.get("ready_for_release_gate")) is bool(ready)]
    if limit is not None:
        filtered = filtered[-max(0, int(limit)) :]
    return {
        "schema_version": QT_RUNTIME_SMOKE_WORKBENCH_FILTER_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_history_filter_result",
        "active_page_id": active_page_id,
        "ready": ready,
        "entries": filtered,
        "summary": {
            "entry_count": len(filtered),
            "ready_count": sum(1 for entry in filtered if entry.get("ready_for_release_gate") is True),
            "not_ready_count": sum(1 for entry in filtered if entry.get("ready_for_release_gate") is False),
            "problem_count_total": sum(int(_mapping(entry).get("problem_count") or 0) for entry in filtered),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_WORKBENCH_FILTER_SCHEMA_VERSION", "filter_qt_runtime_smoke_history"]
