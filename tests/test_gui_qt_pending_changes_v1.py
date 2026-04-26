from media_manager.core.gui_qt_pending_changes import build_pending_change, summarize_pending_changes


def test_pending_change_is_safe_intent() -> None:
    change = build_pending_change("rename_group", target_id="g1", payload={"name": "Alice"})
    assert change["change_id"] == "rename_group:group:g1"
    assert change["executes_immediately"] is False
    assert change["risk_level"] == "medium"


def test_pending_change_summary_counts_high_risk() -> None:
    summary = summarize_pending_changes([
        build_pending_change("rename_group", target_id="g1"),
        build_pending_change("apply_ready_groups", target_id="catalog", target_type="catalog"),
    ])
    assert summary["change_count"] == 2
    assert summary["high_risk_count"] == 1
    assert summary["requires_confirmation_count"] == 1
    assert summary["has_unsaved_changes"] is True
