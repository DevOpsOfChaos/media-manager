from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows import (
    build_profile_bound_workflow_form_model,
    build_preset_bound_workflow_form_model,
    build_workflow_launcher_model,
)


def test_build_preset_bound_workflow_form_model_marks_missing_required_fields() -> None:
    model = build_preset_bound_workflow_form_model("cleanup-family-library")

    assert model.workflow_name == "cleanup"
    assert set(model.missing_required_fields) == {"source", "target"}
    duplicate_policy = next(item for item in model.fields if item.name == "duplicate_policy")
    assert duplicate_policy.value == "first"
    assert duplicate_policy.value_source == "binding"


def test_build_profile_bound_workflow_form_model_uses_profile_values(tmp_path: Path) -> None:
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
    assert model.command_preview is not None
    assert model.command_preview.startswith("media-manager workflow run trip")
    label_field = next(item for item in model.fields if item.name == "label")
    assert label_field.value == "Italy_2025"


def test_build_workflow_launcher_model_lists_profiles(tmp_path: Path) -> None:
    profile_path = tmp_path / "cleanup.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Cleanup profile",
                "preset": "cleanup-family-library",
                "values": {
                    "source": ["C:/Photos"],
                    "target": "E:/Library",
                },
            }
        ),
        encoding="utf-8",
    )

    model = build_workflow_launcher_model(tmp_path)

    assert any(item.name == "cleanup-family-library" for item in model.presets)
    assert any(item.profile_name == "Cleanup profile" for item in model.profiles)
