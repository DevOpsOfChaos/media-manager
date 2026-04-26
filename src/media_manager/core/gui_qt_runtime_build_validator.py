from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_BUILD_VALIDATOR_SCHEMA_VERSION = "1.0"
_ALLOWED_OPERATIONS = {"create_widget", "configure_layout", "apply_props", "connect_bindings", "mark_sensitive", "attach_child"}
_ALLOWED_EXECUTE_POLICIES = {"none", "deferred"}


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def validate_qt_runtime_build_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    """Validate a headless Qt runtime build plan before a real Qt runtime consumes it."""

    problems: list[str] = []
    if plan.get("kind") != "qt_runtime_build_plan":
        problems.append("invalid_build_plan_kind")
    steps = [step for step in _list(plan.get("steps")) if isinstance(step, Mapping)]
    if not steps:
        problems.append("missing_build_steps")
    seen_step_ids: set[str] = set()
    created_nodes: set[str] = set()
    last_order = 0
    for index, step in enumerate(steps):
        step_id = _text(step.get("step_id"), f"step-{index + 1}")
        if step_id in seen_step_ids:
            problems.append(f"duplicate_step_id:{step_id}")
        seen_step_ids.add(step_id)
        order = int(step.get("order", index + 1) or 0)
        if order <= last_order:
            problems.append(f"non_increasing_order:{step_id}")
        last_order = order
        operation = _text(step.get("operation"))
        if operation not in _ALLOWED_OPERATIONS:
            problems.append(f"unsupported_operation:{operation or step_id}")
        execute_policy = _text(step.get("execute_policy"), "none")
        if execute_policy not in _ALLOWED_EXECUTE_POLICIES:
            problems.append(f"unsafe_execute_policy:{step_id}")
        if step.get("executes_immediately"):
            problems.append(f"executes_immediately:{step_id}")
        node_id = _text(step.get("node_id"))
        if operation == "create_widget":
            if not node_id:
                problems.append(f"missing_node_id:{step_id}")
            created_nodes.add(node_id)
            if not _text(step.get("qt_widget")):
                problems.append(f"missing_qt_widget:{step_id}")
        elif node_id and node_id not in created_nodes:
            problems.append(f"step_before_create:{step_id}")
        if operation == "attach_child":
            parent_id = _text(step.get("parent_id"))
            if not parent_id:
                problems.append(f"missing_attach_parent:{step_id}")
            elif parent_id not in created_nodes:
                problems.append(f"attach_parent_not_created:{step_id}")
        if operation == "mark_sensitive":
            if step.get("privacy_policy") != "local_only":
                problems.append(f"sensitive_not_local_only:{step_id}")
            if step.get("allows_export") is not False:
                problems.append(f"sensitive_allows_export:{step_id}")
    summary = _mapping(plan.get("summary"))
    if int(summary.get("unsupported_component_count", 0) or 0) > 0:
        problems.append("unsupported_components_present")
    return {
        "schema_version": QT_RUNTIME_BUILD_VALIDATOR_SCHEMA_VERSION,
        "valid": not problems,
        "problems": problems,
        "problem_count": len(problems),
        "step_count": len(steps),
    }


__all__ = ["QT_RUNTIME_BUILD_VALIDATOR_SCHEMA_VERSION", "validate_qt_runtime_build_plan"]
