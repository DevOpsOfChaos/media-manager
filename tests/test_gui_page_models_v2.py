from __future__ import annotations

from media_manager.core.gui_page_models import build_page_model


def test_dashboard_page_model_has_modern_layout() -> None:
    page = build_page_model("dashboard", {}, language="en", density="spacious")

    assert page["schema_version"] == "3.0"
    assert page["layout"] == "hero_card_grid_activity"
    assert page["density"] == "spacious"
    assert page["validation"]["page_id"] == "dashboard"


def test_new_run_page_model_contains_wizard() -> None:
    page = build_page_model("new-run", {}, language="en")

    assert page["layout"] == "guided_wizard"
    assert page["wizard"]["selected_command"] == "people"


def test_run_history_page_model_contains_table_state() -> None:
    home = {"runs": {"items": [{"run_id": "r2", "command": "people", "status": "ok"}]}}
    page = build_page_model("run-history", home, query="people")

    assert page["table_state"]["filtered_row_count"] == 1
    assert page["rows"][0]["command"] == "people"
