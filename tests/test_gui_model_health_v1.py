from __future__ import annotations

from media_manager.core.gui_model_health import validate_page_model_contract, validate_shell_model_contract


def test_page_health_catches_missing_people_editor() -> None:
    result = validate_page_model_contract({"page_id": "people-review", "kind": "people_review_page", "layout": "review"})

    assert result["healthy"] is False
    assert {message["code"] for message in result["messages"]} == {"missing_people_editor", "missing_people_queue"}


def test_page_health_accepts_dashboard() -> None:
    result = validate_page_model_contract({"page_id": "dashboard", "kind": "dashboard_page", "layout": "hero_card_grid"})

    assert result["healthy"] is True
    assert result["error_count"] == 0


def test_shell_health_includes_page_contract() -> None:
    result = validate_shell_model_contract({"active_page_id": "people-review", "navigation": [{"id": "people-review"}], "page": {"page_id": "people-review", "kind": "people_review_page", "layout": "review"}})

    assert result["healthy"] is False
    assert result["error_count"] == 2
