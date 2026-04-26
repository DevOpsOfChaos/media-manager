from media_manager.core.gui_qt_widget_factory_plan import build_qt_widget_factory_plan, validate_qt_widget_factory_plan


def test_widget_factory_plan_marks_supported_tree_ready() -> None:
    tree = {"id": "root", "type": "window", "children": [{"id": "title", "type": "text"}, {"id": "card", "type": "card"}]}
    plan = build_qt_widget_factory_plan(tree)
    assert plan["widget_count"] == 3
    assert plan["unsupported_widget_count"] == 0
    assert plan["ready_for_qt_renderer"] is True
    assert validate_qt_widget_factory_plan(plan)["valid"] is True


def test_widget_factory_plan_reports_unknown_widgets() -> None:
    plan = build_qt_widget_factory_plan({"id": "x", "type": "custom"})
    assert plan["unsupported_widget_count"] == 1
    assert validate_qt_widget_factory_plan(plan)["problem_count"] == 1
