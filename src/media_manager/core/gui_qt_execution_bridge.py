from __future__ import annotations

from collections.abc import Mapping
from typing import Any

EXECUTION_BRIDGE_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, default: str = "") -> str:
    return str(value) if value is not None else default


def build_execution_control_panel(execution_dashboard: Mapping[str, Any]) -> dict[str, Any]:
    monitor = _as_mapping(execution_dashboard.get("monitor"))
    queue = _as_mapping(execution_dashboard.get("queue"))
    active_job = _as_mapping(monitor.get("active_job"))
    status = _text(monitor.get("status"), "idle")
    controls = [
        {"id": "start_next", "label": "Start next", "enabled": status in {"idle", "queued"} and int(queue.get("queued_count", 0) or 0) > 0, "requires_confirmation": False},
        {"id": "cancel_active", "label": "Cancel active", "enabled": bool(active_job), "requires_confirmation": True},
        {"id": "clear_finished", "label": "Clear finished", "enabled": int(_as_mapping(execution_dashboard.get("history")).get("finished_count", 0) or 0) > 0, "requires_confirmation": False},
    ]
    return {
        "schema_version": EXECUTION_BRIDGE_SCHEMA_VERSION,
        "kind": "execution_control_panel",
        "status": status,
        "active_job_id": active_job.get("job_id"),
        "controls": controls,
        "enabled_control_count": sum(1 for item in controls if item["enabled"]),
    }


def execution_control_to_intent(control: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": EXECUTION_BRIDGE_SCHEMA_VERSION,
        "kind": "execution_control_intent",
        "control_id": control.get("id"),
        "enabled": bool(control.get("enabled")),
        "requires_confirmation": bool(control.get("requires_confirmation")),
        "executes_immediately": False,
    }


def build_log_table_rows(execution_dashboard: Mapping[str, Any], *, limit: int = 100) -> list[dict[str, Any]]:
    logs = _as_mapping(execution_dashboard.get("logs"))
    entries = [item for item in _as_list(logs.get("entries")) if isinstance(item, Mapping)]
    return [
        {
            "level": item.get("level"),
            "message": item.get("message"),
            "source": item.get("source"),
            "created_at": item.get("created_at"),
        }
        for item in entries[: max(0, limit)]
    ]


__all__ = ["EXECUTION_BRIDGE_SCHEMA_VERSION", "build_execution_control_panel", "build_log_table_rows", "execution_control_to_intent"]
