from media_manager.core.gui_qt_form_plan import build_qt_form_plan


def test_required_empty_field_makes_form_invalid() -> None:
    form = build_qt_form_plan("settings", [{"id": "catalog", "label": "Catalog", "required": True, "value": ""}])
    assert form["valid"] is False
    assert form["required_count"] == 1


def test_sensitive_field_is_preserved() -> None:
    form = build_qt_form_plan("people", [{"id": "encodings", "label": "Encodings", "type": "checkbox", "sensitive": True}])
    assert form["fields"][0]["sensitive"] is True
