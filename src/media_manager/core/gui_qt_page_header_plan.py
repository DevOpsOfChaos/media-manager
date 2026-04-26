from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PAGE_HEADER_PLAN_SCHEMA_VERSION = "1.0"


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_qt_page_header_plan(
    page_model: Mapping[str, Any],
    *,
    breadcrumbs: list[Mapping[str, Any]] | None = None,
    actions: list[Mapping[str, Any]] | None = None,
) -> dict[str, object]:
    action_list = [dict(item) for item in (actions or [])]
    breadcrumb_list = [dict(item) for item in (breadcrumbs or [])]
    return {
        "schema_version": PAGE_HEADER_PLAN_SCHEMA_VERSION,
        "kind": "qt_page_header_plan",
        "page_id": _text(page_model.get("page_id"), "page"),
        "title": _text(page_model.get("title"), "Media Manager"),
        "description": _text(page_model.get("description")),
        "breadcrumbs": breadcrumb_list,
        "actions": action_list,
        "primary_action": next((item for item in action_list if item.get("bucket") == "primary" or item.get("variant") == "primary"), None),
        "qt": {
            "widget": "QFrame",
            "object_name": "PageHeader",
            "layout": "QVBoxLayout",
        },
    }


def header_has_actions(header_plan: Mapping[str, Any]) -> bool:
    return bool(_as_list(header_plan.get("actions")))


__all__ = ["PAGE_HEADER_PLAN_SCHEMA_VERSION", "build_qt_page_header_plan", "header_has_actions"]
