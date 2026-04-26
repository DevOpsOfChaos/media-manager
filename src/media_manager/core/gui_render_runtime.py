from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_viewport_model import normalize_viewport

RENDER_RUNTIME_SCHEMA_VERSION = "1.0"
_CHILD_KEYS = ("children", "items", "widgets", "sections", "cards", "rows")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def flatten_widget_tree(widget: Mapping[str, Any], *, parent_id: str | None = None) -> list[dict[str, object]]:
    node = dict(widget)
    widget_id = str(node.get("id") or node.get("widget_id") or f"widget-{abs(hash(str(node))) % 100000}")
    widget_type = str(node.get("type") or node.get("component") or node.get("kind") or "unknown")
    rows = [{"id": widget_id, "type": widget_type, "parent_id": parent_id, "widget": node}]
    for child_key in _CHILD_KEYS:
        for child in _as_list(node.get(child_key)):
            if isinstance(child, Mapping):
                rows.extend(flatten_widget_tree(child, parent_id=widget_id))
    return rows


def summarize_render_contract(contract: Mapping[str, Any]) -> dict[str, object]:
    root = _as_mapping(contract.get("root") or contract.get("render_spec") or contract.get("page") or contract)
    widgets = flatten_widget_tree(root) if root else []
    type_summary: dict[str, int] = {}
    for item in widgets:
        key = str(item["type"])
        type_summary[key] = type_summary.get(key, 0) + 1
    diagnostics: list[dict[str, object]] = []
    if not widgets:
        diagnostics.append({"severity": "warning", "code": "empty_render_contract", "message": "No renderable widgets were found."})
    return {
        "schema_version": RENDER_RUNTIME_SCHEMA_VERSION,
        "widget_count": len(widgets),
        "type_summary": dict(sorted(type_summary.items())),
        "diagnostics": diagnostics,
        "has_errors": any(item.get("severity") == "error" for item in diagnostics),
    }


def build_render_runtime(contract: Mapping[str, Any], *, viewport: Mapping[str, Any] | None = None) -> dict[str, object]:
    root = _as_mapping(contract.get("root") or contract.get("render_spec") or contract.get("page") or contract)
    widgets = flatten_widget_tree(root) if root else []
    return {
        "schema_version": RENDER_RUNTIME_SCHEMA_VERSION,
        "kind": "render_runtime",
        "viewport": normalize_viewport(viewport),
        "summary": summarize_render_contract(contract),
        "widgets": widgets,
        "root_widget_id": widgets[0]["id"] if widgets else None,
    }


__all__ = ["RENDER_RUNTIME_SCHEMA_VERSION", "build_render_runtime", "flatten_widget_tree", "summarize_render_contract"]
