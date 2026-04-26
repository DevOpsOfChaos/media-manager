from media_manager.core.gui_qt_settings_binder import build_qt_settings_form, build_settings_update_intent


def test_settings_form_and_update_intent_are_safe() -> None:
    form = build_qt_settings_form({"language": "de", "theme": "modern-light"})
    fields = {field["id"]: field for field in form["fields"]}
    assert fields["language"]["value"] == "de"
    assert "modern-dark" in fields["theme"]["choices"]
    intent = build_settings_update_intent("theme", "modern-dark")
    assert intent["executes_immediately"] is False
    assert intent["requires_save"] is True
