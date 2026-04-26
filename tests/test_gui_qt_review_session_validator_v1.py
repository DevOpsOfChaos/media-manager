from media_manager.core.gui_qt_review_session_panel import build_qt_review_session_panel, summarize_qt_review_session_panel
from media_manager.core.gui_qt_ui_contract_validator import validate_qt_page_contract, validate_qt_shell_contract


def test_review_session_panel_blocks_empty_review() -> None:
    panel = build_qt_review_session_panel({"page_id": "people-review", "queue": {"groups": []}, "editor": {}, "detail": {}})
    summary = summarize_qt_review_session_panel(panel)
    assert panel["ready_for_review"] is False
    assert summary["blocked_count"] >= 1


def test_review_session_panel_accepts_selected_group() -> None:
    panel = build_qt_review_session_panel(
        {
            "page_id": "people-review",
            "selected_group_id": "g1",
            "queue": {"groups": [{"group_id": "g1"}], "group_count": 1},
            "editor": {"detail_actions": [{"id": "rename", "label": "Rename"}]},
            "detail": {"faces": [{"face_id": "f1"}]},
        }
    )
    assert panel["ready_for_review"] is True
    assert panel["face_count"] == 1


def test_contract_validator_checks_page_and_shell() -> None:
    page = {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "layout": "hero_card_grid"}
    shell = {"application": {}, "window": {}, "navigation": [{"id": "dashboard"}], "active_page_id": "dashboard", "page": page, "theme": {}, "status_bar": {}}
    assert validate_qt_page_contract(page)["valid"] is True
    assert validate_qt_shell_contract(shell)["valid"] is True
    broken = validate_qt_page_contract({"page_id": "people-review", "kind": "people_review_page", "title": "People", "layout": "review"})
    assert broken["valid"] is False
    assert broken["problem_count"] >= 1
