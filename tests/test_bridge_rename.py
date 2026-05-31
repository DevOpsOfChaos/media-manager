from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest import mock

from media_manager.bridge_rename import cmd_preview, cmd_apply


def test_rename_preview_valid_input(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.bridge_rename.build_rename_dry_run",
        lambda options, **_: type(
            "FakeDryRun", (),
            {
                "entries": [
                    type("FakeEntry", (), {
                        "source_path": source / "photo.jpg",
                        "target_path": source / "photo_renamed.jpg",
                        "status": "planned",
                        "reason": "",
                    })()
                ],
                "planned_count": 1,
                "skipped_count": 0,
                "conflict_count": 0,
                "error_count": 0,
            },
        )(),
    )

    payload = {"source_dir": str(source), "template": "{stem}"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_preview()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "rename_preview"
    assert output["planned_count"] == 1
    assert len(output["entries"]) == 1
    assert output["entries"][0]["status"] == "planned"


def test_rename_preview_missing_source_dir() -> None:
    payload = {"template": "{stem}"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_preview()

    assert exit_code == 1
    err = json.loads(fake_stderr.getvalue())
    assert "source_dir is required" in err["error"]


def test_rename_preview_invalid_json() -> None:
    fake_stdin = StringIO("not json")
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_preview()

    assert exit_code == 1
    err = json.loads(fake_stderr.getvalue())
    assert "Invalid JSON" in err["error"]


def test_rename_preview_empty_stdin() -> None:
    fake_stdin = StringIO("")
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_preview()

    assert exit_code == 1
    err = json.loads(fake_stderr.getvalue())
    assert "Empty stdin" in err["error"]


def test_rename_preview_nonexistent_source_dir(tmp_path: Path) -> None:
    payload = {"source_dir": str(tmp_path / "nope")}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_preview()

    assert exit_code == 1
    err = json.loads(fake_stderr.getvalue())
    assert "does not exist" in err["error"]


def test_rename_apply_valid_input(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "img.png").write_bytes(b"png")

    monkeypatch.setattr(
        "media_manager.bridge_rename.build_rename_dry_run",
        lambda options, **_: type(
            "FakeDryRun", (),
            {
                "entries": [],
                "planned_count": 1,
                "skipped_count": 0,
                "conflict_count": 0,
                "error_count": 0,
            },
        )(),
    )
    monkeypatch.setattr(
        "media_manager.bridge_rename.execute_rename_dry_run",
        lambda dry_run, apply=False: type(
            "FakeResult", (),
            {
                "renamed_count": 0,
                "skipped_count": 0,
                "error_count": 0,
                "conflict_count": 0,
            },
        )(),
    )

    payload = {"source_dir": str(source), "template": "{stem}"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_apply()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "rename_apply"
    assert output["renamed_count"] == 0


def test_rename_apply_invalid_json() -> None:
    fake_stdin = StringIO("{invalid")
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_apply()

    assert exit_code == 1
    err = json.loads(fake_stderr.getvalue())
    assert "Invalid JSON" in err["error"]
