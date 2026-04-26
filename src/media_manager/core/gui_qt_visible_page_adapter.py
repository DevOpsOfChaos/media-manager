from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_dashboard_visible_plan import build_qt_dashboard_visible_plan
from .gui_qt_page_header_plan import build_qt_page_header_plan
from .gui_qt_people_review_visible_plan import build_qt_people_review_visible_plan
from .gui_qt_section_plan import build_empty_state_section
from .gui_qt_table_visible_plan import build_qt_table_visible_plan

VISIBLE_PAGE_ADAPTER_SCHEMA_VERSION = "1.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_visible_page_plan(page_model: Mapping[str, Any], *, density: str = "comfortable") -> dict[str, object]:
    kind = str(page_model.get("kind") or "")
    header = build_qt_page_header_plan(page_model)
    if kind == "dashboard_page":
        body = build_qt_dashboard_visible_plan(page_model, density=density)
    elif kind == "people_review_page":
        body = build_qt_people_review_visible_plan(page_model)
    elif kind in {"table_page", "profiles_page"}:
        body = build_qt_table_visible_plan(
            table_id=str(page_model.get("page_id") or "table"),
            columns=_as_list(page_model.get("columns")),
            rows=[row for row in _as_list(page_model.get("rows")) if isinstance(row, Mapping)],
            empty_title=str(_as_mapping(page_model.get("empty_state")).get("title") or "No rows"),
        )
    else:
        body = build_empty_state_section(str(page_model.get("page_id") or "page"), _as_mapping(page_model.get("empty_state")))
    return {
        "schema_version": VISIBLE_PAGE_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_visible_page_plan",
        "page_id": page_model.get("page_id"),
        "page_kind": kind,
        "density": density,
        "header": header,
        "body": body,
        "regions": ["header", "body"],
        "ready_for_qt": True,
    }


def visible_page_plan_summary(plan: Mapping[str, Any]) -> dict[str, object]:
    body = _as_mapping(plan.get("body"))
    return {
        "page_id": plan.get("page_id"),
        "page_kind": plan.get("page_kind"),
        "body_kind": body.get("kind"),
        "ready_for_qt": bool(plan.get("ready_for_qt")),
    }


__all__ = ["VISIBLE_PAGE_ADAPTER_SCHEMA_VERSION", "build_qt_visible_page_plan", "visible_page_plan_summary"]
