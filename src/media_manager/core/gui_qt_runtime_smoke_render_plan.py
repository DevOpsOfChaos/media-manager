from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_RENDER_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _walk(node: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    nodes = [node]
    for child in _list(node.get("children")):
        if isinstance(child, Mapping):
            nodes.extend(_walk(child))
    return nodes


def build_qt_runtime_smoke_render_plan(widget_tree: Mapping[str, Any], layout_plan: Mapping[str, Any] | None = None) -> dict[str, object]:
    root = _mapping(widget_tree.get("root"))
    layout = _mapping(layout_plan)
    placements = {str(item.get("section_id")): dict(item) for item in _list(layout.get("placements")) if isinstance(item, Mapping)}
    steps: list[dict[str, object]] = []
    for index, node in enumerate(_walk(root)):
        node_id = str(node.get("id") or f"node-{index + 1}")
        steps.append(
            {
                "step_id": f"render-{node_id}",
                "order": index + 1,
                "node_id": node_id,
                "component": node.get("component"),
                "qt_widget": node.get("qt_widget"),
                "layout": node.get("layout"),
                "role": node.get("role"),
                "placement": placements.get(node_id),
                "sensitive": bool(node.get("sensitive")),
                "executes_immediately": False,
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_RENDER_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_render_plan",
        "page_id": widget_tree.get("page_id"),
        "steps": steps,
        "summary": {
            "render_step_count": len(steps),
            "sensitive_step_count": sum(1 for step in steps if step.get("sensitive")),
            "executable_step_count": 0,
            "placed_step_count": sum(1 for step in steps if step.get("placement")),
            "opens_window": False,
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_RENDER_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_render_plan"]
