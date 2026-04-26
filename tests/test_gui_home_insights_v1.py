from media_manager.core.gui_home_insights import build_home_insights


def test_home_insights_detects_missing_profiles_and_people_bundle() -> None:
    insights = build_home_insights({
        "profiles": {"summary": {"profile_count": 0}},
        "runs": {"summary": {"error_count": 0}},
        "people_review": {"ready_for_gui": True, "summary": {}},
    })

    ids = {item["insight_id"] for item in insights["insights"]}
    assert {"no_profiles", "people_ready"} <= ids
    assert insights["next_action_id"] == "open_profiles"


def test_home_insights_reports_run_errors() -> None:
    insights = build_home_insights({"profiles": {"summary": {"profile_count": 1}}, "runs": {"summary": {"error_count": 2}}})

    assert insights["warning_count"] == 1
    assert any(item["insight_id"] == "run_errors" for item in insights["insights"])
