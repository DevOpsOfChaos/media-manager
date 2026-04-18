from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_duplicates import build_parser, main
from media_manager.similar_images import SimilarImageGroup, SimilarImageMember, SimilarImageScanResult


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
            "--similar-images",
            "--show-similar-groups",
            "--similar-threshold",
            "5",
            "--history-dir",
            "history",
        ]
    )

    assert args.policy == "first"
    assert args.mode == "delete"
    assert args.show_plan is True
    assert args.save_session == Path("session.json")
    assert args.json_report == Path("report.json")
    assert args.similar_images is True
    assert args.show_similar_groups is True
    assert args.similar_threshold == 5
    assert args.history_dir == Path("history")


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


def test_main_builds_plan_and_saves_session_and_report(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")

    session_path = tmp_path / "duplicate-session.json"
    report_path = tmp_path / "duplicate-report.json"

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
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Plan:" in out
    assert "Dry run:" in out
    assert "Execution preview:" in out
    assert session_path.exists()
    assert report_path.exists()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["scan"]["exact_groups"] == 1
    assert payload["dry_run"]["planned_count"] == 1
    assert payload["execution_preview"]["executable_count"] == 1


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


def test_main_apply_delete_executes_removal(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    keep = source / "one.jpg"
    remove = source / "two.jpg"
    keep.write_bytes(b"duplicate-bytes")
    remove.write_bytes(b"duplicate-bytes")

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


def test_main_writes_history_run_log_for_preview(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")
    history_dir = tmp_path / "history"

    exit_code = main(
        [
            "--source",
            str(source),
            "--history-dir",
            str(history_dir),
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Wrote history run log:" in out

    run_logs = sorted(history_dir.glob("*-duplicates-preview-run-log.json"))
    journals = sorted(history_dir.glob("*-duplicates-preview-execution-journal.json"))

    assert len(run_logs) == 1
    assert journals == []

    payload = json.loads(run_logs[0].read_text(encoding="utf-8"))
    assert payload["command_name"] == "duplicates"
    assert payload["apply_requested"] is False
    assert payload["payload"]["scan"]["exact_groups"] == 1


def test_main_writes_history_run_log_and_journal_for_apply(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    keep = source / "one.jpg"
    remove = source / "two.jpg"
    keep.write_bytes(b"duplicate-bytes")
    remove.write_bytes(b"duplicate-bytes")
    history_dir = tmp_path / "history"

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
            "--history-dir",
            str(history_dir),
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Wrote history run log:" in out
    assert "Wrote history journal:" in out

    run_logs = sorted(history_dir.glob("*-duplicates-apply-run-log.json"))
    journals = sorted(history_dir.glob("*-duplicates-apply-execution-journal.json"))

    assert len(run_logs) == 1
    assert len(journals) == 1

    run_log = json.loads(run_logs[0].read_text(encoding="utf-8"))
    journal = json.loads(journals[0].read_text(encoding="utf-8"))

    assert run_log["command_name"] == "duplicates"
    assert run_log["apply_requested"] is True
    assert journal["command_name"] == "duplicates"
    assert journal["apply_requested"] is True
    assert journal["entries"][0]["outcome"] in {"deleted", "preview-delete", "blocked", "deferred", "error"}


def test_main_can_report_similar_image_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")

    similar_result = SimilarImageScanResult(
        scanned_files=2,
        image_files=2,
        hashed_files=2,
        similar_pairs=1,
        similar_groups=[
            SimilarImageGroup(
                anchor_path=source / "one.jpg",
                members=[
                    SimilarImageMember(path=source / "one.jpg", hash_hex="ff00", distance=0),
                    SimilarImageMember(path=source / "two.jpg", hash_hex="ff10", distance=2),
                ],
            )
        ],
        errors=0,
    )

    monkeypatch.setattr("media_manager.cli_duplicates.scan_similar_images", lambda config: similar_result)

    exit_code = main([
        "--source", str(source),
        "--similar-images",
        "--show-similar-groups",
    ])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Similar images:" in out
    assert "[Similar Group 1]" in out
