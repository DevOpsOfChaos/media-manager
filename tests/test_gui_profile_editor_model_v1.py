from __future__ import annotations

from media_manager.core.gui_profile_editor_model import build_profile_form_schema, build_profile_list_state


def test_people_profile_form_has_catalog_and_backend_fields() -> None:
    schema = build_profile_form_schema(command="people", language="de")
    field_ids = {item["id"] for item in schema["fields"]}
    assert {"source_dirs", "catalog", "backend", "include_encodings"} <= field_ids


def test_profile_list_state_includes_form_schemas() -> None:
    state = build_profile_list_state({"profiles": {"items": []}})
    assert "people" in state["form_schemas"]
