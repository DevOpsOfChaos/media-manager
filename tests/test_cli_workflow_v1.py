from __future__ import annotations

import json

from media_manager.cli_workflow import main


def test_workflow_list_json_contains_cleanup_and_trip(capsys) -> None:
    exit_code = main(["list", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    names = {item["name"] for item in payload["workflows"]}
    assert "trip" in names
    assert "duplicates" in names


def test_workflow_show_cleanup_prints_summary(capsys) -> None:
    exit_code = main(["show", "cleanup"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Cleanup workflow" in captured.out
    assert "Best for:" in captured.out


def test_workflow_recommend_returns_cleanup_for_messy_sources(capsys) -> None:
    exit_code = main(["recommend", "messy-multi-source-library", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["problem"]["name"] == "messy-multi-source-library"
    assert payload["recommended_workflow"]["name"] == "cleanup"


def test_workflow_run_delegates_to_trip(monkeypatch) -> None:
    called = {}

    def fake_trip_main(argv: list[str] | None = None) -> int:
        called["argv"] = list(argv or [])
        return 7

    monkeypatch.setattr("media_manager.cli_workflow.DELEGATE_HANDLERS", {"trip": fake_trip_main})

    exit_code = main(["run", "trip", "--source", "A", "--target", "B"])

    assert exit_code == 7
    assert called["argv"] == ["--source", "A", "--target", "B"]
