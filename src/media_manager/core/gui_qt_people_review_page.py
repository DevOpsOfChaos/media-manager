from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_helpers import as_list, as_mapping, as_text, compact_metrics, widget

QT_PEOPLE_REVIEW_SCHEMA_VERSION = "1.0"

_STATUS_RANK = {
    "needs_name": 0,
    "needs_review": 1,
    "ready_to_apply": 2,
    "named_not_applied": 3,
    "matched_existing": 4,
    "all_faces_rejected": 5,
}


def _ranked_groups(page_model: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    groups = [as_mapping(item) for item in as_list(page_model.get("groups"))]
    return sorted(groups, key=lambda item: (_STATUS_RANK.get(as_text(item.get("status")), 99), as_text(item.get("display_label") or item.get("group_id")).casefold()))


def build_qt_people_review_page_plan(page_model: Mapping[str, Any]) -> dict[str, object]:
    groups = _ranked_groups(page_model)
    selected_group_id = as_text(page_model.get("selected_group_id") or (groups[0].get("group_id") if groups else ""))
    detail = as_mapping(page_model.get("detail"))
    widgets: list[dict[str, object]] = [
        widget(
            "people_review_toolbar",
            widget_id="people.toolbar",
            title=as_text(page_model.get("title"), "People review"),
            query=as_text(page_model.get("query")),
            metrics=compact_metrics(as_mapping(page_model.get("overview"))),
            region="toolbar",
        ),
        widget(
            "people_group_list",
            widget_id="people.groups",
            groups=[
                {
                    "group_id": group.get("group_id"),
                    "label": group.get("display_label") or group.get("group_id"),
                    "status": group.get("status"),
                    "face_count": group.get("face_count", 0),
                    "selected": as_text(group.get("group_id")) == selected_group_id,
                }
                for group in groups[:100]
            ],
            region="master",
        ),
        widget(
            "people_group_detail",
            widget_id="people.detail",
            group_id=selected_group_id or None,
            title=as_text(detail.get("title"), "Selection"),
            subtitle=as_text(detail.get("subtitle")),
            faces=as_list(detail.get("faces"))[:60],
            region="detail",
        ),
    ]
    empty_state = page_model.get("empty_state")
    if empty_state:
        widgets.append(widget("empty_state", widget_id="people.empty", payload=dict(as_mapping(empty_state)), region="detail"))
    return {
        "schema_version": QT_PEOPLE_REVIEW_SCHEMA_VERSION,
        "kind": "qt_people_review_page_plan",
        "page_id": "people-review",
        "layout": "people_review_master_detail",
        "selected_group_id": selected_group_id or None,
        "group_count": len(groups),
        "widget_count": len(widgets),
        "widgets": widgets,
    }


__all__ = ["QT_PEOPLE_REVIEW_SCHEMA_VERSION", "build_qt_people_review_page_plan"]
