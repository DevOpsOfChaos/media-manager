from media_manager.core.gui_qt_performance_budget import build_qt_performance_budget, evaluate_qt_performance_budget


def test_performance_budget_counts_widgets_and_violations() -> None:
    tree = {"type": "root", "children": [{"type": "card", "children": []}, {"type": "card", "children": []}]}
    budget = build_qt_performance_budget(overrides={"widgets": 2, "visible_faces": 1})
    result = evaluate_qt_performance_budget(widget_tree=tree, metrics={"visible_faces": 3}, budget=budget)
    assert result["ok"] is False
    assert result["violation_count"] == 2
    assert {item["metric"] for item in result["violations"]} == {"widgets", "visible_faces"}
