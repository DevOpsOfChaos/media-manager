from __future__ import annotations

from media_manager.core.gui_qt_dashboard_page import build_qt_dashboard_page_plan


def test_dashboard_page_plan_contains_hero_and_cards() -> None:
    plan = build_qt_dashboard_page_plan(
        {
            "page_id": "dashboard",
            "title": "Dashboard",
            "hero": {"title": "Welcome", "metrics": {"runs": 3}},
            "cards": [
                {"id": "runs", "title": "Runs", "metrics": {"errors": 0}},
                {"id": "people", "title": "People", "metrics": {"groups": 2}},
            ],
        }
    )

    assert plan["layout"] == "dashboard_responsive_grid"
    assert plan["widget_count"] == 3
    assert plan["widgets"][0]["widget_type"] == "hero_panel"
    assert plan["widgets"][1]["widget_type"] == "metric_card"
