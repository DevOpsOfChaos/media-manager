from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_doctor import main as doctor_main
from media_manager.core.doctor import DoctorOptions, build_doctor_payload, build_doctor_report


def test_doctor_reports_missing_source_as_error(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing"

    exit_code = doctor_main(["--json", "--source", str(missing)])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "blocked"
    assert payload["summary"]["error_count"] == 1
    assert payload["diagnostics"][0]["code"] == "source.missing"


def test_doctor_previews_include_exclude_patterns(tmp_path: Path, capsys) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "keep.jpg").write_text("x", encoding="utf-8")
    (source / "skip.jpg").write_text("x", encoding="utf-8")
    (source / "notes.txt").write_text("x", encoding="utf-8")

    exit_code = doctor_main(
        [
            "--json",
            "--command",
            "organize",
            "--source",
            str(source),
            "--target",
            str(tmp_path / "out"),
            "--include-pattern",
            "*.jpg",
            "--exclude-pattern",
            "skip*",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    preview = payload["source_previews"][0]
    assert preview["scanned_file_count"] == 3
    assert preview["included_file_count"] == 1
    assert preview["excluded_by_include_count"] == 1
    assert preview["excluded_by_exclude_count"] == 1
    assert payload["include_patterns"] == ["*.jpg"]
    assert payload["exclude_patterns"] == ["skip*"]


def test_doctor_writes_report_json(tmp_path: Path) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "image.jpg").write_text("x", encoding="utf-8")
    report_path = tmp_path / "reports" / "doctor.json"

    exit_code = doctor_main(["--source", str(source), "--report-json", str(report_path)])

    assert exit_code == 0
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["included_file_count"] == 1


def test_build_doctor_report_can_fail_on_filter_without_cli(tmp_path: Path) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "image.jpg").write_text("x", encoding="utf-8")

    report = build_doctor_report(
        DoctorOptions(
            source_dirs=(source,),
            include_patterns=("*.png",),
        )
    )
    payload = build_doctor_payload(report)

    assert report.error_count == 0
    assert report.warning_count == 1
    assert payload["status"] == "review_recommended"
    assert payload["diagnostics"][0]["code"] == "filters.no_matches"
