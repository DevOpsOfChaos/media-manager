from __future__ import annotations

import json

from media_manager.cli_shell import main


def test_cli_shell_dump_forms_outputs_form_models(capsys) -> None:
    exit_code = main(["--dump-forms"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert any(item["workflow_name"] == "cleanup" for item in payload["forms"])


def test_cli_shell_preview_form_outputs_single_form_model(capsys) -> None:
    exit_code = main(["--preview-form", "trip"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["workflow_name"] == "trip"
    assert any(item["name"] == "label" for item in payload["fields"])
