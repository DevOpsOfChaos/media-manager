from __future__ import annotations
import json, sys
from io import StringIO
from pathlib import Path
from unittest import mock
from media_manager.bridge_trip import cmd_preview

def test_trip_preview_valid(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")
    target = tmp_path / "target"
    target.mkdir()
    payload = {"source_dirs": [str(source)], "target_root": str(target), "label": "test_trip", "start_date": "2020-01-01", "end_date": "2030-12-31", "use_hardlinks": True}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_preview() == 0
    output = json.loads(fake_stdout.getvalue())
    assert "planned_count" in output

def test_trip_preview_empty_source(tmp_path: Path) -> None:
    source = tmp_path / "empty"
    source.mkdir()
    target = tmp_path / "target"
    target.mkdir()
    payload = {"source_dirs": [str(source)], "target_root": str(target), "label": "empty", "start_date": "2020-01-01", "end_date": "2020-12-31", "use_hardlinks": True}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_preview() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["planned_count"] == 0
