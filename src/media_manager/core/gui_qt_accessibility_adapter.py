from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

ACCESSIBILITY_ADAPTER_SCHEMA_VERSION = "1.0"

def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []

def build_accessibility_labels(blueprint: Mapping[str, Any]) -> dict[str, object]:
    labels: dict[str, str] = {}

    def walk(node: Mapping[str, Any]) -> None:
        widget_id = str(node.get("widget_id") or "")
        props = _mapping(node.get("props"))
        if widget_id:
            labels[widget_id] = str(props.get("accessible_name") or props.get("text") or props.get("title") or widget_id)
        for raw in _list(node.get("children")):
            if isinstance(raw, Mapping):
                walk(raw)

    root = _mapping(blueprint.get("root"))
    walk(root)
    return {
        "schema_version": ACCESSIBILITY_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_accessibility_labels",
        "label_count": len(labels),
        "labels": labels,
    }

def find_missing_accessibility_labels(payload: Mapping[str, Any]) -> dict[str, object]:
    labels = _mapping(payload.get("labels"))
    missing = [key for key, value in labels.items() if not str(value).strip()]
    return {"missing_count": len(missing), "missing": missing, "valid": not missing}

__all__ = ["ACCESSIBILITY_ADAPTER_SCHEMA_VERSION", "build_accessibility_labels", "find_missing_accessibility_labels"]
