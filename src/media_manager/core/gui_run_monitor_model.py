from __future__ import annotations

from typing import Any, Mapping, Sequence

RUN_MONITOR_SCHEMA_VERSION = "1.0"


def build_run_monitor_state(
    *,
    active_job: Mapping[str, Any] | None = None,
    queue: Mapping[str, Any] | None = None,
    log_stream: Mapping[str, Any] | None = None,
    history: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    queued = queue.get("summary", {}).get("status_summary", {}).get("queued", 0) if isinstance(queue, Mapping) else 0
    running = 1 if active_job and active_job.get("status") == "running" else 0
    error_logs = log_stream.get("level_summary", {}).get("error", 0) if isinstance(log_stream, Mapping) else 0
    return {
        "schema_version": RUN_MONITOR_SCHEMA_VERSION,
        "kind": "gui_run_monitor_state",
        "active_job": dict(active_job) if isinstance(active_job, Mapping) else None,
        "queue_summary": queue.get("summary", {}) if isinstance(queue, Mapping) else {},
        "log_summary": {"error_count": error_logs, "entry_count": log_stream.get("entry_count", 0) if isinstance(log_stream, Mapping) else 0},
        "history_summary": history.get("summary", {}) if isinstance(history, Mapping) else {},
        "status": "running" if running else "queued" if queued else "attention" if error_logs else "idle",
        "can_start_next": running == 0 and queued > 0,
    }


def build_monitor_tabs(*, include_history: bool = True) -> list[dict[str, object]]:
    tabs = [
        {"id": "queue", "label": "Queue", "enabled": True},
        {"id": "logs", "label": "Logs", "enabled": True},
        {"id": "result", "label": "Result", "enabled": True},
    ]
    if include_history:
        tabs.append({"id": "history", "label": "History", "enabled": True})
    return tabs


__all__ = ["RUN_MONITOR_SCHEMA_VERSION", "build_monitor_tabs", "build_run_monitor_state"]
