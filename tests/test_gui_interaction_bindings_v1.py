from media_manager.core.gui_interaction_bindings import build_interaction_binding, build_page_interaction_bindings, validate_interaction_bindings


def test_interaction_binding_never_executes_immediately() -> None:
    binding = build_interaction_binding("apply_ready", requires_confirmation=True)

    assert binding["requires_confirmation"] is True
    assert binding["executes_immediately"] is False


def test_page_interaction_bindings_extract_actions() -> None:
    page = {"page_id": "people-review", "quick_actions": [{"id": "open"}, {"id": "apply", "risk_level": "high"}]}
    payload = build_page_interaction_bindings(page)

    assert payload["binding_count"] == 2
    assert payload["confirmation_count"] == 1
    assert validate_interaction_bindings(payload["bindings"])["valid"] is True
