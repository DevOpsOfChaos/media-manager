from __future__ import annotations

from media_manager.core.workflows import build_workflow_form_model, list_workflow_form_models


def test_build_workflow_form_model_for_cleanup_contains_core_fields() -> None:
    model = build_workflow_form_model("cleanup")

    assert model.workflow_name == "cleanup"
    names = [item.name for item in model.fields]
    assert names[:2] == ["source", "target"]
    source_field = next(item for item in model.fields if item.name == "source")
    assert source_field.required is True
    assert source_field.multiple is True


def test_build_workflow_form_model_for_trip_contains_date_fields() -> None:
    model = build_workflow_form_model("trip")

    names = [item.name for item in model.fields]
    assert "label" in names
    assert "start" in names
    assert "end" in names
    mode_field = next(item for item in model.fields if item.name == "mode")
    assert mode_field.choices == ("link", "copy")


def test_list_workflow_form_models_contains_known_workflows() -> None:
    models = list_workflow_form_models()
    names = {item.workflow_name for item in models}
    assert {"cleanup", "trip", "duplicates", "organize", "rename"} <= names
