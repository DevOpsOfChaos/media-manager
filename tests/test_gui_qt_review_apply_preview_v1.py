from media_manager.core.gui_qt_pending_changes import build_pending_change
from media_manager.core.gui_qt_review_apply_preview import build_qt_review_apply_preview


def test_apply_preview_blocks_groups_that_need_names() -> None:
    state = {
        "page": {"queue": {"groups": [{"group_id": "g1", "status": "needs_name"}]}},
        "pending_changes": [],
    }
    preview = build_qt_review_apply_preview(state)
    assert preview["safe_to_apply"] is False
    assert "groups_need_name" in preview["blocked_reasons"]


def test_apply_preview_is_safe_when_ready_and_no_risky_changes() -> None:
    state = {
        "page": {"queue": {"groups": [{"group_id": "g1", "status": "ready_to_apply"}]}},
        "pending_changes": [build_pending_change("rename_group", target_id="g1")],
    }
    preview = build_qt_review_apply_preview(state)
    assert preview["ready_group_count"] == 1
    assert preview["safe_to_apply"] is True
    assert preview["executes_immediately"] is False


def test_apply_preview_requires_confirmation_for_high_risk_changes() -> None:
    state = {
        "page": {"queue": {"groups": [{"group_id": "g1", "status": "ready_to_apply"}]}},
        "pending_changes": [build_pending_change("apply_ready_groups", target_id="catalog", target_type="catalog")],
    }
    preview = build_qt_review_apply_preview(state)
    assert preview["safe_to_apply"] is False
    assert "confirmation_required" in preview["blocked_reasons"]
