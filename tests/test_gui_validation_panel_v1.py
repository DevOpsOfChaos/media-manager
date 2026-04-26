from __future__ import annotations

from media_manager.core.gui_validation_panel import build_validation_message, build_validation_panel, validation_panel_from_status


def test_validation_panel_counts_messages() -> None:
    panel = build_validation_panel([
        build_validation_message("warn", "Careful", severity="warning"),
        build_validation_message("err", "Broken", severity="error"),
    ])
    assert panel["message_count"] == 2
    assert panel["warning_count"] == 1
    assert panel["error_count"] == 1


def test_validation_panel_from_people_overview() -> None:
    panel = validation_panel_from_status({"overview": {"needs_name_group_count": 2}})
    assert panel["warning_count"] == 1
