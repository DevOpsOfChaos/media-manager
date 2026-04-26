from __future__ import annotations

from media_manager.core.gui_dashboard_model import build_dashboard_overview


def test_dashboard_overview_contains_hero_metrics_and_cards() -> None:
    payload = build_dashboard_overview({"profiles": {"summary": {"profile_count": 2}}, "runs": {"summary": {"run_count": 1}}}, language="de")
    assert payload["hero"]["title"] == "Willkommen zurück"
    assert len(payload["metrics"]) == 3
    assert payload["cards"][0]["component"] == "card"
