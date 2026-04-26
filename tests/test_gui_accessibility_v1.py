from __future__ import annotations

from media_manager.core.gui_accessibility import annotate_for_accessibility, build_accessibility_contract


def test_accessibility_contract_has_keyboard_shortcuts() -> None:
    payload = build_accessibility_contract(language="de")
    assert payload["keyboard_first"] is True
    assert any(item["id"] == "command_palette" for item in payload["shortcuts"])


def test_annotate_component_adds_role_and_label() -> None:
    component = annotate_for_accessibility({"id": "x", "title": "Title"}, role="button")
    assert component["accessibility"]["role"] == "button"
    assert component["accessibility"]["label"] == "Title"
