from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_build_snapshot import build_qt_runtime_build_snapshot
from .gui_qt_runtime_build_steps import build_qt_runtime_build_plan
from .gui_qt_runtime_build_validator import validate_qt_runtime_build_plan

QT_RUNTIME_BOOTSTRAP_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_bootstrap_plan(desktop_integration_plan: Mapping[str, Any]) -> dict[str, object]:
    """Prepare the future Qt runtime bootstrap from the desktop integration plan.

    This still does not import PySide6 or open a QApplication. It provides the
    next safe handoff: runtime widget plan -> deterministic build steps ->
    validation -> snapshot.
    """

    runtime_widget_plan = _mapping(desktop_integration_plan.get("runtime_widget_plan"))
    build_plan = build_qt_runtime_build_plan(runtime_widget_plan)
    validation = validate_qt_runtime_build_plan(build_plan)
    snapshot = build_qt_runtime_build_snapshot(build_plan)
    desktop_summary = _mapping(desktop_integration_plan.get("summary"))
    build_summary = _mapping(build_plan.get("summary"))
    ready = bool(validation.get("valid")) and bool(desktop_integration_plan.get("ready", True))
    return {
        "schema_version": QT_RUNTIME_BOOTSTRAP_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_bootstrap_plan",
        "active_page_id": desktop_integration_plan.get("active_page_id") or desktop_summary.get("active_page_id"),
        "runtime_widget_plan_ready": bool(desktop_integration_plan.get("ready", True)),
        "build_plan": build_plan,
        "validation": validation,
        "snapshot": snapshot,
        "summary": {
            "active_page_id": desktop_integration_plan.get("active_page_id") or desktop_summary.get("active_page_id"),
            "build_step_count": build_summary.get("step_count", 0),
            "build_node_count": build_summary.get("node_count", 0),
            "sensitive_step_count": build_summary.get("sensitive_step_count", 0),
            "unsupported_component_count": build_summary.get("unsupported_component_count", 0),
            "problem_count": validation.get("problem_count", 0),
            "snapshot_hash": snapshot.get("payload_hash"),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready": ready,
    }


__all__ = ["QT_RUNTIME_BOOTSTRAP_PLAN_SCHEMA_VERSION", "build_qt_runtime_bootstrap_plan"]
