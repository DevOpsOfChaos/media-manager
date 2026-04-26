from __future__ import annotations

from media_manager.core.gui_safety_center import build_safety_center_state


def test_people_review_page_gets_privacy_warning() -> None:
    state = build_safety_center_state(page_model={"page_id": "people-review"})

    assert state["warning_count"] == 1
    assert state["safe_to_continue"] is True


def test_command_preview_risky_flags_become_warnings() -> None:
    state = build_safety_center_state(command_preview={"risky_flags": ["--apply", "--yes"]})

    assert state["warning_count"] == 2
