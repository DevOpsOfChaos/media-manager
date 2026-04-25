from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_duplicates import main as duplicates_main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_duplicates_can_export_and_import_editable_decision_file(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "a.jpg"
    second = source / "b.jpg"
    _write(first, "same content")
    _write(second, "same content")

    decision_file = tmp_path / "reports" / "decisions.json"
    report_file = tmp_path / "reports" / "report.json"

    assert duplicates_main(["--source", str(source), "--export-decisions", str(decision_file)]) == 0
    payload = json.loads(decision_file.read_text(encoding="utf-8"))

    assert payload["type"] == "duplicate_decisions"
    assert payload["exact_group_count"] == 1
    assert payload["groups"][0]["status"] == "unresolved"

    payload["groups"][0]["selected_keep_path"] = str(first)
    decision_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert duplicates_main([
        "--source",
        str(source),
        "--import-decisions",
        str(decision_file),
        "--mode",
        "delete",
        "--report-json",
        str(report_file),
    ]) == 0

    report = json.loads(report_file.read_text(encoding="utf-8"))
    assert report["decision_import"]["status"] == "matched"
    assert report["decision_summary"]["from_decision_file_count"] == 1
    assert report["decision_summary"]["undecided_groups"] == 0
    assert report["execution_preview"]["delete_count"] == 1


def test_duplicates_rejects_missing_decision_file(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    _write(source / "a.jpg", "same content")
    _write(source / "b.jpg", "same content")

    assert duplicates_main([
        "--source",
        str(source),
        "--import-decisions",
        str(tmp_path / "missing.json"),
        "--json",
    ]) == 1
