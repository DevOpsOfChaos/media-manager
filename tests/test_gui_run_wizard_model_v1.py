from __future__ import annotations

from media_manager.core.gui_run_wizard_model import build_run_wizard_model


def test_run_wizard_defaults_to_people_and_safe_defaults() -> None:
    wizard = build_run_wizard_model(language="de", selected_command="unknown")

    assert wizard["selected_command"] == "people"
    assert wizard["safe_defaults"]["preview_first"] is True
    assert wizard["current_step_id"] == "select_inputs"
