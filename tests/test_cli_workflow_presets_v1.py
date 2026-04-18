from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import DELEGATE_HANDLERS, main


def test_cli_workflow_presets_json_lists_builtin_presets(capsys) -> None:
    exit_code = main(["presets", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert any(item["name"] == "cleanup-family-library" for item in payload["presets"])


def test_cli_workflow_render_preset_outputs_command(capsys) -> None:
    exit_code = main(
        [
            "render-preset",
            "cleanup-family-library",
            "--source",
            "C:/Photos",
            "--source",
            "D:/Phone",
            "--target",
            "E:/Library",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "media-manager workflow run cleanup" in captured.out
    assert "--target E:/Library" in captured.out


def test_cli_workflow_profile_show_reads_profile_json(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "cleanup-profile.json"
    profile_path.write_text(
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

    exit_code = main(["profile-show", str(profile_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["profile_name"] == "Family cleanup"
    assert payload["preset"] == "cleanup-family-library"
    assert payload["command"].startswith("media-manager workflow run cleanup")


def test_cli_workflow_profile_save_writes_profile_json(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "profiles" / "trip-profile.json"

    exit_code = main(
        [
            "profile-save",
            str(profile_path),
            "--preset",
            "trip-hardlink-collection",
            "--profile-name",
            "Italy trip",
            "--source",
            "C:/Phone",
            "--target",
            "E:/Trips",
            "--label",
            "Italy_2025",
            "--start",
            "2025-08-01",
            "--end",
            "2025-08-14",
            "--json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    written = json.loads(profile_path.read_text(encoding="utf-8"))
    assert payload["profile_name"] == "Italy trip"
    assert written["profile_name"] == "Italy trip"
    assert written["preset"] == "trip-hardlink-collection"


def test_cli_workflow_profile_validate_reports_valid_profile(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "cleanup-profile.json"
    profile_path.write_text(
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

    exit_code = main(["profile-validate", str(profile_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["valid"] is True
    assert payload["workflow"] == "cleanup"
    assert payload["command"].startswith("media-manager workflow run cleanup")


def test_cli_workflow_profile_run_delegates_to_trip_handler(tmp_path: Path, capsys, monkeypatch) -> None:
    profile_path = tmp_path / "trip-profile.json"
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

    captured_args: list[str] = []

    def fake_trip_handler(args: list[str]) -> int:
        captured_args.extend(args)
        print("trip-handler-called")
        return 0

    monkeypatch.setitem(DELEGATE_HANDLERS, "trip", fake_trip_handler)

    exit_code = main(["profile-run", str(profile_path), "--show-command"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "media-manager workflow run trip" in captured.out
    assert "trip-handler-called" in captured.out
    assert captured_args == [
        "--source",
        "C:/Phone",
        "--target",
        "E:/Trips",
        "--label",
        "Italy_2025",
        "--start",
        "2025-08-01",
        "--end",
        "2025-08-14",
        "--link",
    ]
