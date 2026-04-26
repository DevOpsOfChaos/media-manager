from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

RUN_HISTORY_WORKBENCH_SCHEMA_VERSION = "1.0"


def build_run_history_workbench(
    runs: Iterable[Mapping[str, Any]],
    *,
    status_filter: str = "all",
    limit: int = 50,
) -> dict[str, object]:
    rows = []
    for raw in runs:
        status = str(raw.get("status") or "unknown")
        if status_filter != "all" and status != status_filter:
            continue
        rows.append(
            {
                "run_id": raw.get("run_id"),
                "command": raw.get("command"),
                "status": status,
                "exit_code": raw.get("exit_code"),
                "needs_attention": raw.get("exit_code") not in (None, 0) or status in {"error", "failed", "blocked"},
                "review_candidate_count": int(raw.get("review_candidate_count", 0) or 0),
            }
        )
    truncated = len(rows) > max(0, int(limit))
    returned = rows[: max(0, int(limit))]
    return {
        "schema_version": RUN_HISTORY_WORKBENCH_SCHEMA_VERSION,
        "kind": "qt_run_history_workbench",
        "status_filter": status_filter,
        "run_count": len(rows),
        "returned_run_count": len(returned),
        "attention_count": sum(1 for row in rows if row["needs_attention"]),
        "truncated": truncated,
        "rows": returned,
        "empty_state": None if returned else {"title": "No runs", "description": "Run previews will appear here."},
    }


__all__ = ["RUN_HISTORY_WORKBENCH_SCHEMA_VERSION", "build_run_history_workbench"]
