from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_RESULT_MERGE_SCHEMA_VERSION = "1.0"


def merge_qt_runtime_smoke_desktop_acceptance_results(
    current_bundle: Mapping[str, Any],
    previous_entries: list[Mapping[str, Any]] | None = None,
) -> dict[str, object]:
    rows = [dict(entry) for entry in (previous_entries or []) if isinstance(entry, Mapping)]
    current = {
        "accepted": bool(current_bundle.get("accepted")),
        "decision": current_bundle.get("summary", {}).get("decision") if isinstance(current_bundle.get("summary"), Mapping) else None,
        "problem_count": current_bundle.get("summary", {}).get("problem_count", 0) if isinstance(current_bundle.get("summary"), Mapping) else 0,
        "source": "current",
    }
    rows.append(current)
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_RESULT_MERGE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_result_merge",
        "entries": rows,
        "summary": {
            "entry_count": len(rows),
            "accepted_count": sum(1 for row in rows if row.get("accepted") is True),
            "current_accepted": current["accepted"],
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_RESULT_MERGE_SCHEMA_VERSION", "merge_qt_runtime_smoke_desktop_acceptance_results"]
