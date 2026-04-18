from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows import (
    build_profile_bound_workflow_form_model,
    build_preset_bound_workflow_form_model,
    build_workflow_launcher_model,
)


def test_build_preset_bound_form_marks_missing_required_fields_for_cleanup() -> None:
    model = build_preset_bound_workflow_form_model("cleanup-family-library")

    assert model.workflow_name == "cleanup"
    assert model.preset_name == "cleanup-family-library"
    assert model.valid is False
    assert set(model.missing_required_fields) == {"source", "target"}
    assert model.command_preview is None


def test_build_profile_bound_form_is_valid_when_required_values_exist(tmp_path: Path) -> None:
    profile_path = tmp_path / "trip.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy trip",
                "preset": "trip-hardlink-collection",
                "values": {
                    "source": ["C:/Phone"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14",
                },
            }
        ),
        encoding="utf-8",
    )

    model = build_profile_bound_workflow_form_model(profile_path)

    assert model.workflow_name == "trip"
    assert model.profile_name == "Italy trip"
    assert model.valid is True
    assert model.missing_required_fields == ()
    assert model.command_preview is not None
    assert model.command_preview.startswith("media-manager workflow run trip")


def test_build_workflow_launcher_model_includes_presets_and_profiles(tmp_path: Path) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "family.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Family cleanup",
                "preset": "cleanup-family-library",
                "values": {
                    "source": ["C:/Photos", "D:/Phone"],
                    "target": "E:/Library",
                },
            }
        ),
        encoding="utf-8",
    )

    model = build_workflow_launcher_model(profiles_dir)

    assert any(item.launcher_type == "preset" and item.name == "cleanup-family-library" for item in model.launchers)
    assert any(item.launcher_type == "profile" and item.profile_name == "Family cleanup" and item.valid for item in model.launchers)
