from __future__ import annotations

import argparse
from pathlib import Path

from media_manager.cli_jobs import cmd_jobs, build_parser
from media_manager.core.job_queue import JobQueue


def test_jobs_list(tmp_path: Path, monkeypatch, capsys) -> None:
    jobs_dir = tmp_path / ".media-manager" / "jobs"
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path / ".media-manager"))

    queue = JobQueue(storage_dir=jobs_dir)
    queue.create("test_kind", {"x": 1})

    args = argparse.Namespace(state=None, kind=None, json=False)
    result = cmd_jobs(args)
    captured = capsys.readouterr()
    assert result == 0
    assert "test_kind" in captured.out


def test_jobs_list_json(tmp_path: Path, monkeypatch, capsys) -> None:
    jobs_dir = tmp_path / ".media-manager" / "jobs"
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path / ".media-manager"))

    queue = JobQueue(storage_dir=jobs_dir)
    queue.create("test_kind", {"x": 1})

    args = argparse.Namespace(state=None, kind=None, json=True)
    result = cmd_jobs(args)
    captured = capsys.readouterr()
    assert result == 0
    assert "test_kind" in captured.out


def test_jobs_filter_by_state(tmp_path: Path, monkeypatch, capsys) -> None:
    jobs_dir = tmp_path / ".media-manager" / "jobs"
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path / ".media-manager"))

    queue = JobQueue(storage_dir=jobs_dir)
    job = queue.create("test_kind", {"x": 1})
    queue.complete(job.job_id)

    args = argparse.Namespace(state="completed", kind=None, json=False)
    result = cmd_jobs(args)
    captured = capsys.readouterr()
    assert result == 0
    assert "test_kind" in captured.out


def test_jobs_filter_by_kind(tmp_path: Path, monkeypatch, capsys) -> None:
    jobs_dir = tmp_path / ".media-manager" / "jobs"
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path / ".media-manager"))

    queue = JobQueue(storage_dir=jobs_dir)
    queue.create("kind_a", {"x": 1})
    queue.create("kind_b", {"x": 2})

    args = argparse.Namespace(state=None, kind="kind_a", json=False)
    result = cmd_jobs(args)
    captured = capsys.readouterr()
    assert result == 0
    assert "kind_a" in captured.out
    assert "kind_b" not in captured.out


def test_build_parser() -> None:
    parser = build_parser()
    args = parser.parse_args(["--state", "pending", "--kind", "organize", "--json"])
    assert args.state == "pending"
    assert args.kind == "organize"
    assert args.json is True
