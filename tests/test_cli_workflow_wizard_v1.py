from __future__ import annotations

import json

from media_manager.cli_workflow import main


def test_workflow_wizard_recommends_cleanup_for_multi_source_duplicates(capsys) -> None:
    exit_code = main(["wizard", "--source-count", "3", "--has-duplicates", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["recommended_workflow"]["name"] == "cleanup"
    assert payload["confidence"] == "high"
    assert payload["command_suggestions"]


def test_workflow_wizard_recommends_trip_when_date_range_is_known(capsys) -> None:
    exit_code = main(["wizard", "--wants-trip", "--date-range-known", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["recommended_workflow"]["name"] == "trip"
    assert payload["confidence"] == "high"


def test_workflow_wizard_recommends_rename_when_naming_is_primary(capsys) -> None:
    exit_code = main(["wizard", "--wants-rename", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["recommended_workflow"]["name"] == "rename"
    assert payload["matched_problem"] is None
