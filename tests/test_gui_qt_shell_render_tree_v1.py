from __future__ import annotations

from media_manager.core.gui_qt_shell_render_tree import build_shell_render_tree, summarize_shell_render_tree
from media_manager.core.gui_qt_render_tree_validator import validate_render_tree


def test_shell_render_tree_wraps_navigation_page_and_status() -> None:
    desktop_plan = {
        "active_page_id": "dashboard",
        "window": {"title": "Media Manager"},
        "navigation": [
            {"id": "dashboard", "label": "Dashboard", "active": True, "enabled": True},
            {"id": "people-review", "label": "People", "active": False, "enabled": True},
        ],
        "page": {
            "page_id": "dashboard",
            "body": {
                "kind": "qt_dashboard_visible_plan",
                "page_id": "dashboard",
                "layout": "hero_grid_activity",
                "sections": [
                    {
                        "section_id": "dashboard-hero",
                        "variant": "hero",
                        "title": "Dashboard",
                        "children": [{"kind": "metric_strip", "metrics": {"profiles": 2}}],
                    },
                    {
                        "section_id": "dashboard-cards",
                        "kind": "card_grid_section",
                        "grid": {
                            "columns": 3,
                            "card_count": 1,
                            "visible_card_count": 1,
                            "cards": [{"card_id": "card-1", "title": "Card 1"}],
                        },
                    },
                ],
            },
        },
        "status_bar": {"text": "Ready"},
    }

    tree = build_shell_render_tree(desktop_plan)
    summary = summarize_shell_render_tree(tree)
    validation = validate_render_tree(tree["root"])

    assert tree["kind"] == "qt_shell_render_tree"
    assert tree["root"]["component"] == "ShellFrame"
    assert summary["navigation_count"] == 2
    assert summary["executable_node_count"] == 0
    assert validation["valid"] is True
