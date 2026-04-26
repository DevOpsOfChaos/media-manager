from media_manager.core.gui_qt_widget_tree import build_widget_tree_from_page_plan, validate_widget_tree


def test_widget_tree_from_page_plan_summarizes_widgets():
    page_plan = {
        "page_id": "dashboard",
        "title": "Dashboard",
        "sections": [
            {"id": "hero", "title": "Hero", "widgets": [{"type": "label", "text": "Hi"}]},
            {"id": "cards", "widgets": [{"type": "card"}, {"type": "button", "children": [{"type": "icon"}]}]},
        ],
    }
    tree = build_widget_tree_from_page_plan(page_plan)
    assert tree["page_id"] == "dashboard"
    assert tree["summary"]["section_count"] == 2
    assert tree["summary"]["type_summary"]["button"] == 1
    assert validate_widget_tree(tree)["valid"] is True
