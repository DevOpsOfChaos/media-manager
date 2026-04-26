from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_drawer_stack import build_drawer_stack
from .gui_qt_navigation_rail import build_navigation_rail_from_shell
from .gui_qt_page_slots import build_page_slots
from .gui_qt_safety_banner import build_safety_banner
from .gui_qt_top_bar_model import build_top_bar_model

APP_FRAME_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_app_frame_model(shell_model: Mapping[str, Any], *, collapsed_navigation: bool = False) -> dict[str, object]:
    page = _as_mapping(shell_model.get("page"))
    rail = build_navigation_rail_from_shell(shell_model, collapsed=collapsed_navigation)
    top_bar = build_top_bar_model(shell_model)
    slots = build_page_slots(page)
    safety = build_safety_banner(shell_model)
    drawers = build_drawer_stack(shell_model)
    return {
        "schema_version": APP_FRAME_SCHEMA_VERSION,
        "kind": "qt_app_frame_model",
        "window": dict(_as_mapping(shell_model.get("window"))),
        "active_page_id": shell_model.get("active_page_id") or page.get("page_id"),
        "navigation_rail": rail,
        "top_bar": top_bar,
        "page_slots": slots,
        "safety_banner": safety,
        "drawer_stack": drawers,
        "ready": bool(slots.get("ready")),
        "regions": ["navigation_rail", "top_bar", "safety_banner", "page_content", "drawer_stack", "status_bar"],
    }


def summarize_app_frame(frame: Mapping[str, Any]) -> dict[str, object]:
    rail = _as_mapping(frame.get("navigation_rail"))
    drawers = _as_mapping(frame.get("drawer_stack"))
    slots = _as_mapping(frame.get("page_slots"))
    return {
        "kind": "qt_app_frame_summary",
        "active_page_id": frame.get("active_page_id"),
        "ready": bool(frame.get("ready")),
        "navigation_items": rail.get("item_count", 0),
        "slot_count": slots.get("slot_count", 0),
        "drawer_count": drawers.get("drawer_count", 0),
        "attention_count": drawers.get("attention_count", 0) + (1 if _as_mapping(frame.get("safety_banner")).get("visible") else 0),
    }


__all__ = ["APP_FRAME_SCHEMA_VERSION", "build_app_frame_model", "summarize_app_frame"]
