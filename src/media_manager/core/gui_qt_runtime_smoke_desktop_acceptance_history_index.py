from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_HISTORY_INDEX_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_history_index(entries: list[Mapping[str, Any]] | None = None) -> dict[str, object]:
    rows = [dict(entry) for entry in (entries or []) if isinstance(entry, Mapping)]
    rows.sort(key=lambda row: str(row.get("recorded_at_utc") or ""))
    latest = rows[-1] if rows else {}
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_HISTORY_INDEX_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_history_index",
        "entries": rows,
        "latest": latest,
        "summary": {
            "entry_count": len(rows),
            "accepted_count": sum(1 for row in rows if row.get("accepted") is True),
            "blocked_count": sum(1 for row in rows if row.get("accepted") is False),
            "latest_accepted": latest.get("accepted") if latest else None,
            "problem_count_total": sum(int(row.get("problem_count") or 0) for row in rows),
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_HISTORY_INDEX_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_history_index"]
