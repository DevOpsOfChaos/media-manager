from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_dashboard_page import build_qt_dashboard_page_plan
from .gui_qt_execution_page import build_qt_execution_page_plan
from .gui_qt_helpers import as_list, as_mapping, as_text, summarize_widgets, widget
from .gui_qt_people_review_page import build_qt_people_review_page_plan
from .gui_qt_settings_page import build_qt_settings_page_plan

QT_PAGE_ADAPTER_SCHEMA_VERSION = "1.0"


def _generic_table_page(page_model: Mapping[str, Any]) -> dict[str, object]:
    columns = [str(item) for item in as_list(page_model.get("columns"))]
    rows = [dict(as_mapping(item)) for item in as_list(page_model.get("rows"))]
    widgets = [
        widget(
            "data_table",
            widget_id=f"{as_text(page_model.get('page_id'), 'page')}.table",
            columns=columns,
            rows=rows[:500],
            returned_row_count=min(len(rows), 500),
            total_row_count=len(rows),
            region="content",
        )
    ]
    if not rows and page_model.get("empty_state"):
        widgets.append(widget("empty_state", widget_id=f"{as_text(page_model.get('page_id'), 'page')}.empty", payload=dict(as_mapping(page_model.get("empty_state"))), region="content"))
    return {
        "schema_version": QT_PAGE_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_generic_table_page_plan",
        "page_id": as_text(page_model.get("page_id")),
        "layout": "table_page",
        "widget_count": len(widgets),
        "widgets": widgets,
    }


def adapt_page_model_for_qt(page_model: Mapping[str, Any], *, execution_dashboard: Mapping[str, Any] | None = None) -> dict[str, object]:
    page_id = as_text(page_model.get("page_id"))
    kind = as_text(page_model.get("kind"))
    if page_id == "dashboard" or kind == "dashboard_page":
        plan = build_qt_dashboard_page_plan(page_model)
    elif page_id in {"people-review", "people"} or kind == "people_review_page":
        plan = build_qt_people_review_page_plan(page_model)
    elif page_id in {"settings", "doctor"} or kind == "settings_page":
        plan = build_qt_settings_page_plan(page_model)
    elif page_id == "execution":
        plan = build_qt_execution_page_plan(execution_dashboard)
    elif kind in {"table_page", "profiles_page"}:
        plan = _generic_table_page(page_model)
    else:
        widgets = [widget("empty_state", widget_id=f"{page_id or 'page'}.placeholder", title=as_text(page_model.get("title"), "Page"), region="content")]
        plan = {
            "schema_version": QT_PAGE_ADAPTER_SCHEMA_VERSION,
            "kind": "qt_placeholder_page_plan",
            "page_id": page_id,
            "layout": "placeholder",
            "widget_count": len(widgets),
            "widgets": widgets,
        }
    widgets = [as_mapping(item) for item in as_list(plan.get("widgets"))]
    return {
        **plan,
        "title": as_text(page_model.get("title")),
        "description": as_text(page_model.get("description")),
        "summary": summarize_widgets(widgets),
    }


__all__ = ["QT_PAGE_ADAPTER_SCHEMA_VERSION", "adapt_page_model_for_qt"]
