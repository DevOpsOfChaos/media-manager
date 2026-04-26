from media_manager.core.gui_render_contracts import build_page_render_contract, summarize_render_contract


def test_render_contract_for_dashboard_is_ready() -> None:
    contract = build_page_render_contract({"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "cards": []})

    assert contract["ready_to_render"] is True
    assert contract["tokens"]["tokens"] == contract["tokens"]["palette"]
    assert summarize_render_contract(contract)["ready_to_render"] is True


def test_render_contract_for_generic_page_is_ready() -> None:
    contract = build_page_render_contract({"page_id": "settings", "kind": "settings_page", "title": "Settings"})

    assert contract["ready_to_render"] is True
    assert contract["render_spec"]["kind"] == "generic_render_spec"
