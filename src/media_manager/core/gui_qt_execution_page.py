from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_helpers import as_list, as_mapping, as_text, compact_metrics, widget

QT_EXECUTION_PAGE_SCHEMA_VERSION = "1.0"


def build_qt_execution_page_plan(execution_dashboard: Mapping[str, Any] | None = None) -> dict[str, object]:
    dashboard = as_mapping(execution_dashboard)
    monitor = as_mapping(dashboard.get("monitor"))
    queue = as_mapping(dashboard.get("queue"))
    logs = as_mapping(dashboard.get("logs"))
    history = as_mapping(dashboard.get("history"))
    widgets = [
        widget("execution_monitor", widget_id="execution.monitor", metrics=compact_metrics(monitor), region="top"),
        widget("command_queue", widget_id="execution.queue", rows=as_list(queue.get("jobs")) or as_list(queue.get("items")), region="left"),
        widget("log_stream", widget_id="execution.logs", rows=as_list(logs.get("entries"))[:200], region="right"),
        widget("job_history", widget_id="execution.history", rows=as_list(history.get("items"))[:50], region="bottom"),
    ]
    return {
        "schema_version": QT_EXECUTION_PAGE_SCHEMA_VERSION,
        "kind": "qt_execution_page_plan",
        "page_id": "execution",
        "layout": "execution_dashboard",
        "status": as_text(monitor.get("status"), "idle"),
        "widget_count": len(widgets),
        "widgets": widgets,
    }


__all__ = ["QT_EXECUTION_PAGE_SCHEMA_VERSION", "build_qt_execution_page_plan"]
