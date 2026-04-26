from __future__ import annotations

from media_manager.core.gui_qt_navigation_model import build_qt_navigation_model


def test_qt_navigation_model_marks_active_item_and_shortcuts() -> None:
    model = build_qt_navigation_model(
        {
            "active_page_id": "people-review",
            "navigation": [
                {"id": "dashboard", "label": "Dashboard"},
                {"id": "people-review", "label": "People"},
            ],
        }
    )

    assert model["item_count"] == 2
    assert model["active_item"]["id"] == "people-review"
    assert model["active_item"]["shortcut"] == "Ctrl+3"
    assert model["items"][1]["button_role"] == "primary_nav"
