from __future__ import annotations

from media_manager.core.gui_page_models import build_page_model
from media_manager.core.gui_qt_page_controller import normalize_page_id
from media_manager.core.gui_router import normalize_route


def test_settings_doctor_route_alias_points_to_settings_page() -> None:
    assert normalize_route("settings-doctor") == "settings"
    assert normalize_page_id("settings-doctor") == "settings"

    model = build_page_model("settings-doctor", {})
    assert model["page_id"] == "settings"
    assert model["kind"] == "settings_page"


def test_common_route_aliases_still_work_for_desktop_ui() -> None:
    assert normalize_route("runs") == "run-history"
    assert normalize_route("people") == "people-review"
    assert normalize_page_id("doctor") == "settings"
    assert build_page_model("history", {})["page_id"] == "run-history"


def test_unknown_page_stays_placeholder_but_has_validation_fields() -> None:
    model = build_page_model("does-not-exist", {})

    assert model["page_id"] == "does-not-exist"
    assert model["kind"] == "placeholder_page"
    assert "empty_state" in model
