from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION = "1.0"
QT_RUNTIME_BUILD_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _safe_step_id(prefix: str, node_id: object) -> str:
    raw = _text(node_id, "node").lower().replace("_", "-").replace(" ", "-")
    cleaned: list[str] = []
    previous_dash = False
    for char in raw:
        if char.isalnum():
            cleaned.append(char)
            previous_dash = False
        elif not previous_dash:
            cleaned.append("-")
            previous_dash = True
    normalized = "".join(cleaned).strip("-") or "node"
    return f"{prefix}-{normalized}"


def _walk_runtime_nodes(root: Mapping[str, Any], *, parent_id: str | None = None, depth: int = 0) -> list[tuple[Mapping[str, Any], str | None, int]]:
    result: list[tuple[Mapping[str, Any], str | None, int]] = [(root, parent_id, depth)]
    node_id = _text(root.get("id"), "node")
    for child in _list(root.get("children")):
        if isinstance(child, Mapping):
            result.extend(_walk_runtime_nodes(child, parent_id=node_id, depth=depth + 1))
    return result


def _create_step(node: Mapping[str, Any], *, parent_id: str | None, depth: int, order: int) -> dict[str, object]:
    node_id = _text(node.get("id"), "node")
    qt_widget = _text(node.get("qt_widget"), "QWidget")
    return {
        "schema_version": QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION,
        "step_id": _safe_step_id("create", node_id),
        "order": order,
        "operation": "create_widget",
        "node_id": node_id,
        "parent_id": parent_id,
        "depth": depth,
        "source_component": node.get("source_component"),
        "qt_widget": qt_widget,
        "object_name": node.get("object_name") or f"MediaManager_{_text(node.get('source_component'), 'Widget')}",
        "supported_component": bool(node.get("supported_component", True)),
        "sensitive": bool(node.get("sensitive")),
        "execute_policy": _text(node.get("execute_policy"), "none"),
        "local_only": bool(node.get("sensitive")),
    }


def _layout_step(node: Mapping[str, Any], *, order: int) -> dict[str, object] | None:
    layout = _text(node.get("layout"))
    if not layout:
        return None
    node_id = _text(node.get("id"), "node")
    return {
        "schema_version": QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION,
        "step_id": _safe_step_id("layout", node_id),
        "order": order,
        "operation": "configure_layout",
        "node_id": node_id,
        "layout": layout,
        "execute_policy": "none",
        "local_only": bool(node.get("sensitive")),
    }


def _props_step(node: Mapping[str, Any], *, order: int) -> dict[str, object] | None:
    props = dict(_mapping(node.get("props")))
    if not props:
        return None
    node_id = _text(node.get("id"), "node")
    return {
        "schema_version": QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION,
        "step_id": _safe_step_id("props", node_id),
        "order": order,
        "operation": "apply_props",
        "node_id": node_id,
        "prop_keys": sorted(str(key) for key in props),
        "prop_count": len(props),
        "execute_policy": "none",
        "local_only": bool(node.get("sensitive")),
    }


def _bindings_step(node: Mapping[str, Any], *, order: int) -> dict[str, object] | None:
    bindings = dict(_mapping(node.get("bindings")))
    if not bindings:
        return None
    node_id = _text(node.get("id"), "node")
    return {
        "schema_version": QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION,
        "step_id": _safe_step_id("bindings", node_id),
        "order": order,
        "operation": "connect_bindings",
        "node_id": node_id,
        "binding_keys": sorted(str(key) for key in bindings),
        "binding_count": len(bindings),
        "execute_policy": "deferred",
        "local_only": bool(node.get("sensitive")),
    }


