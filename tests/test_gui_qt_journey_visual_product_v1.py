from media_manager.core.gui_qt_user_journey_map import build_user_journey_map
from media_manager.core.gui_qt_visual_regression_manifest import build_visual_regression_manifest
from media_manager.core.gui_qt_product_experience import build_product_experience


def test_user_journey_marks_active_complete_and_pending() -> None:
    journey = build_user_journey_map("people-review", active_step_id="name_people")
    states = [step["state"] for step in journey["steps"]]
    assert "active" in states
    assert states[0] == "complete"
    assert states[-1] == "pending"


def test_visual_regression_manifest_uses_stable_digests() -> None:
    manifest = build_visual_regression_manifest([{"kind": "card", "title": "A"}, {"page_id": "dashboard"}])
    assert manifest["snapshot_count"] == 2
    assert len(manifest["snapshots"][0]["digest"]) == 16


def test_product_experience_combines_major_surfaces_safely() -> None:
    shell = {"active_page_id": "dashboard", "language": "de", "navigation": [{"id": "dashboard"}, {"id": "people-review"}], "theme": {"theme": "modern-dark", "palette": {"background": "#0", "surface": "#1", "text": "#2", "accent": "#3"}}}
    people_page = {"overview": {"face_count": 2}, "groups": [{"group_id": "g1", "status": "ready_to_apply"}]}
    product = build_product_experience(shell_model=shell, people_page=people_page, profiles=[{"profile_id": "p1"}], runs=[{"run_id": "r1", "exit_code": 0}])
    assert product["kind"] == "qt_product_experience"
    assert product["page_storyboard"]["scene_count"] == 2
    assert product["people_dashboard"]["ready_group_count"] == 1
    assert product["release_gate"]["ready"] is True
    assert product["job_launcher_plan"]["executes_immediately"] is False
