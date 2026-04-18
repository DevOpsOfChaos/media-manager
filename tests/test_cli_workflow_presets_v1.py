from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main



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
