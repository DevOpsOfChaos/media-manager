from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DETAIL_PANEL_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_detail_panel(workbench: Mapping[str, Any]) -> dict[str, object]:
    """Build a detail panel model for the selected or current runtime smoke status."""

    trend_section = next(
        (
            section
            for section in _list(workbench.get("sections"))
            if isinstance(section, Mapping) and section.get("kind") == "trend"
        ),
        {},
    )
    trend_summary = _mapping(_mapping(trend_section).get("summary"))
    decision = _mapping(workbench.get("decision"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_DETAIL_PANEL_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_detail_panel",
        "active_page_id": workbench.get("active_page_id"),
        "title": "Runtime smoke details",
        "status": workbench.get("status"),
        "message": workbench.get("message"),
        "recommended_next_step": workbench.get("recommended_next_step"),
        "decision": {
            "id": decision.get("decision"),
            "severity": decision.get("severity"),
            "requires_user_confirmation": bool(decision.get("requires_user_confirmation", True)),
            "executes_immediately": bool(decision.get("executes_immediately", False)),
        },
        "trend": {
            "entry_count": int(trend_summary.get("entry_count") or 0),
            "direction": trend_summary.get("direction"),
            "latest_ready": trend_summary.get("latest_ready"),
            "latest_active_page_id": trend_summary.get("latest_active_page_id"),
        },
        "privacy": {
            "local_only": True,
            "network_required": False,
            "telemetry_allowed": False,
            "contains_sensitive_people_data_possible": workbench.get("active_page_id") == "people-review",
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DETAIL_PANEL_SCHEMA_VERSION", "build_qt_runtime_smoke_detail_panel"]
