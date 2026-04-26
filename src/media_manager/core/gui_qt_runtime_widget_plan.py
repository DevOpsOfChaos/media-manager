from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_render_tree import summarize_render_tree, walk_render_tree
from .gui_qt_runtime_component_catalog import build_qt_runtime_component_catalog, lookup_qt_component_spec

QT_RUNTIME_WIDGET_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _runtime_node(node: Mapping[str, Any], *, catalog: Mapping[str, Any]) -> dict[str, object]:
    component = _text(node.get("component"), "Container")
    spec = lookup_qt_component_spec(component, catalog)
    children = [
        _runtime_node(child, catalog=catalog)
        for child in _list(node.get("children"))
        if isinstance(child, Mapping)
    ]
    node_id = _text(node.get("id"), "node")
    return {
        "id": node_id,
        "source_component": component,
        "supported_component": bool(spec.get("supported")),
        "qt_widget": spec.get("qt_widget"),
        "layout": spec.get("layout"),
        "role": node.get("role") or spec.get("role"),
        "object_name": f"MediaManager_{component}",
        "props": dict(_mapping(node.get("props"))),
        "bindings": dict(_mapping(node.get("bindings"))),
        "children": children,
        "child_count": len(children),
        "sensitive": bool(node.get("sensitive")),
        "execute_policy": "deferred" if node.get("executes_immediately") else "none",
    }


def _collect_runtime_nodes(root: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    nodes: list[Mapping[str, Any]] = []
    stack: list[Mapping[str, Any]] = [root]
    while stack:
        node = stack.pop()
        if not isinstance(node, Mapping):
            continue
        nodes.append(node)
        stack.extend(reversed([child for child in _list(node.get("children")) if isinstance(child, Mapping)]))
    return nodes


def summarize_runtime_widget_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    root = _mapping(plan.get("root"))
    nodes = _collect_runtime_nodes(root) if root else []
    unsupported = sorted({_text(node.get("source_component")) for node in nodes if node.get("supported_component") is False})
    qt_widgets = sorted({_text(node.get("qt_widget")) for node in nodes if node.get("qt_widget")})
    return {
        "schema_version": QT_RUNTIME_WIDGET_PLAN_SCHEMA_VERSION,
        "node_count": len(nodes),
        "unsupported_components": unsupported,
        "unsupported_component_count": len(unsupported),
        "qt_widgets": qt_widgets,
        "sensitive_node_count": sum(1 for node in nodes if node.get("sensitive")),
        "deferred_execution_count": sum(1 for node in nodes if node.get("execute_policy") == "deferred"),
    }


def build_qt_runtime_widget_plan(render_root: Mapping[str, Any]) -> dict[str, object]:
    """Map a render tree to a PySide6 runtime construction plan without importing PySide6."""

    catalog = build_qt_runtime_component_catalog()
    root = _runtime_node(render_root, catalog=catalog)
    source_summary = summarize_render_tree(render_root)
    summary = summarize_runtime_widget_plan({"root": root})
    return {
        "schema_version": QT_RUNTIME_WIDGET_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_widget_plan",
        "root": root,
        "component_catalog": catalog,
        "source_summary": source_summary,
        "summary": summary,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
        },
    }


def collect_runtime_widget_ids(plan: Mapping[str, Any]) -> list[str]:
    return [_text(node.get("id")) for node in _collect_runtime_nodes(_mapping(plan.get("root")))]


__all__ = [
    "QT_RUNTIME_WIDGET_PLAN_SCHEMA_VERSION",
    "build_qt_runtime_widget_plan",
    "collect_runtime_widget_ids",
    "summarize_runtime_widget_plan",
]
