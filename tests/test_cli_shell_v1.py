from __future__ import annotations

import json

from media_manager.cli_shell import main


def test_cli_shell_dump_model_outputs_workflows_and_problems(capsys) -> None:
    exit_code = main(["--dump-model"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert any(item["name"] == "cleanup" for item in payload["workflows"])
    assert any(item["name"] == "build-trip-collection" for item in payload["problems"])


def test_cli_shell_preview_workflow_outputs_example_command(capsys) -> None:
    exit_code = main(["--preview-workflow", "rename"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "media-manager workflow run rename" in captured.out
    assert "--template" in captured.out


def test_cli_shell_preview_problem_outputs_recommended_command(capsys) -> None:
    exit_code = main(["--preview-problem", "messy-multi-source-library"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "media-manager workflow run cleanup" in captured.out
