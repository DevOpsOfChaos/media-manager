from __future__ import annotations

from media_manager.core.gui_page_models import build_dashboard_page_model, build_page_model
from media_manager.core.gui_validation_panel import build_validation_panel


def test_dashboard_keeps_legacy_layout_and_new_variant() -> None:
    model = build_dashboard_page_model({}, language="de")

    assert model["title"] == "Übersicht"
    assert model["layout"] == "hero_card_grid"
    assert model["layout_variant"] == "hero_card_grid_activity"
    assert model["hero"]["title"] == "Willkommen zurück"
    assert model["layout_contract"]["layout"] == "hero_card_grid"


def test_people_page_keeps_legacy_editor_field_without_bundle() -> None:
    model = build_page_model("people-review", {}, language="en")

    assert model["page_id"] == "people-review"
    assert model["card_grid"]["card_count"] == 0
    assert model["editor"]["kind"] == "people_review_editor_state"


def test_validation_panel_accepts_old_and_page_model_call_shapes() -> None:
    old_style = build_validation_panel([])
    assert old_style["message_count"] == 0

    new_style = build_validation_panel(page_id="people-review", page_model={"empty_state": "Open bundle"}, language="en")
    assert new_style["page_id"] == "people-review"
    assert new_style["message_count"] == 1
