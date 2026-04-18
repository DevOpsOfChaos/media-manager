from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows import (
    build_workflow_profile_argv,
    get_workflow_preset,
    list_workflow_presets,
    load_workflow_profile,
    render_workflow_preset_command,
    render_workflow_profile_command,
    save_workflow_profile,
    validate_workflow_profile,
)


def test_list_workflow_presets_contains_cleanup_family_library() -> None:
    presets = list_workflow_presets()
    assert any(item.name == "cleanup-family-library" for item in presets)


def test_list_workflow_presets_contains_new_review_presets() -> None:
    presets = list_workflow_presets()
    names = {item.name for item in presets}
    assert "duplicates-similar-review" in names
    assert "trip-copy-review" in names
    assert "organize-review-json" in names
    assert "rename-review-json" in names


def test_render_workflow_preset_command_builds_cleanup_command() -> None:
    command = render_workflow_preset_command(
        "cleanup-family-library",
        overrides={
            "source": ["C:/Photos", "D:/Phone"],
            "target": "E:/Library",
        },
    )

    assert command.startswith("media-manager workflow run cleanup")
    assert "--source C:/Photos" in command
    assert "--source D:/Phone" in command
    assert "--target E:/Library" in command
    assert "--duplicate-policy first" in command


def test_render_trip_copy_review_preset_includes_review_flags() -> None:
    command = render_workflow_preset_command(
        "trip-copy-review",
        overrides={
            "source": ["C:/Phone"],
            "target": "E:/Trips",
            "label": "Italy_2025",
            "start": "2025-08-01",
            "end": "2025-08-14",
        },
    )

    assert command.startswith("media-manager workflow run trip")
    assert "--copy" in command
    assert "--show-files" in command
    assert "--json" in command


def test_render_duplicates_similar_review_preset_includes_review_flags() -> None:
    command = render_workflow_preset_command(
        "duplicates-similar-review",
        overrides={
            "source": ["C:/Library"],
        },
    )

    assert command.startswith("media-manager workflow run duplicates")
    assert "--policy first" in command
    assert "--mode delete" in command
    assert "--show-plan" in command
    assert "--show-decisions" in command
    assert "--similar-images" in command
    assert "--show-similar-review" in command


def test_render_workflow_preset_command_raises_for_missing_required_values() -> None:
    try:
        render_workflow_preset_command("trip-hardlink-collection", overrides={"source": ["C:/Phone"]})
    except ValueError as exc:
        assert "missing required values" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected missing required values error.")


def test_load_workflow_profile_and_render_command(tmp_path: Path) -> None:
    profile_path = tmp_path / "italy-trip.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy 2025",
                "preset": "trip-hardlink-collection",
                "values": {
                    "source": ["C:/Phone", "D:/Camera"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14",
                },
            }
        ),
        encoding="utf-8",
    )

    profile = load_workflow_profile(profile_path)
    command = render_workflow_profile_command(profile)

    assert profile.profile_name == "Italy 2025"
    assert profile.preset_name == "trip-hardlink-collection"
    assert command.startswith("media-manager workflow run trip")
    assert "--label Italy_2025" in command
    assert "--link" in command


def test_save_workflow_profile_roundtrip(tmp_path: Path) -> None:
    profile_path = tmp_path / "family-cleanup.json"

    saved = save_workflow_profile(
        profile_path,
        profile_name="Family cleanup",
        preset_name="cleanup-family-library",
        values={
            "source": ["C:/Photos", "D:/Phone"],
            "target": "E:/Library",
        },
    )
    loaded = load_workflow_profile(profile_path)
    command = render_workflow_profile_command(loaded)

    assert saved.profile_name == "Family cleanup"
    assert loaded.profile_name == "Family cleanup"
    assert loaded.preset_name == "cleanup-family-library"
    assert command.startswith("media-manager workflow run cleanup")


def test_build_workflow_profile_argv_returns_trip_command_parts(tmp_path: Path) -> None:
    profile_path = tmp_path / "italy-trip.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy 2025",
                "preset": "trip-hardlink-collection",
                "values": {
                    "source": ["C:/Phone", "D:/Camera"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14",
                },
            }
        ),
        encoding="utf-8",
    )
    profile = load_workflow_profile(profile_path)
    argv = build_workflow_profile_argv(profile)

    assert argv[:4] == ["media-manager", "workflow", "run", "trip"]
    assert "--source" in argv
    assert "--label" in argv
    assert "--link" in argv


def test_build_workflow_profile_argv_supports_runtime_flags() -> None:
    profile = save_workflow_profile(
        Path("/tmp/unused-profile.json"),
        profile_name="Review rename",
        preset_name="rename-review-json",
        values={
            "source": ["C:/Photos"],
            "history_dir": "runs",
            "run_log": "logs/rename.json",
            "non_recursive": True,
            "include_hidden": True,
        },
        overwrite=True,
    )
    argv = build_workflow_profile_argv(profile)

    assert "--show-files" in argv
    assert "--json" in argv
    assert "--history-dir" in argv
    assert "runs" in argv
    assert "--run-log" in argv
    assert "logs/rename.json" in argv
    assert "--non-recursive" in argv
    assert "--include-hidden" in argv


def test_validate_workflow_profile_reports_missing_values(tmp_path: Path) -> None:
    profile_path = tmp_path / "broken-trip.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Broken trip",
                "preset": "trip-hardlink-collection",
                "values": {
                    "source": ["C:/Phone"],
                    "target": "E:/Trips",
                },
            }
        ),
        encoding="utf-8",
    )
    profile = load_workflow_profile(profile_path)
    validation = validate_workflow_profile(profile)

    assert validation.valid is False
    assert set(validation.missing_values) == {"label", "start", "end"}
    assert validation.command_preview is None


def test_validate_workflow_profile_reports_journal_requires_apply(tmp_path: Path) -> None:
    profile_path = tmp_path / "organize-journal.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Organize journal preview",
                "preset": "organize-date-library",
                "values": {
                    "source": ["C:/Photos"],
                    "target": "E:/Library",
                    "journal": "logs/organize-journal.json",
                },
            }
        ),
        encoding="utf-8",
    )
    profile = load_workflow_profile(profile_path)
    validation = validate_workflow_profile(profile)

    assert validation.valid is False
    assert "Journal output requires apply mode." in validation.problems


def test_validate_workflow_profile_reports_duplicate_apply_requires_yes(tmp_path: Path) -> None:
    profile_path = tmp_path / "duplicates-apply.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Duplicates apply",
                "preset": "duplicate-review-safe",
                "values": {
                    "source": ["C:/Photos"],
                    "apply": True,
                },
            }
        ),
        encoding="utf-8",
    )
    profile = load_workflow_profile(profile_path)
    validation = validate_workflow_profile(profile)

    assert validation.valid is False
    assert "Duplicate apply mode requires yes confirmation." in validation.problems
