from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_about_panel import build_qt_about_panel
from .gui_qt_content_sections import build_qt_content_sections
from .gui_qt_diagnostics_drawer import build_qt_diagnostics_drawer
from .gui_qt_help_overlay import build_qt_help_overlay
from .gui_qt_notification_drawer import build_qt_notification_drawer
from .gui_qt_screen_map import build_qt_screen_map

SHELL_COMPOSITION_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_shell_composition(shell_model: Mapping[str, Any]) -> dict[str, object]:
    page = _mapping(shell_model.get("page"))
    home = _mapping(shell_model.get("home_state"))
    manifest = _mapping(home.get("manifest_summary"))
    return {
        "schema_version": SHELL_COMPOSITION_SCHEMA_VERSION,
        "active_page_id": shell_model.get("active_page_id"),
        "screen_map": build_qt_screen_map(_list(shell_model.get("navigation")), active_page_id=str(shell_model.get("active_page_id") or "dashboard")),
        "content": build_qt_content_sections(page),
        "notifications": build_qt_notification_drawer(_list(shell_model.get("notifications"))),
        "diagnostics": build_qt_diagnostics_drawer(_list(shell_model.get("diagnostics"))),
        "help_overlay": build_qt_help_overlay(language=str(shell_model.get("language") or "en")),
        "about": build_qt_about_panel(manifest),
        "ready": bool(page),
    }


__all__ = ["SHELL_COMPOSITION_SCHEMA_VERSION", "build_qt_shell_composition"]
