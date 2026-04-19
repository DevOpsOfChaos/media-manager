from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_shell import main


def test_cli_shell_dump_launchers_includes_built_in_presets_and_summary(capsys) -> None:
    exit_code = main(["--dump-launchers"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["total_launchers"] == len(payload["launchers"])
    assert any(item["launcher_type"] == "preset" and item["name"] == "cleanup-family-library" for item in payload["launchers"])


def test_cli_shell_preview_preset_form_outputs_bound_form_json(capsys) -> None:
    exit_code = main(["--preview-preset-form", "trip-hardlink-collection"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["workflow_name"] == "trip"
    assert payload["preset_name"] == "trip-hardlink-collection"
    assert payload["valid"] is False
    assert "source" in payload["missing_required_fields"]


def test_cli_shell_preview_profile_form_and_command(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "trip.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy trip",
                "preset": "trip-copy-review",
                "values": {
                    "source": ["C:/Phone"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14",
                    "history_dir": "runs",
                },
            }
        ),
        encoding="utf-8",
    )

    code_form = main(["--preview-profile-form", str(profile_path)])
    captured_form = capsys.readouterr()
    assert code_form == 0
    payload = json.loads(captured_form.out)
    assert payload["profile_name"] == "Italy trip"
    assert payload["valid"] is True
    assert payload["binding_summary"]["value_source_summary"]["profile-value"] >= 1
    assert payload["command_preview"].startswith("media-manager workflow run trip")
    assert "--copy" in payload["command_preview"]
    assert "--history-dir runs" in payload["command_preview"]

    code_command = main(["--preview-profile-command", str(profile_path)])
    captured_command = capsys.readouterr()
    assert code_command == 0
    assert captured_command.out.strip().startswith("media-manager workflow run trip")


def test_cli_shell_dump_launchers_scans_profiles_dir_and_shows_invalid_profile(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "cleanup.json").write_text(
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
    (profiles_dir / "broken.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Broken duplicates",
                "preset": "duplicates-similar-review",
                "values": {
                    "source": ["C:/Photos"],
                    "show_similar_review": True,
                    "similar_images": False,
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["--dump-launchers", "--profiles-dir", str(profiles_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["launcher_type_summary"]["profile"] == 2
    assert any(item["launcher_type"] == "profile" and item["profile_name"] == "Family cleanup" and item["valid"] for item in payload["launchers"])
    assert any(item["launcher_type"] == "profile" and item["profile_name"] == "Broken duplicates" and not item["valid"] for item in payload["launchers"])
