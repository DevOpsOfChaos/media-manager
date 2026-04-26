from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RENDER_DIAGNOSTICS_SCHEMA_VERSION = "1.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_render_diagnostics(*, desktop_plan: Mapping[str, Any] | None = None, widget_tree: Mapping[str, Any] | None = None) -> dict[str, object]:
    desktop_plan = desktop_plan or {}
    widget_tree = widget_tree or {}
    problems: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    if not desktop_plan:
        warnings.append({"code": "missing_desktop_plan", "message": "No desktop plan was provided."})
    if desktop_plan and not _as_mapping(desktop_plan).get("page_plan"):
        problems.append({"code": "missing_page_plan", "message": "Desktop plan does not contain a page plan."})
    if widget_tree and not _as_list(widget_tree.get("children")):
        warnings.append({"code": "empty_widget_tree", "message": "Widget tree has no children."})
    unsupported = [item for item in _as_list(widget_tree.get("unsupported_widgets")) if isinstance(item, Mapping)]
    for item in unsupported:
        problems.append({"code": "unsupported_widget", "message": f"Unsupported widget: {item.get('type')}", "target": item.get("id")})
    return {
        "schema_version": QT_RENDER_DIAGNOSTICS_SCHEMA_VERSION,
        "kind": "qt_render_diagnostics",
        "valid": not problems,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "problems": problems,
        "warnings": warnings,
    }


__all__ = ["QT_RENDER_DIAGNOSTICS_SCHEMA_VERSION", "build_qt_render_diagnostics"]
