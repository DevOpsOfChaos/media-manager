from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_render_tree import QT_RENDER_TREE_NODE_KIND, collect_render_node_ids, summarize_render_tree, walk_render_tree

RENDER_TREE_VALIDATOR_SCHEMA_VERSION = "1.0"

_FORBIDDEN_RUNTIME_KEYS = {
    "qt_object",
    "widget_instance",
    "qwidget",
    "signal_instance",
    "callback",
    "callable",
}


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _contains_runtime_value(value: object) -> bool:
    if callable(value):
        return True
    if isinstance(value, Mapping):
        return any(str(key).lower() in _FORBIDDEN_RUNTIME_KEYS or _contains_runtime_value(raw) for key, raw in value.items())
    if isinstance(value, list):
        return any(_contains_runtime_value(item) for item in value)
    return False


def validate_render_tree(root: Mapping[str, Any]) -> dict[str, object]:
    """Validate that a render tree is safe to consume in headless tests.

    This checks structure and safety policy only. It intentionally does not
    validate visual accuracy or instantiate any Qt/PySide6 objects.
    """

    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(root, Mapping) or not root:
        errors.append("missing_root")
        return {
            "schema_version": RENDER_TREE_VALIDATOR_SCHEMA_VERSION,
            "kind": "qt_render_tree_validation",
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "summary": {},
        }

    nodes = walk_render_tree(root)
    seen: set[str] = set()
    duplicates: list[str] = []
    for node in nodes:
        node_id = str(node.get("id") or "")
        if not node_id:
            errors.append("node_missing_id")
        elif node_id in seen:
            duplicates.append(node_id)
        seen.add(node_id)
        if node.get("kind") != QT_RENDER_TREE_NODE_KIND:
            errors.append(f"node_has_invalid_kind:{node_id or '<missing>'}")
        if not node.get("component"):
            errors.append(f"node_missing_component:{node_id or '<missing>'}")
        if node.get("executes_immediately"):
            errors.append(f"node_executes_immediately:{node_id or '<missing>'}")
        if _contains_runtime_value(node.get("props")) or _contains_runtime_value(node.get("bindings")):
            errors.append(f"node_contains_runtime_value:{node_id or '<missing>'}")
        expected_child_count = len(_list(node.get("children")))
        if int(node.get("child_count", expected_child_count) or 0) != expected_child_count:
            warnings.append(f"node_child_count_mismatch:{node_id or '<missing>'}")
    for duplicate in sorted(set(duplicates)):
        errors.append(f"duplicate_node_id:{duplicate}")
    summary = summarize_render_tree(root)
    if int(summary.get("node_count", 0) or 0) <= 0:
        errors.append("empty_render_tree")
    return {
        "schema_version": RENDER_TREE_VALIDATOR_SCHEMA_VERSION,
        "kind": "qt_render_tree_validation",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "duplicate_ids": sorted(set(duplicates)),
        "node_ids": collect_render_node_ids(root),
        "summary": summary,
    }


def render_tree_is_safe(root: Mapping[str, Any]) -> bool:
    validation = validate_render_tree(root)
    return bool(validation.get("valid"))


__all__ = ["RENDER_TREE_VALIDATOR_SCHEMA_VERSION", "render_tree_is_safe", "validate_render_tree"]
