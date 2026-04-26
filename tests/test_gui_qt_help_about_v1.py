from media_manager.core.gui_qt_about_panel import build_qt_about_panel
from media_manager.core.gui_qt_help_overlay import build_qt_help_overlay


def test_help_overlay_is_localized() -> None:
    overlay = build_qt_help_overlay(language="de")
    assert overlay["title"].startswith("Hilfe")
    assert overlay["item_count"] >= 3


def test_about_panel_contains_privacy_text() -> None:
    panel = build_qt_about_panel({"command_count": 8})
    assert panel["command_count"] == 8
    assert "Local" in panel["privacy"]
