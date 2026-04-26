from __future__ import annotations

from media_manager.core.gui_actions import build_page_actions


def test_people_page_actions_are_safe() -> None:
    actions = build_page_actions({"page_id": "people-review"})
    assert {action["id"] for action in actions} >= {"review_people_groups", "preview_people_apply"}
    assert all(action["executes_filesystem_changes"] is False for action in actions)
