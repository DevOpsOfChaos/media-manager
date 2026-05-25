from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest import mock

from media_manager.bridge_doctor import cmd_check


def test_doctor_check_valid_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    payload = {
        "command": "organize",
        "source_dirs": [str(source)],
        "target_root": str(tmp_path / "target"),
    }
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_check()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["ready"] is True or output["ready"] is False
    assert "summary" in output
    assert "diagnostics" in output


def test_doctor_check_missing_source(tmp_path: Path) -> None:
    payload = {
        "command": "organize",
        "source_dirs": [str(tmp_path / "nonexistent")],
        "target_root": str(tmp_path / "target"),
    }
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_check()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["ready"] is False
