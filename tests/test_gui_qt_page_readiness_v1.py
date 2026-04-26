from media_manager.core.gui_qt_page_readiness import evaluate_qt_page_readiness, summarize_qt_page_readiness


def test_page_readiness_scores_required_keys() -> None:
    ready = evaluate_qt_page_readiness({"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "hero": {}, "cards": []})
    blocked = evaluate_qt_page_readiness({"page_id": "people-review", "kind": "people_review_page", "title": "People"})
    assert ready["ready"] is True
    assert blocked["ready"] is False
    summary = summarize_qt_page_readiness([ready, blocked])
    assert summary["page_count"] == 2
    assert summary["blocked_count"] == 1
