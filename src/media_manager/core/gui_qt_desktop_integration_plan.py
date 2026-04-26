from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_render_bridge import build_qt_render_bridge, summarize_qt_render_bridge
from .gui_qt_runtime_plan_validator import validate_qt_runtime_widget_plan
from .gui_qt_runtime_widget_plan import build_qt_runtime_widget_plan, summarize_runtime_widget_plan

QT_DESKTOP_INTEGRATION_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_desktop_integration_plan(shell_model: Mapping[str, Any]) -> dict[str, object]:
    """Build the first desktop-facing integration plan from shell model to Qt widget plan.

    This is the safe bridge between the existing model/render-tree work and the
    visible Qt runtime. It deliberately remains headless: no PySide6 import, no
    QApplication, no widgets, no command execution.
    """

    render_bridge = build_qt_render_bridge(shell_model)
    shell_tree = _mapping(render_bridge.get("shell_render_tree"))
    root = _mapping(shell_tree.get("root"))
    runtime_plan = build_qt_runtime_widget_plan(root)
    runtime_validation = validate_qt_runtime_widget_plan(runtime_plan)
    runtime_summary = summarize_runtime_widget_plan(runtime_plan)
    render_summary_text = summarize_qt_render_bridge(render_bridge)
    ready = bool(render_bridge.get("ready")) and bool(runtime_validation.get("valid"))
    return {
        "schema_version": QT_DESKTOP_INTEGRATION_PLAN_SCHEMA_VERSION,
        "kind": "qt_desktop_integration_plan",
        "active_page_id": shell_model.get("active_page_id"),
        "render_bridge": render_bridge,
        "runtime_widget_plan": runtime_plan,
        "runtime_validation": runtime_validation,
        "summary": {
            "active_page_id": shell_model.get("active_page_id"),
            "render_bridge_ready": bool(render_bridge.get("ready")),
            "runtime_plan_valid": bool(runtime_validation.get("valid")),
            "runtime_node_count": runtime_summary.get("node_count", 0),
            "unsupported_component_count": runtime_summary.get("unsupported_component_count", 0),
            "sensitive_node_count": runtime_summary.get("sensitive_node_count", 0),
            "deferred_execution_count": runtime_summary.get("deferred_execution_count", 0),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "render_bridge_summary": render_summary_text,
        "ready": ready,
    }


def summarize_qt_desktop_integration_plan(plan: Mapping[str, Any]) -> str:
    summary = _mapping(plan.get("summary"))
    capabilities = _mapping(plan.get("capabilities"))
    validation = _mapping(plan.get("runtime_validation"))
    return "\n".join(
        [
            "Qt desktop integration plan",
            f"  Active page: {plan.get('active_page_id')}",
            f"  Ready: {plan.get('ready')}",
            f"  Render bridge ready: {summary.get('render_bridge_ready')}",
            f"  Runtime nodes: {summary.get('runtime_node_count')}",
            f"  Unsupported components: {summary.get('unsupported_component_count')}",
            f"  Sensitive nodes: {summary.get('sensitive_node_count')}",
            f"  Problems: {validation.get('problem_count', 0)}",
            f"  Requires PySide6: {capabilities.get('requires_pyside6')}",
            f"  Opens window: {capabilities.get('opens_window')}",
        ]
    )


__all__ = [
    "QT_DESKTOP_INTEGRATION_PLAN_SCHEMA_VERSION",
    "build_qt_desktop_integration_plan",
    "summarize_qt_desktop_integration_plan",
]
