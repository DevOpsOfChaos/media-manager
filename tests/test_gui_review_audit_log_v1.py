from media_manager.core.gui_review_audit_log import append_review_audit_event, build_review_audit_event, build_review_audit_log, recent_review_events


def test_build_review_audit_event_is_local_and_structured() -> None:
    event = build_review_audit_event("face_rejected", group_id="g1", face_id="f1", details={"reason": "wrong person"}, created_at_utc="2026-01-01T00:00:00Z")
    assert event["event_type"] == "face_rejected"
    assert event["details"]["reason"] == "wrong person"
    assert event["actor"] == "local-user"


def test_append_event_updates_summary() -> None:
    log = build_review_audit_log()
    log = append_review_audit_event(log, build_review_audit_event("group_named", group_id="g1"))
    log = append_review_audit_event(log, build_review_audit_event("group_named", group_id="g2"))
    assert log["event_count"] == 2
    assert log["event_type_summary"] == {"group_named": 2}


def test_recent_events_are_reverse_chronological_by_append_order() -> None:
    log = build_review_audit_log(build_review_audit_event(f"e{i}") for i in range(4))
    assert [item["event_type"] for item in recent_review_events(log, limit=2)] == ["e3", "e2"]
