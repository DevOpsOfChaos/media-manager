from __future__ import annotations

from media_manager.core.gui_page_models import build_dashboard_page_model, build_page_model
from media_manager.core.gui_validation_panel import build_validation_panel


def test_dashboard_direct_call_keeps_legacy_layout_contract() -> None:
    model = build_dashboard_page_model({}, language="de")

    assert model["title"] == "Übersicht"
    assert model["layout"] == "hero_card_grid"
    assert model["layout_variant"] == "hero_card_grid_activity"
    assert model["layout_contract"]["layout"] == "hero_card_grid"
    assert model["layout_contract"]["variant"] == "hero_card_grid_activity"


def test_dashboard_page_model_wrapper_keeps_modern_layout() -> None:
    model = build_page_model("dashboard", {}, language="en", density="spacious")

    assert model["schema_version"] == "3.0"
    assert model["layout"] == "hero_card_grid_activity"
    assert model["layout_contract"]["layout"] == "hero_card_grid"


def test_people_page_keeps_legacy_editor_and_new_queue() -> None:
    model = build_page_model("people-review", {}, language="en")

    assert model["page_id"] == "people-review"
    assert model["card_grid"]["card_count"] == 0
    assert model["editor"]["kind"] == "people_review_editor_state"
    assert model["queue"]["group_count"] == 0


def test_validation_panel_supports_legacy_and_page_model_calls() -> None:
    legacy = build_validation_panel([])
    modern = build_validation_panel(page_id="people-review", page_model={"empty_state": "Open a bundle"}, language="en")

    assert legacy["message_count"] == 0
    assert modern["page_id"] == "people-review"
    assert modern["message_count"] == 1
