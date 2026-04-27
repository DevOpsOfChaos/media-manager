from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_HISTORY_SCHEMA_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_qt_runtime_smoke_desktop_result_history_entry(
    report: Mapping[str, object],
    *,
    run_id: str = "runtime-smoke-manual",
    recorded_at_utc: str | None = None,
) -> dict[str, object]:
    summary = report.get("summary") if isinstance(report.get("summary"), Mapping) else {}
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_HISTORY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_history_entry",
        "run_id": run_id,
        "recorded_at_utc": recorded_at_utc or _now(),
        "accepted": bool(report.get("accepted")),
        "decision": summary.get("decision"),
        "result_count": int(summary.get("result_count") or 0),
        "failed_required_count": int(summary.get("failed_required_count") or 0),
        "missing_required_count": int(summary.get("missing_required_count") or 0),
        "problem_count": int(summary.get("problem_count") or 0),
        "local_only": True,
    }


def build_qt_runtime_smoke_desktop_result_history(entries: list[Mapping[str, object]] | None = None) -> dict[str, object]:
    rows = [dict(entry) for entry in (entries or []) if isinstance(entry, Mapping)]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_HISTORY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_history",
        "entries": rows,
        "summary": {
            "entry_count": len(rows),
            "accepted_count": sum(1 for row in rows if row.get("accepted") is True),
            "blocked_count": sum(1 for row in rows if row.get("accepted") is False),
            "problem_count_total": sum(int(row.get("problem_count") or 0) for row in rows),
            "local_only": True,
            "opens_window": False,
            "executes_commands": False,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = [
    "QT_RUNTIME_SMOKE_DESKTOP_RESULT_HISTORY_SCHEMA_VERSION",
    "build_qt_runtime_smoke_desktop_result_history",
    "build_qt_runtime_smoke_desktop_result_history_entry",
]
