from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .gui_qt_render_tree import summarize_render_tree, walk_render_tree

RENDER_TREE_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _node_outline(node: Mapping[str, Any]) -> dict[str, object]:
    props = _mapping(node.get("props"))
    return {
        "id": node.get("id"),
        "component": node.get("component"),
        "role": node.get("role"),
        "child_count": len(_list(node.get("children"))),
        "sensitive": bool(node.get("sensitive")),
        "executes_immediately": bool(node.get("executes_immediately")),
        "title": props.get("title"),
        "page_id": props.get("page_id"),
    }


def build_render_tree_snapshot(root: Mapping[str, Any], *, include_outline: bool = True) -> dict[str, object]:
    """Build a deterministic snapshot for tests and future visual regression manifests."""

    nodes = walk_render_tree(root)
    outline = [_node_outline(node) for node in nodes] if include_outline else []
    summary = summarize_render_tree(root)
    payload = {"summary": summary, "outline": outline}
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return {
        "schema_version": RENDER_TREE_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_render_tree_snapshot",
        "node_count": summary.get("node_count", 0),
        "sensitive_node_count": summary.get("sensitive_node_count", 0),
        "executable_node_count": summary.get("executable_node_count", 0),
        "component_summary": summary.get("component_summary", {}),
        "outline": outline,
        "payload_hash": hashlib.sha256(payload_json.encode("utf-8")).hexdigest(),
    }


def compare_render_tree_snapshots(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, object]:
    before_components = _mapping(before.get("component_summary"))
    after_components = _mapping(after.get("component_summary"))
    components = sorted({*before_components.keys(), *after_components.keys()})
    component_delta = {
        str(component): int(after_components.get(component, 0) or 0) - int(before_components.get(component, 0) or 0)
        for component in components
        if int(after_components.get(component, 0) or 0) != int(before_components.get(component, 0) or 0)
    }
    return {
        "schema_version": RENDER_TREE_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_render_tree_snapshot_diff",
        "same_hash": before.get("payload_hash") == after.get("payload_hash"),
        "node_count_delta": int(after.get("node_count", 0) or 0) - int(before.get("node_count", 0) or 0),
        "sensitive_node_delta": int(after.get("sensitive_node_count", 0) or 0) - int(before.get("sensitive_node_count", 0) or 0),
        "component_delta": component_delta,
    }


__all__ = ["RENDER_TREE_SNAPSHOT_SCHEMA_VERSION", "build_render_tree_snapshot", "compare_render_tree_snapshots"]
