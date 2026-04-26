from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_PLAN_VALIDATOR_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _walk(root: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    result: list[Mapping[str, Any]] = []
    stack: list[Mapping[str, Any]] = [root]
    while stack:
        node = stack.pop()
        if not isinstance(node, Mapping):
            continue
        result.append(node)
        stack.extend(reversed([child for child in _list(node.get("children")) if isinstance(child, Mapping)]))
    return result


def validate_qt_runtime_widget_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    problems: list[str] = []
    warnings: list[str] = []
    root = _mapping(plan.get("root"))
    if not root:
        problems.append("missing_root")
        nodes: list[Mapping[str, Any]] = []
    else:
        nodes = _walk(root)
    for node in nodes:
        if not node.get("id"):
            problems.append("node_missing_id")
        if not node.get("qt_widget"):
            problems.append(f"node_missing_qt_widget:{node.get('id')}")
        if node.get("supported_component") is False:
            warnings.append(f"unsupported_component:{node.get('source_component')}")
        if node.get("execute_policy") not in {"none", "deferred"}:
            problems.append(f"unsafe_execute_policy:{node.get('id')}")
    capabilities = _mapping(plan.get("capabilities"))
    if capabilities.get("opens_window"):
        problems.append("runtime_plan_must_not_open_window")
    if capabilities.get("requires_pyside6"):
        problems.append("runtime_plan_must_be_headless")
    if capabilities.get("executes_commands"):
        problems.append("runtime_plan_must_not_execute_commands")
    return {
        "schema_version": QT_RUNTIME_PLAN_VALIDATOR_SCHEMA_VERSION,
        "valid": not problems,
        "problems": problems,
        "problem_count": len(problems),
        "warnings": warnings,
        "warning_count": len(warnings),
        "node_count": len(nodes),
    }


__all__ = ["QT_RUNTIME_PLAN_VALIDATOR_SCHEMA_VERSION", "validate_qt_runtime_widget_plan"]
