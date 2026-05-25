from __future__ import annotations
import json, sys
from io import StringIO
from pathlib import Path
from unittest import mock
from media_manager.bridge_library import cmd_browse

def test_browse_valid_directory(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")
    (source / "notes.txt").write_bytes(b"text")
    payload = {"root_dir": str(source)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_browse() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["file_count"] == 1  # only jpg, not txt

def test_browse_empty_directory(tmp_path: Path) -> None:
    source = tmp_path / "empty"
    source.mkdir()
    payload = {"root_dir": str(source)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_browse() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["file_count"] == 0

def test_browse_nonexistent_directory(tmp_path: Path) -> None:
    payload = {"root_dir": str(tmp_path / "nope")}
    fake_stdin = StringIO(json.dumps(payload))
    with mock.patch.object(sys, "stdin", fake_stdin):
        assert cmd_browse() == 1  # error exit
