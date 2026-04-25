from __future__ import annotations

import json
from pathlib import Path

from media_manager import cli_app
from media_manager.core.app_profiles import build_app_profile_payload, validate_app_profile


def test_app_profile_validation_and_render_for_duplicates() -> None:
    profile = build_app_profile_payload(
        profile_id="video-duplicates",
        title="Video duplicates",
        command="duplicates",
        values={
            "source_dirs": ["C:/Media"],
            "media_kinds": ["video"],
            "run_dir": "runs",
        },
    )

    validation = validate_app_profile(profile)

    assert validation.valid is True
    assert "media-manager" in validation.command_argv
    assert "duplicates" in validation.command_argv
    assert "--media-kind" in validation.command_argv
    assert "video" in validation.command_argv


def test_app_profiles_cli_init_list_render(tmp_path: Path, capsys) -> None:
    profile_dir = tmp_path / "profiles"
    profile_path = profile_dir / "video-duplicates.json"

    assert cli_app.main([
        "profiles",
        "init",
        "--out",
        str(profile_path),
        "--command",
        "duplicates",
        "--title",
        "Video duplicate review",
        "--source",
        "C:/Media",
        "--media-kind",
        "video",
        "--run-dir",
        "runs",
    ]) == 0
    init_payload = json.loads(capsys.readouterr().out)
    assert init_payload["valid"] is True
    assert profile_path.exists()

    assert cli_app.main(["profiles", "list", "--profile-dir", str(profile_dir), "--json"]) == 0
    list_payload = json.loads(capsys.readouterr().out)
    assert list_payload["summary"]["profile_count"] == 1
    assert list_payload["profiles"][0]["command"] == "duplicates"

    assert cli_app.main(["profiles", "render", str(profile_path), "--json"]) == 0
    render_payload = json.loads(capsys.readouterr().out)
    assert render_payload["valid"] is True
    assert render_payload["command_argv"][:2] == ["media-manager", "duplicates"]
