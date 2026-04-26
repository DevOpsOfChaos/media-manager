from __future__ import annotations

from media_manager.core.gui_shell_model import build_gui_shell_model, summarize_gui_shell_model


def test_gui_shell_model_v4_contains_router_view_state_and_notifications() -> None:
    model = build_gui_shell_model(active_page_id="people", language="de", density="compact", view_state={"search_query": "max"})

    assert model["schema_version"] == "4.0"
    assert model["active_page_id"] == "people-review"
    assert model["router"]["active_page_id"] == "people-review"
    assert model["view_state"]["search_query"] == "max"
    assert model["notifications"]["kind"] == "notification_center"
    assert model["capabilities"]["interactive_navigation"] is True


def test_summarize_gui_shell_model_mentions_interactive_navigation() -> None:
    model = build_gui_shell_model(active_page_id="dashboard")

    text = summarize_gui_shell_model(model)

    assert "Interactive navigation: True" in text
