from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.gui_command_plan import (
    build_open_people_bundle_plan,
    build_people_review_apply_command_plan,
    build_profile_command_plan,
)


def test_people_review_apply_command_plan_is_non_executing_and_confirmed(tmp_path: Path) -> None:
    plan = build_people_review_apply_command_plan(
        catalog_path=tmp_path / "people.json",
        workflow_json=tmp_path / "workflow.json",
        report_json=tmp_path / "report.json",
    )

    assert plan["plan_id"] == "people:review-apply"
    assert plan["requires_confirmation"] is True
    assert plan["execution_policy"]["execute_in_service_layer"] is False
    assert "review-apply" in plan["argv"]


def test_profile_command_plan_uses_app_profile_renderer(tmp_path: Path) -> None:
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_id": "people-scan",
                "title": "People Scan",
                "command": "people",
                "values": {"people_mode": "scan", "source_dirs": ["photos"], "catalog": "people.json"},
            }
        ),
        encoding="utf-8",
    )

    plan = build_profile_command_plan(profile_path)

    assert plan["enabled"] is True
    assert plan["metadata"]["command"] == "people"
    assert plan["argv"][:3] == ["media-manager", "people", "scan"]


def test_open_people_bundle_plan_points_at_validation_command(tmp_path: Path) -> None:
    plan = build_open_people_bundle_plan(tmp_path / "bundle")

    assert plan["risk_level"] == "safe"
    assert plan["argv"][:2] == ["media-manager-app-services", "validate-people-bundle"]
