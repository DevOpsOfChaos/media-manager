from media_manager.core.gui_workspace_snapshot import build_gui_workspace_snapshot, snapshot_is_compatible, summarize_workspace_snapshot


def test_workspace_snapshot_extracts_shell_page() -> None:
    snapshot = build_gui_workspace_snapshot(
        shell_model={"active_page_id": "people-review", "language": "de", "theme": {"theme": "modern-dark"}, "page": {"page_id": "people-review", "title": "Personenprüfung", "kind": "people_review_page", "layout": "review"}},
        audit_log={"event_count": 2, "event_type_summary": {"group_named": 2}},
    )
    assert snapshot["active_page_id"] == "people-review"
    assert snapshot["page"]["title"] == "Personenprüfung"
    assert snapshot["audit_summary"]["event_count"] == 2
    assert snapshot_is_compatible(snapshot) is True


def test_snapshot_summary_is_readable() -> None:
    text = summarize_workspace_snapshot(build_gui_workspace_snapshot(page_model={"page_id": "dashboard", "title": "Dashboard"}))
    assert "GUI workspace snapshot" in text
    assert "Dashboard" in text
