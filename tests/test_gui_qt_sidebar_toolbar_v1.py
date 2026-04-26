from media_manager.core.gui_qt_sidebar_model import build_qt_sidebar_model
from media_manager.core.gui_qt_toolbar_model import build_qt_toolbar_model


def test_sidebar_model_builds_buttons_and_active_page() -> None:
    sidebar = build_qt_sidebar_model([
        {"id": "dashboard", "label": "Dashboard", "active": True},
        {"id": "people-review", "label": "People", "enabled": False},
    ])
    assert sidebar["active_page_id"] == "dashboard"
    assert sidebar["buttons"][0]["shortcut"] == "Ctrl+1"
    assert sidebar["buttons"][1]["enabled"] is False


def test_toolbar_buckets_risky_actions() -> None:
    toolbar = build_qt_toolbar_model([
        {"id": "open", "label": "Open", "recommended": True},
        {"id": "apply", "label": "Apply", "requires_confirmation": True},
        {"id": "disabled", "enabled": False},
    ])
    assert toolbar["bucket_summary"]["primary"] == 1
    assert toolbar["bucket_summary"]["danger"] == 1
    assert toolbar["bucket_summary"]["disabled"] == 1
