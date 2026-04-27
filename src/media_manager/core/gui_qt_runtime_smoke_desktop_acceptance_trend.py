from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_TREND_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_trend(history_index: Mapping[str, Any]) -> dict[str, object]:
    entries = history_index.get("entries") if isinstance(history_index.get("entries"), list) else []
    points = [
        {
            "index": index,
            "recorded_at_utc": entry.get("recorded_at_utc") if isinstance(entry, Mapping) else None,
            "accepted": bool(entry.get("accepted")) if isinstance(entry, Mapping) else False,
            "problem_count": int(entry.get("problem_count") or 0) if isinstance(entry, Mapping) else 0,
        }
        for index, entry in enumerate(entries)
    ]
    accepted = sum(1 for point in points if point["accepted"])
    direction = "empty" if not points else "stable_accepting" if points[-1]["accepted"] and accepted == len(points) else "latest_accepted" if points[-1]["accepted"] else "latest_blocked"
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_TREND_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_trend",
        "points": points,
        "summary": {
            "point_count": len(points),
            "accepted_count": accepted,
            "blocked_count": len(points) - accepted,
            "direction": direction,
            "problem_count_total": sum(point["problem_count"] for point in points),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_TREND_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_trend"]