def _sensitive_step(node: Mapping[str, Any], *, order: int) -> dict[str, object] | None:
    if not bool(node.get("sensitive")):
        return None
    node_id = _text(node.get("id"), "node")
    return {
        "schema_version": QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION,
        "step_id": _safe_step_id("sensitive", node_id),
        "order": order,
        "operation": "mark_sensitive",
        "node_id": node_id,
        "privacy_policy": "local_only",
        "allows_export": False,
        "execute_policy": "none",
        "local_only": True,
    }


def _attach_step(node: Mapping[str, Any], *, parent_id: str | None, order: int) -> dict[str, object] | None:
    if not parent_id:
        return None
    node_id = _text(node.get("id"), "node")
    return {
        "schema_version": QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION,
        "step_id": _safe_step_id("attach", node_id),
        "order": order,
        "operation": "attach_child",
        "node_id": node_id,
        "parent_id": parent_id,
        "execute_policy": "none",
        "local_only": bool(node.get("sensitive")),
    }


def build_runtime_build_steps(runtime_widget_plan: Mapping[str, Any]) -> list[dict[str, object]]:
    """Create deterministic widget-construction steps from a runtime widget plan.

    The result is still pure data. It imports no PySide6, opens no window, and
    never executes command bindings. Sensitive People Review nodes receive an
    explicit local-only marker step.
    """

    root = _mapping(runtime_widget_plan.get("root"))
    if not root:
        return []
    steps: list[dict[str, object]] = []

    def add(step: dict[str, object] | None) -> None:
        if step is None:
            return
        step["order"] = len(steps) + 1
        steps.append(step)

    for node, parent_id, depth in _walk_runtime_nodes(root):
        add(_create_step(node, parent_id=parent_id, depth=depth, order=len(steps) + 1))
        add(_layout_step(node, order=len(steps) + 1))
        add(_props_step(node, order=len(steps) + 1))
        add(_bindings_step(node, order=len(steps) + 1))
        add(_sensitive_step(node, order=len(steps) + 1))
        add(_attach_step(node, parent_id=parent_id, order=len(steps) + 1))
    return steps


def summarize_runtime_build_steps(steps: list[Mapping[str, Any]]) -> dict[str, object]:
    operation_counts: dict[str, int] = {}
    node_ids = set()
    for step in steps:
        operation = _text(step.get("operation"), "unknown")
        operation_counts[operation] = operation_counts.get(operation, 0) + 1
        node_id = _text(step.get("node_id"))
        if node_id:
            node_ids.add(node_id)
    return {
        "schema_version": QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION,
        "step_count": len(steps),
        "node_count": len(node_ids),
        "operation_counts": dict(sorted(operation_counts.items())),
        "sensitive_step_count": sum(1 for step in steps if step.get("operation") == "mark_sensitive"),
        "local_only_step_count": sum(1 for step in steps if step.get("local_only")),
        "deferred_execution_count": sum(1 for step in steps if step.get("execute_policy") == "deferred"),
        "unsupported_component_count": sum(1 for step in steps if step.get("operation") == "create_widget" and step.get("supported_component") is False),
    }


def build_qt_runtime_build_plan(runtime_widget_plan: Mapping[str, Any]) -> dict[str, object]:
    steps = build_runtime_build_steps(runtime_widget_plan)
    root = _mapping(runtime_widget_plan.get("root"))
    return {
        "schema_version": QT_RUNTIME_BUILD_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_build_plan",
        "root_id": root.get("id"),
        "steps": steps,
        "summary": summarize_runtime_build_steps(steps),
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def collect_runtime_build_step_ids(plan: Mapping[str, Any]) -> list[str]:
    return [_text(step.get("step_id")) for step in _list(plan.get("steps")) if isinstance(step, Mapping)]


__all__ = [
    "QT_RUNTIME_BUILD_PLAN_SCHEMA_VERSION",
    "QT_RUNTIME_BUILD_STEPS_SCHEMA_VERSION",
    "build_qt_runtime_build_plan",
    "build_runtime_build_steps",
    "collect_runtime_build_step_ids",
    "summarize_runtime_build_steps",
]
