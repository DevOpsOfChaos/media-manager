from __future__ import annotations

from media_manager.core.gui_page_models import build_dashboard_page_model, build_page_model


def test_dashboard_page_model_is_localized_and_modern() -> None:
    model = build_dashboard_page_model({}, language="de")
    assert model["title"] == "Übersicht"
    assert model["layout"] == "hero_card_grid"
    assert model["hero"]["title"] == "Willkommen zurück"
    assert model["layout_contract"]["layout"] == "hero_card_grid"


def test_people_page_model_has_editor_without_bundle() -> None:
    model = build_page_model("people-review", {}, language="en")
    assert model["page_id"] == "people-review"
    assert model["card_grid"]["card_count"] == 0
    assert model["editor"]["kind"] == "people_review_editor_state"
