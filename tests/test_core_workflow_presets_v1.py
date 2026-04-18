from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows import (
    get_workflow_preset,
    list_workflow_presets,
    load_workflow_profile,
    render_workflow_preset_command,
    render_workflow_profile_command,
)


def test_list_workflow_presets_contains_cleanup_family_library() -> None:
    presets = list_workflow_presets()
    assert any(item.name == "cleanup-family-library" for item in presets)



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
