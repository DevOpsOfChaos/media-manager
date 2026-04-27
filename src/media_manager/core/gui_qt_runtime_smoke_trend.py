from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_TREND_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def build_qt_runtime_smoke_trend(history: Mapping[str, Any] | list[Mapping[str, Any]], *, limit: int = 12) -> dict[str, object]:
    entries = _list(history.get("entries")) if isinstance(history, Mapping) else list(history)
    valid = [entry for entry in entries if isinstance(entry, Mapping)]
    window = valid[-max(0, int(limit)):] if limit else valid
    points = [
        {
            "index": index,
            "recorded_at_utc": entry.get("recorded_at_utc"),
            "active_page_id": entry.get("active_page_id"),
            "ready": bool(entry.get("ready_for_release_gate")),
            "problem_count": _int(entry.get("problem_count")),
            "privacy_check_count": _int(entry.get("privacy_check_count")),
            "commit_sha": str(entry.get("commit_sha") or ""),
        }
        for index, entry in enumerate(window)
    ]
    ready_count = sum(1 for point in points if point["ready"])
    latest = points[-1] if points else {}
    previous = points[-2] if len(points) >= 2 else {}
    if not points:
        direction = "empty"
    elif latest.get("ready") and previous.get("ready") is False:
        direction = "improved"
    elif latest.get("ready") is False and previous.get("ready") is True:
        direction = "regressed"
    elif latest.get("ready"):
        direction = "stable_ready" if previous else "ready"
    else:
        direction = "needs_attention"
    return {
        "schema_version": QT_RUNTIME_SMOKE_TREND_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_trend",
        "points": points,
        "summary": {
            "entry_count": len(points),
            "ready_count": ready_count,
            "not_ready_count": len(points) - ready_count,
            "latest_ready": latest.get("ready"),
            "latest_active_page_id": latest.get("active_page_id"),
            "latest_problem_count": latest.get("problem_count", 0),
            "direction": direction,
            "problem_count_total": sum(_int(point.get("problem_count")) for point in points),
            "privacy_check_count_total": sum(_int(point.get("privacy_check_count")) for point in points),
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_TREND_SCHEMA_VERSION", "build_qt_runtime_smoke_trend"]
