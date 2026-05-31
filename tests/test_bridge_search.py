from __future__ import annotations
import json
import sys
from io import StringIO
from pathlib import Path
from unittest import mock
from media_manager.bridge_search import cmd_search


def test_search_by_filename(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "beach_sunset.jpg").write_bytes(b"x")
    (source / "mountain_view.jpg").write_bytes(b"x")
    (source / "notes.txt").write_bytes(b"text")
    payload = {"source_dir": str(source), "query": "beach"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_search() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["query"] == "beach"
    assert output["total_matches"] == 1
    assert "beach_sunset" in output["results"][0]["name"]


def test_search_by_path(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    sub = source / "vacation"
    sub.mkdir()
    (sub / "photo.jpg").write_bytes(b"x")
    payload = {"source_dir": str(source), "query": "vacation", "fields": ["path"]}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_search() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_matches"] == 1


def test_search_case_insensitive(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "Beach_Sunset.JPG").write_bytes(b"x")
    payload = {"source_dir": str(source), "query": "beach"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_search() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_matches"] == 1


def test_search_no_results(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"x")
    payload = {"source_dir": str(source), "query": "nonexistent"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_search() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_matches"] == 0
    assert output["results"] == []


def test_search_max_results(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    for i in range(10):
        (source / f"beach_{i}.jpg").write_bytes(b"x")
    payload = {"source_dir": str(source), "query": "beach", "max_results": 3}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_search() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_matches"] == 10
    assert len(output["results"]) == 3


def test_search_empty_query(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"x")
    payload = {"source_dir": str(source), "query": ""}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stderr", fake_stderr):
        assert cmd_search() == 1
    err_output = json.loads(fake_stderr.getvalue())
    assert "error" in err_output


def test_search_scores_sorted(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    sub = source / "beach_trip"
    sub.mkdir()
    (source / "beach.jpg").write_bytes(b"x")
    (sub / "random.jpg").write_bytes(b"x")
    payload = {"source_dir": str(source), "query": "beach", "fields": ["filename", "path"]}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_search() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_matches"] == 2
    assert output["results"][0]["name"] == "beach.jpg"
    assert output["results"][0]["score"] > output["results"][1]["score"]
