from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_step_index import build_qt_runtime_step_index

QT_RUNTIME_SAFETY_AUDIT_SCHEMA_VERSION = "1.0"
_ALLOWED_EXECUTE_POLICIES = {"none", "deferred"}


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def audit_qt_runtime_build_safety(build_plan: Mapping[str, Any]) -> dict[str, object]:
    """Audit runtime build steps for local-only and deferred-execution safety."""

    index = build_qt_runtime_step_index(build_plan)
    problems: list[dict[str, object]] = []
    steps = [step for step in _list(build_plan.get("steps")) if isinstance(step, Mapping)]

    sensitive_nodes = set()
    marked_sensitive_nodes = set()
    local_only_nodes = set()

    for step_index, step in enumerate(steps):
        step_id = _text(step.get("step_id"), f"step-{step_index + 1}")
        node_id = _text(step.get("node_id"))
        operation = _text(step.get("operation"), "unknown")
        execute_policy = _text(step.get("execute_policy"), "none")

        if execute_policy not in _ALLOWED_EXECUTE_POLICIES:
            problems.append(
                {
                    "code": "unsafe_execute_policy",
                    "step_id": step_id,
                    "node_id": node_id or None,
                    "execute_policy": execute_policy,
                }
            )

        if bool(step.get("sensitive")):
            sensitive_nodes.add(node_id)
        if operation == "mark_sensitive":
            marked_sensitive_nodes.add(node_id)
            sensitive_nodes.add(node_id)
            if step.get("local_only") is not True:
                problems.append({"code": "sensitive_marker_not_local_only", "step_id": step_id, "node_id": node_id})
        if step.get("local_only") is True:
            local_only_nodes.add(node_id)

    for node_id in sorted(node for node in sensitive_nodes if node):
        if node_id not in marked_sensitive_nodes:
            problems.append({"code": "missing_sensitive_marker", "node_id": node_id})
        if node_id not in local_only_nodes:
            problems.append({"code": "sensitive_node_not_local_only", "node_id": node_id})

    summary = _mapping(index.get("summary"))
    if summary.get("order_is_monotonic") is not True:
        problems.append({"code": "build_step_order_not_monotonic"})
    if int(summary.get("duplicate_step_id_count") or 0) > 0:
        problems.append({"code": "duplicate_step_ids", "step_ids": summary.get("duplicate_step_ids", [])})

    return {
        "schema_version": QT_RUNTIME_SAFETY_AUDIT_SCHEMA_VERSION,
        "kind": "qt_runtime_safety_audit",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "step_count": summary.get("step_count", 0),
            "node_count": summary.get("node_count", 0),
            "sensitive_node_count": len([node for node in sensitive_nodes if node]),
            "marked_sensitive_node_count": len([node for node in marked_sensitive_nodes if node]),
            "local_only_node_count": len([node for node in local_only_nodes if node]),
            "deferred_execution_count": summary.get("deferred_execution_count", 0),
            "unsafe_immediate_execution_count": sum(1 for problem in problems if problem.get("code") == "unsafe_execute_policy"),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SAFETY_AUDIT_SCHEMA_VERSION", "audit_qt_runtime_build_safety"]
