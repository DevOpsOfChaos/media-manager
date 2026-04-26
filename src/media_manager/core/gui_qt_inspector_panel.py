from __future__ import annotations

from collections.abc import Mapping
from typing import Any

INSPECTOR_SCHEMA_VERSION = "1.0"


def _inspect_value(value: Any, *, key: str = "root", depth: int = 0, max_depth: int = 3) -> dict[str, object]:
    if isinstance(value, Mapping):
        children = []
        if depth < max_depth:
            children = [_inspect_value(child, key=str(child_key), depth=depth + 1, max_depth=max_depth) for child_key, child in list(value.items())[:20]]
        return {"key": key, "type": "object", "size": len(value), "children": children}
    if isinstance(value, list):
        children = []
        if depth < max_depth:
            children = [_inspect_value(child, key=f"{index}", depth=depth + 1, max_depth=max_depth) for index, child in enumerate(value[:20])]
        return {"key": key, "type": "array", "size": len(value), "children": children}
    return {"key": key, "type": type(value).__name__, "value": value}


def build_inspector_panel(model: Mapping[str, Any], *, title: str = "Model inspector") -> dict[str, object]:
    tree = _inspect_value(model)
    top_keys = sorted(str(key) for key in model.keys())
    return {
        "schema_version": INSPECTOR_SCHEMA_VERSION,
        "kind": "inspector_panel",
        "title": title,
        "top_level_key_count": len(top_keys),
        "top_level_keys": top_keys,
        "tree": tree,
    }


def summarize_inspector_panel(panel: Mapping[str, Any]) -> dict[str, object]:
    return {
        "schema_version": INSPECTOR_SCHEMA_VERSION,
        "title": panel.get("title"),
        "top_level_key_count": panel.get("top_level_key_count", 0),
        "has_tree": bool(panel.get("tree")),
    }


__all__ = ["INSPECTOR_SCHEMA_VERSION", "build_inspector_panel", "summarize_inspector_panel"]
