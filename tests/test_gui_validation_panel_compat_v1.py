from __future__ import annotations

from media_manager.core.gui_validation_panel import build_validation_message, build_validation_panel


def test_validation_panel_keeps_legacy_messages_api() -> None:
    panel = build_validation_panel([
        build_validation_message("x", "Legacy message", severity="warning"),
    ])

    assert panel["message_count"] == 1
    assert panel["warning_count"] == 1


def test_validation_panel_accepts_page_model_keywords() -> None:
    panel = build_validation_panel(
        page_id="people-review",
        page_model={
            "page_id": "people-review",
            "overview": {"needs_name_group_count": 2, "groups_truncated": True},
        },
        language="de",
    )

    assert panel["page_id"] == "people-review"
    assert panel["language"] == "de"
    assert panel["message_count"] == 2
    assert panel["warning_count"] == 2
