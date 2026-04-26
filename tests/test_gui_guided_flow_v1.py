from media_manager.core.gui_guided_flow import build_guided_flow, build_guided_step, build_people_review_guided_flow


def test_guided_flow_finds_current_step() -> None:
    flow = build_guided_flow("demo", [build_guided_step("one", "One", complete=True), build_guided_step("two", "Two")])

    assert flow["complete_count"] == 1
    assert flow["current_step_id"] == "two"
    assert flow["complete"] is False


def test_people_review_guided_flow_blocks_later_steps() -> None:
    flow = build_people_review_guided_flow(has_scan_report=True, has_bundle=False, has_review_decisions=False, has_apply_preview=False)

    assert flow["steps"][0]["status"] == "complete"
    assert flow["steps"][2]["blocked"] is True
    assert flow["current_step_id"] == "bundle"
