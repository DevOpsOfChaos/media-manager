from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_STEP_INDEX_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _step_id(step: Mapping[str, Any], index: int) -> str:
    return _text(step.get("step_id"), f"step-{index + 1}")


def build_qt_runtime_step_index(build_plan: Mapping[str, Any]) -> dict[str, object]:
    """Index deterministic runtime build steps without importing PySide6.

    The index is used by later runtime diagnostics and readiness checks. It is
    intentionally pure data: no QApplication, no widget creation, no command
    execution.
    """

    steps = [step for step in _list(build_plan.get("steps")) if isinstance(step, Mapping)]
    by_operation: dict[str, dict[str, object]] = {}
    by_node: dict[str, dict[str, object]] = {}
    step_ids: set[str] = set()
    duplicate_step_ids: list[str] = []
    previous_order = 0
    order_is_monotonic = True
    sequence: list[dict[str, object]] = []

    for index, step in enumerate(steps):
        sid = _step_id(step, index)
        if sid in step_ids and sid not in duplicate_step_ids:
            duplicate_step_ids.append(sid)
        step_ids.add(sid)

        order = int(step.get("order") or index + 1)
        if order < previous_order:
            order_is_monotonic = False
        previous_order = order

        operation = _text(step.get("operation"), "unknown")
        node_id = _text(step.get("node_id"))
        parent_id = _text(step.get("parent_id"))

        operation_entry = by_operation.setdefault(operation, {"count": 0, "step_ids": []})
        operation_entry["count"] = int(operation_entry["count"]) + 1
        operation_entry["step_ids"] = [*list(operation_entry["step_ids"]), sid]

        if node_id:
            node_entry = by_node.setdefault(
                node_id,
                {
                    "node_id": node_id,
                    "parent_id": parent_id or None,
                    "operations": [],
                    "step_ids": [],
                    "sensitive": False,
                    "local_only": False,
                    "deferred_execution_count": 0,
                },
            )
            if parent_id and not node_entry.get("parent_id"):
                node_entry["parent_id"] = parent_id
            node_entry["operations"] = [*list(node_entry["operations"]), operation]
            node_entry["step_ids"] = [*list(node_entry["step_ids"]), sid]
            node_entry["sensitive"] = bool(node_entry.get("sensitive")) or bool(step.get("sensitive")) or operation == "mark_sensitive"
            node_entry["local_only"] = bool(node_entry.get("local_only")) or bool(step.get("local_only"))
            if step.get("execute_policy") == "deferred":
                node_entry["deferred_execution_count"] = int(node_entry["deferred_execution_count"]) + 1

        sequence.append(
            {
                "step_id": sid,
                "order": order,
                "operation": operation,
                "node_id": node_id or None,
                "parent_id": parent_id or None,
                "local_only": bool(step.get("local_only")),
                "execute_policy": _text(step.get("execute_policy"), "none"),
            }
        )

    summary = {
        "schema_version": QT_RUNTIME_STEP_INDEX_SCHEMA_VERSION,
        "step_count": len(steps),
        "node_count": len(by_node),
        "operation_count": len(by_operation),
        "create_widget_count": int(by_operation.get("create_widget", {}).get("count", 0)),
        "attach_child_count": int(by_operation.get("attach_child", {}).get("count", 0)),
        "mark_sensitive_count": int(by_operation.get("mark_sensitive", {}).get("count", 0)),
        "deferred_execution_count": sum(1 for item in sequence if item.get("execute_policy") == "deferred"),
        "local_only_step_count": sum(1 for item in sequence if item.get("local_only")),
        "order_is_monotonic": order_is_monotonic,
        "duplicate_step_ids": sorted(duplicate_step_ids),
        "duplicate_step_id_count": len(duplicate_step_ids),
    }
    return {
        "schema_version": QT_RUNTIME_STEP_INDEX_SCHEMA_VERSION,
        "kind": "qt_runtime_step_index",
        "root_id": build_plan.get("root_id"),
        "by_operation": by_operation,
        "by_node": by_node,
        "sequence": sequence,
        "summary": summary,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def summarize_qt_runtime_step_index(index: Mapping[str, Any]) -> str:
    summary = _mapping(index.get("summary"))
    return "\n".join(
        [
            "Qt runtime step index",
            f"  Steps: {summary.get('step_count', 0)}",
            f"  Nodes: {summary.get('node_count', 0)}",
            f"  Operations: {summary.get('operation_count', 0)}",
            f"  Sensitive markers: {summary.get('mark_sensitive_count', 0)}",
            f"  Deferred execution: {summary.get('deferred_execution_count', 0)}",
            f"  Order monotonic: {summary.get('order_is_monotonic')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_STEP_INDEX_SCHEMA_VERSION",
    "build_qt_runtime_step_index",
    "summarize_qt_runtime_step_index",
]
