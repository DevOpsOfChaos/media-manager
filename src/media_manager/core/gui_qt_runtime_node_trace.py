from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_step_index import build_qt_runtime_step_index

QT_RUNTIME_NODE_TRACE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_qt_runtime_node_trace(build_plan: Mapping[str, Any], node_id: str) -> dict[str, object]:
    """Return the ordered build trace for one runtime node."""

    target = _text(node_id, "node")
    index = build_qt_runtime_step_index(build_plan)
    sequence = [
        item
        for item in _list(index.get("sequence"))
        if isinstance(item, Mapping) and item.get("node_id") == target
    ]
    node_entry = _mapping(_mapping(index.get("by_node")).get(target))
    operations = [str(item.get("operation")) for item in sequence]
    return {
        "schema_version": QT_RUNTIME_NODE_TRACE_SCHEMA_VERSION,
        "kind": "qt_runtime_node_trace",
        "node_id": target,
        "parent_id": node_entry.get("parent_id"),
        "step_count": len(sequence),
        "step_ids": [item.get("step_id") for item in sequence],
        "operations": operations,
        "creates_widget": "create_widget" in operations,
        "attached_to_parent": "attach_child" in operations or not node_entry.get("parent_id"),
        "marked_sensitive": "mark_sensitive" in operations,
        "sensitive": bool(node_entry.get("sensitive")),
        "local_only": bool(node_entry.get("local_only")),
        "deferred_execution_count": int(node_entry.get("deferred_execution_count") or 0),
    }


def build_qt_runtime_sensitive_node_traces(build_plan: Mapping[str, Any]) -> dict[str, object]:
    """Collect traces for all nodes that are sensitive or explicitly local-only."""

    index = build_qt_runtime_step_index(build_plan)
    nodes = _mapping(index.get("by_node"))
    traces = [
        build_qt_runtime_node_trace(build_plan, node_id)
        for node_id, node in sorted(nodes.items())
        if isinstance(node, Mapping) and (node.get("sensitive") or node.get("local_only"))
    ]
    return {
        "schema_version": QT_RUNTIME_NODE_TRACE_SCHEMA_VERSION,
        "kind": "qt_runtime_sensitive_node_traces",
        "traces": traces,
        "summary": {
            "trace_count": len(traces),
            "marked_sensitive_count": sum(1 for trace in traces if trace.get("marked_sensitive")),
            "local_only_count": sum(1 for trace in traces if trace.get("local_only")),
            "deferred_execution_count": sum(int(trace.get("deferred_execution_count") or 0) for trace in traces),
        },
    }


__all__ = [
    "QT_RUNTIME_NODE_TRACE_SCHEMA_VERSION",
    "build_qt_runtime_node_trace",
    "build_qt_runtime_sensitive_node_traces",
]
