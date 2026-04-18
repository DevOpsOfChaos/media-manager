from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_shell import main


def test_cli_shell_preview_preset_form_outputs_bound_form(capsys) -> None:
    exit_code = main(["--preview-preset-form", "cleanup-family-library"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["workflow_name"] == "cleanup"
    assert set(payload["missing_required_fields"]) == {"source", "target"}


def test_cli_shell_preview_profile_form_outputs_bound_form(tmp_path: Path, capsys) -> None:
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

    exit_code = main(["--preview-profile-form", str(profile_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["profile_name"] == "Italy trip"
    assert payload["workflow_name"] == "trip"


def test_cli_shell_dump_launchers_lists_profiles(tmp_path: Path, capsys) -> None:
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

    exit_code = main(["--dump-launchers", "--profiles-dir", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert any(item["name"] == "cleanup-family-library" for item in payload["presets"])
    assert any(item["profile_name"] == "Cleanup profile" for item in payload["profiles"])
