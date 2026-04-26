from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

QT_RENDER_TREE_SCHEMA_VERSION = "1.0"
QT_RENDER_TREE_NODE_KIND = "qt_render_tree_node"


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _safe_id(value: object, fallback: str = "node") -> str:
    text = _text(value, fallback).lower().replace("_", "-").replace(" ", "-")
    allowed = []
    previous_dash = False
    for char in text:
        if char.isalnum():
            allowed.append(char)
            previous_dash = False
        elif not previous_dash:
            allowed.append("-")
            previous_dash = True
    normalized = "".join(allowed).strip("-")
    return normalized or fallback


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _plain_props(value: Mapping[str, Any] | None) -> dict[str, object]:
    props: dict[str, object] = {}
    for key, raw in dict(value or {}).items():
        if callable(raw):
            continue
        if isinstance(raw, Mapping):
            props[str(key)] = _plain_props(raw)
        elif isinstance(raw, list):
            props[str(key)] = [dict(item) if isinstance(item, Mapping) else item for item in raw if not callable(item)]
        else:
            props[str(key)] = raw
    return props


def build_render_node(
    node_id: str,
    component: str,
    *,
    role: str = "",
    props: Mapping[str, Any] | None = None,
    children: Iterable[Mapping[str, Any]] = (),
    bindings: Mapping[str, Any] | None = None,
    sensitive: bool = False,
    executes_immediately: bool = False,
) -> dict[str, object]:
    """Build one declarative Qt render-tree node without importing Qt.

    The payload is intentionally plain JSON-like data. Runtime code can later
    turn these nodes into PySide6 widgets, while tests can keep validating the
    contract headlessly.
    """

    child_list = [dict(item) for item in children if isinstance(item, Mapping)]
    return {
        "schema_version": QT_RENDER_TREE_SCHEMA_VERSION,
        "kind": QT_RENDER_TREE_NODE_KIND,
        "id": _safe_id(node_id),
        "component": _text(component, "Container"),
        "role": _text(role, component),
        "props": _plain_props(props),
        "bindings": _plain_props(bindings),
        "children": child_list,
        "child_count": len(child_list),
        "sensitive": bool(sensitive),
        "executes_immediately": bool(executes_immediately),
    }


def walk_render_tree(root: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    nodes: list[Mapping[str, Any]] = []
    stack: list[Mapping[str, Any]] = [root]
    while stack:
        node = stack.pop()
        if not isinstance(node, Mapping):
            continue
        nodes.append(node)
        children = [child for child in _as_list(node.get("children")) if isinstance(child, Mapping)]
        stack.extend(reversed(children))
    return nodes


def summarize_render_tree(root: Mapping[str, Any]) -> dict[str, object]:
    nodes = walk_render_tree(root)
    component_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    sensitive_count = 0
    executable_count = 0
    leaf_count = 0
    max_depth = 0

    def visit(node: Mapping[str, Any], depth: int) -> None:
        nonlocal max_depth, sensitive_count, executable_count, leaf_count
        max_depth = max(max_depth, depth)
        component = _text(node.get("component"), "Container")
        role = _text(node.get("role"), component)
        component_counts[component] = component_counts.get(component, 0) + 1
        role_counts[role] = role_counts.get(role, 0) + 1
        sensitive_count += 1 if node.get("sensitive") else 0
        executable_count += 1 if node.get("executes_immediately") else 0
        children = [child for child in _as_list(node.get("children")) if isinstance(child, Mapping)]
        if not children:
            leaf_count += 1
        for child in children:
            visit(child, depth + 1)

    if isinstance(root, Mapping):
        visit(root, 0)

    return {
        "schema_version": QT_RENDER_TREE_SCHEMA_VERSION,
        "node_count": len(nodes),
        "leaf_count": leaf_count,
        "max_depth": max_depth,
        "sensitive_node_count": sensitive_count,
        "executable_node_count": executable_count,
        "component_summary": dict(sorted(component_counts.items())),
        "role_summary": dict(sorted(role_counts.items())),
    }


def collect_render_node_ids(root: Mapping[str, Any]) -> list[str]:
    return [_text(node.get("id"), "") for node in walk_render_tree(root)]


def build_leaf_node(node_id: str, component: str, *, role: str = "", props: Mapping[str, Any] | None = None, sensitive: bool = False) -> dict[str, object]:
    return build_render_node(node_id, component, role=role or component, props=props, sensitive=sensitive)


__all__ = [
    "QT_RENDER_TREE_NODE_KIND",
    "QT_RENDER_TREE_SCHEMA_VERSION",
    "build_leaf_node",
    "build_render_node",
    "collect_render_node_ids",
    "summarize_render_tree",
    "walk_render_tree",
]
