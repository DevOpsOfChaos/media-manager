from media_manager.core.gui_qt_widget_plan import build_qt_widget_plan, qt_class_for_widget_type, validate_qt_widget_plan


def test_qt_widget_plan_maps_known_types() -> None:
    plan = build_qt_widget_plan({"root": {"id": "card-1", "type": "card", "children": [{"id": "label", "type": "text", "text": "Hi"}]}})

    assert plan["widget_count"] == 2
    assert plan["widgets"][0]["qt_class"] == "QFrame"
    assert plan["widgets"][1]["qt_class"] == "QLabel"
    assert validate_qt_widget_plan(plan)["valid"] is True


def test_qt_class_falls_back_to_qwidget() -> None:
    assert qt_class_for_widget_type("unknown_custom") == "QWidget"
