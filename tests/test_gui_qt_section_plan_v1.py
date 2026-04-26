from media_manager.core.gui_qt_section_plan import build_empty_state_section, build_qt_section_plan, summarize_section_plan


def test_section_plan_summarizes_children() -> None:
    plan = build_qt_section_plan("main", title="Main", children=[{"kind": "text"}])
    assert plan["kind"] == "qt_section_plan"
    assert plan["child_count"] == 1
    assert summarize_section_plan(plan)["title"] == "Main"


def test_empty_state_section_contains_text_children() -> None:
    plan = build_empty_state_section("people-review", {"title": "No bundle", "description": "Open one."})
    assert plan["variant"] == "empty_state"
    assert plan["children"][0]["text"] == "No bundle"
