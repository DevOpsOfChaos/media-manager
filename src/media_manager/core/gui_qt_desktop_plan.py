from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_helpers import as_mapping, as_text
from .gui_qt_navigation_model import build_qt_navigation_model
from .gui_qt_page_adapter import adapt_page_model_for_qt
from .gui_qt_status_presenter import build_qt_status_presenter

QT_DESKTOP_PLAN_SCHEMA_VERSION = "1.0"


def build_qt_desktop_plan(shell_model: Mapping[str, Any], *, execution_dashboard: Mapping[str, Any] | None = None) -> dict[str, object]:
    page = as_mapping(shell_model.get("page"))
    plan = adapt_page_model_for_qt(page, execution_dashboard=execution_dashboard)
    navigation = build_qt_navigation_model(shell_model)
    status = build_qt_status_presenter(shell_model)
    window = as_mapping(shell_model.get("window"))
    theme = as_mapping(shell_model.get("theme"))
    return {
        "schema_version": QT_DESKTOP_PLAN_SCHEMA_VERSION,
        "kind": "qt_desktop_plan",
        "window": {
            "title": as_text(window.get("title"), "Media Manager"),
            "width": window.get("width", 1440),
            "height": window.get("height", 940),
            "minimum_width": window.get("minimum_width", 1180),
            "minimum_height": window.get("minimum_height", 760),
        },
        "theme": theme.get("theme", "modern-dark"),
        "active_page_id": status.get("active_page_id"),
        "navigation": navigation,
        "page_plan": plan,
        "status": status,
        "safe_runtime": {
            "executes_commands": False,
            "requires_user_confirmation_for_risky_actions": True,
            "uses_shell_subprocess": False,
        },
    }


def summarize_qt_desktop_plan(plan: Mapping[str, Any]) -> str:
    nav = as_mapping(plan.get("navigation"))
    page = as_mapping(plan.get("page_plan"))
    summary = as_mapping(page.get("summary"))
    return "\n".join(
        [
            "Qt desktop plan",
            f"  Active page: {plan.get('active_page_id')}",
            f"  Navigation items: {nav.get('item_count', 0)}",
            f"  Page layout: {page.get('layout')}",
            f"  Widgets: {summary.get('widget_count', 0)}",
            f"  Safe runtime: {as_mapping(plan.get('safe_runtime')).get('executes_commands') is False}",
        ]
    )


__all__ = ["QT_DESKTOP_PLAN_SCHEMA_VERSION", "build_qt_desktop_plan", "summarize_qt_desktop_plan"]
