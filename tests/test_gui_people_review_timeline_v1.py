from __future__ import annotations

from media_manager.core.gui_people_review_timeline import build_people_review_timeline


def test_people_review_timeline_starts_pending_without_bundle() -> None:
    timeline = build_people_review_timeline()

    assert timeline["next_stage_id"] == "scan"
    assert timeline["stages"][0]["status"] == "pending"
    assert timeline["stages"][2]["enabled"] is False


def test_people_review_timeline_marks_ready_apply() -> None:
    timeline = build_people_review_timeline(
        bundle_summary={"ready_for_gui": True},
        workspace_overview={"group_count": 3, "face_count": 8, "ready_group_count": 2},
        audit_preview={"safe_to_apply": True},
    )

    assert timeline["safe_to_apply"] is True
    assert timeline["next_stage_id"] == "catalog_apply"
    assert timeline["stages"][4]["status"] == "ready"
