from __future__ import annotations
import json
import sys
from io import StringIO
from pathlib import Path
from unittest import mock
from media_manager.bridge_stats import cmd_library_stats, cmd_size_report


def test_stats_with_media_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"x" * 100)
    (source / "video.mp4").write_bytes(b"x" * 200)
    (source / "notes.txt").write_bytes(b"text")
    payload = {"source_dir": str(source)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_library_stats() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_files"] == 2
    assert output["total_size_bytes"] == 300
    assert ".jpg" in output["by_extension"]
    assert ".mp4" in output["by_extension"]
    assert ".txt" not in output["by_extension"]


def test_stats_empty_directory(tmp_path: Path) -> None:
    source = tmp_path / "empty"
    source.mkdir()
    payload = {"source_dir": str(source)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_library_stats() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_files"] == 0
    assert output["total_size_bytes"] == 0


def test_size_report_largest(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "small.jpg").write_bytes(b"x" * 10)
    (source / "big.jpg").write_bytes(b"x" * 1000)
    (source / "medium.png").write_bytes(b"x" * 100)
    payload = {"source_dir": str(source), "top_n": 2}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_size_report() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["file_count"] == 3
    assert output["total_size_bytes"] == 1110
    assert len(output["largest_files"]) == 2
    assert output["largest_files"][0]["size_bytes"] == 1000
    assert output["largest_files"][1]["size_bytes"] == 100


def test_size_report_duplicate_space(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"same_content")
    (source / "b.jpg").write_bytes(b"same_content")
    (source / "c.jpg").write_bytes(b"same_content")
    (source / "d.jpg").write_bytes(b"other")
    payload = {"source_dir": str(source)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_size_report() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["file_count"] == 4
    assert output["duplicate_space_wasted_bytes"] == 24  # 12 * 2 extra copies


def test_size_report_empty_directory(tmp_path: Path) -> None:
    source = tmp_path / "empty"
    source.mkdir()
    payload = {"source_dir": str(source)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_size_report() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["file_count"] == 0
    assert output["total_size_bytes"] == 0
    assert output["largest_files"] == []
