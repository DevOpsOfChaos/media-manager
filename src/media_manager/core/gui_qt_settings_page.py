from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_helpers import as_list, as_mapping, as_text, widget

QT_SETTINGS_PAGE_SCHEMA_VERSION = "1.0"


def build_qt_settings_page_plan(page_model: Mapping[str, Any]) -> dict[str, object]:
    widgets = []
    for index, raw_section in enumerate(as_list(page_model.get("sections"))):
        section = as_mapping(raw_section)
        widgets.append(
            widget(
                "settings_section",
                widget_id=f"settings.section.{as_text(section.get('id'), str(index))}",
                title=as_text(section.get("title")),
                items=as_list(section.get("items")),
                region="content",
            )
        )
    if not widgets:
        widgets.append(widget("empty_state", widget_id="settings.empty", title="No settings sections", region="content"))
    return {
        "schema_version": QT_SETTINGS_PAGE_SCHEMA_VERSION,
        "kind": "qt_settings_page_plan",
        "page_id": "settings",
        "layout": "settings_sections",
        "widget_count": len(widgets),
        "widgets": widgets,
    }


__all__ = ["QT_SETTINGS_PAGE_SCHEMA_VERSION", "build_qt_settings_page_plan"]
