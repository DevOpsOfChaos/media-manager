from __future__ import annotations

from media_manager.core.gui_modern_components import build_action_button, build_card, build_metric_tile, build_table_model, build_status_badge


def test_modern_components_build_stable_payloads() -> None:
    action = build_action_button("open", "Open", variant="primary")
    tile = build_metric_tile("runs", "Runs", 3)
    card = build_card("dashboard", "Dashboard", metrics={"runs": 3}, actions=[action])
    table = build_table_model("runs", ["id"], [{"id": "r1"}])
    badge = build_status_badge("ready_to_apply")

    assert action["component"] == "action_button"
    assert tile["value"] == 3
    assert card["actions"][0]["id"] == "open"
    assert table["row_count"] == 1
    assert badge["tone"] == "success"
