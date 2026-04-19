from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows import (
    build_profile_bound_workflow_form_model,
    build_preset_bound_workflow_form_model,
    build_workflow_form_model,
    build_workflow_launcher_model,
)


def test_build_preset_bound_form_marks_missing_required_fields_for_cleanup() -> None:
    model = build_preset_bound_workflow_form_model("cleanup-family-library")

    assert model.workflow_name == "cleanup"
    assert model.preset_name == "cleanup-family-library"
    assert model.valid is False
    assert set(model.missing_required_fields) == {"source", "target"}
    assert model.command_preview is None
    assert model.binding_summary["value_source_summary"]["preset-default"] >= 1


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
    mode_field = next(item for item in model.fields if item.name == "mode")
    assert mode_field.value == "link"
    assert mode_field.value_source == "preset-default"
    label_field = next(item for item in model.fields if item.name == "label")
    assert label_field.value_source == "profile-value"


def test_build_profile_bound_form_surfaces_runtime_validation_problems(tmp_path: Path) -> None:
    profile_path = tmp_path / "bad-duplicates.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Bad duplicates",
                "preset": "duplicates-similar-review",
                "values": {
                    "source": ["C:/Photos"],
                    "show_similar_review": True,
                    "similar_images": False,
                    "apply": True,
                    "yes": False,
                },
            }
        ),
        encoding="utf-8",
    )

    model = build_profile_bound_workflow_form_model(profile_path)

    assert model.workflow_name == "duplicates"
    assert model.valid is False
    assert model.command_preview is None
    assert any("show_similar_review requires similar_images" in item for item in model.problems)
    assert any("duplicates apply requires yes" in item for item in model.problems)


def test_build_workflow_form_model_exposes_runtime_review_fields() -> None:
    model = build_workflow_form_model("trip")
    field_names = {item.name for item in model.fields}
    assert {"history_dir", "run_log", "journal", "show_files", "json_output", "apply"} <= field_names


def test_build_workflow_launcher_model_includes_presets_profiles_and_summary(tmp_path: Path) -> None:
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
    summary = model.build_summary()
    assert summary["total_launchers"] == len(model.launchers)
    assert summary["launcher_type_summary"]["preset"] >= 1
    assert summary["launcher_type_summary"]["profile"] == 1
