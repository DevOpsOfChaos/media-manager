from __future__ import annotations

from typing import Any, Mapping

from .gui_command_queue import build_command_queue
from .gui_job_history import build_job_history
from .gui_log_stream_model import build_log_stream
from .gui_run_monitor_model import build_monitor_tabs, build_run_monitor_state

EXECUTION_DASHBOARD_SCHEMA_VERSION = "1.0"


def build_execution_dashboard(
    *,
    queue: Mapping[str, Any] | None = None,
    log_stream: Mapping[str, Any] | None = None,
    history: Mapping[str, Any] | None = None,
    active_job: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    resolved_queue = dict(queue) if isinstance(queue, Mapping) else build_command_queue()
    resolved_logs = dict(log_stream) if isinstance(log_stream, Mapping) else build_log_stream()
    resolved_history = dict(history) if isinstance(history, Mapping) else build_job_history()
    monitor = build_run_monitor_state(active_job=active_job, queue=resolved_queue, log_stream=resolved_logs, history=resolved_history)
    status = monitor.get("status")
    return {
        "schema_version": EXECUTION_DASHBOARD_SCHEMA_VERSION,
        "kind": "gui_execution_dashboard",
        "status": status,
        "monitor": monitor,
        "tabs": build_monitor_tabs(),
        "queue": resolved_queue,
        "logs": resolved_logs,
        "history": resolved_history,
        "safe_execution_notice": "The GUI models prepare and monitor command execution, but do not execute commands directly.",
        "requires_attention": status == "attention" or bool(resolved_logs.get("has_errors")),
    }


__all__ = ["EXECUTION_DASHBOARD_SCHEMA_VERSION", "build_execution_dashboard"]
