from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_duplicates import build_parser, main


def test_build_parser_supports_workflow_arguments() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--source",
            "C:/media/source",
            "--policy",
            "first",
            "--mode",
            "delete",
            "--show-plan",
            "--save-session",
            "session.json",
            "--json-report",
            "report.json",
            "--audit-log",
            "audit.json",
        ]
    )

    assert args.policy == "first"
    assert args.mode == "delete"
    assert args.show_plan is True
    assert args.save_session == Path("session.json")
    assert args.json_report == Path("report.json")
    assert args.audit_log == Path("audit.json")


def test_main_prints_scan_summary_without_groups(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")

    exit_code = main(["--source", str(source)])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Scanned:" in out
    assert "Exact groups: 1" in out


def test_main_builds_plan_and_saves_session_report_and_audit(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")

    session_path = tmp_path / "duplicate-session.json"
    report_path = tmp_path / "duplicate-report.json"
    audit_path = tmp_path / "duplicate-audit.json"

    exit_code = main(
        [
            "--source",
            str(source),
            "--policy",
            "first",
            "--mode",
            "delete",
            "--show-plan",
            "--save-session",
            str(session_path),
            "--json-report",
            str(report_path),
            "--audit-log",
            str(audit_path),
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Plan:" in out
    assert "Dry run:" in out
    assert "Execution preview:" in out
    assert session_path.exists()
    assert report_path.exists()
    assert audit_path.exists()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["scan"]["exact_groups"] == 1
    assert payload["dry_run"]["planned_count"] == 1
    assert payload["execution_preview"]["executable_count"] == 1

    audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit_payload["scan"]["exact_groups"] == 1
    assert audit_payload["apply_requested"] is False
    assert audit_payload["execution_status"] == "planned_only"
    assert audit_payload["recommended_exit_code"] == 0
    assert audit_payload["execution_run"] is None


def test_main_can_restore_saved_session(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")

    session_path = tmp_path / "duplicate-session.json"
    save_exit = main(
        [
            "--source",
            str(source),
            "--policy",
            "first",
            "--save-session",
            str(session_path),
        ]
    )
    assert save_exit == 0
    capsys.readouterr()

    load_exit = main(
        [
            "--source",
            str(source),
            "--load-session",
            str(session_path),
            "--show-plan",
        ]
    )

    out = capsys.readouterr().out
    assert load_exit == 0
    assert "Decisions: 1" in out
    assert "resolved=1" in out


def test_main_apply_delete_sends_file_to_trash(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    keep = source / "one.jpg"
    remove = source / "two.jpg"
    keep.write_bytes(b"duplicate-bytes")
    remove.write_bytes(b"duplicate-bytes")

    trashed: list[str] = []

    def fake_send2trash(path_str: str) -> None:
        trashed.append(path_str)
        Path(path_str).unlink()

    monkeypatch.setattr("media_manager.execution_runner.send2trash", fake_send2trash)

    exit_code = main(
        [
            "--source",
            str(source),
            "--policy",
            "first",
            "--mode",
            "delete",
            "--apply",
            "--yes",
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Execution run:" in out
    assert keep.exists()
    assert not remove.exists()
    assert trashed == [str(remove)]


def test_main_apply_returns_nonzero_when_delete_is_blocked(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    keep = source / "IMG_0001.jpg"
    remove = source / "IMG_0002.jpg"
    sidecar = source / "IMG_0002.xmp"
    keep.write_bytes(b"duplicate-bytes")
    remove.write_bytes(b"duplicate-bytes")
    sidecar.write_bytes(b"xmp")

    trashed: list[str] = []

    def fake_send2trash(path_str: str) -> None:
        trashed.append(path_str)
        Path(path_str).unlink()

    monkeypatch.setattr("media_manager.execution_runner.send2trash", fake_send2trash)

    exit_code = main(
        [
            "--source",
            str(source),
            "--policy",
            "first",
            "--mode",
            "delete",
            "--apply",
            "--yes",
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 3
    assert "Execution run:" in out
    assert keep.exists()
    assert remove.exists()
    assert trashed == []
