from __future__ import annotations

from media_manager.core.gui_notifications import build_notification, build_notification_center, notifications_from_validation


def test_build_notification_normalizes_level() -> None:
    note = build_notification("x", "Title", "Message", level="loud")

    assert note["level"] == "info"
    assert note["dismissible"] is True


def test_build_notification_center_summarizes_levels() -> None:
    center = build_notification_center([
        build_notification("a", "A", level="warning"),
        build_notification("b", "B", level="warning"),
        build_notification("c", "C", level="error"),
    ])

    assert center["notification_count"] == 3
    assert center["level_summary"] == {"error": 1, "warning": 2}


def test_notifications_from_validation_panel() -> None:
    notes = notifications_from_validation({"messages": [{"id": "m", "title": "Check", "level": "warning"}]})

    assert notes[0]["id"] == "m"
    assert notes[0]["level"] == "warning"
