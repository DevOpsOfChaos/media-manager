"""Tests for the run history bridge module."""

import json
import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from media_manager.bridge_history import (
    DEFAULT_RUNS_PATH,
    _resolve_runs_path,
    cmd_get,
    cmd_list,
    main,
)


# ── path resolution ──


class TestResolveRunsPath:
    def test_default_returns_dot_media_manager(self):
        result = _resolve_runs_path()
        assert result == DEFAULT_RUNS_PATH
        assert result.name == "runs"

    def test_cli_arg_has_priority(self):
        result = _resolve_runs_path(cli_path="/custom/runs")
        assert result == Path("/custom/runs")

    def test_env_var_falls_back(self, monkeypatch):
        monkeypatch.setenv("MEDIA_MANAGER_RUNS_PATH", "/env/runs")
        result = _resolve_runs_path()
        assert result == Path("/env/runs")

    def test_cli_overrides_env(self, monkeypatch):
        monkeypatch.setenv("MEDIA_MANAGER_RUNS_PATH", "/env/runs")
        result = _resolve_runs_path(cli_path="/cli/runs")
        assert result == Path("/cli/runs")


# ── list ──


class TestCmdList:
    def test_list_empty_dir(self, tmp_path):
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_list(runs_dir, limit=50)
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["run_count"] == 0
        assert data["runs"] == []

    def test_list_missing_dir(self, tmp_path):
        runs_dir = tmp_path / "nonexistent"
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_list(runs_dir, limit=50)
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["run_count"] == 0

    def test_list_with_artifacts(self, tmp_path):
        runs_dir = tmp_path / "runs"
        run_dir = runs_dir / "20260511-120000-organize"
        run_dir.mkdir(parents=True)
        cmd_json = run_dir / "command.json"
        cmd_json.write_text(json.dumps({"command": "organize", "apply_requested": False, "exit_code": 0}))
        (run_dir / "report.json").write_text("{}")
        (run_dir / "review.json").write_text("{}")
        (run_dir / "summary.txt").write_text("Done.")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_list(runs_dir, limit=50)
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["run_count"] == 1
        run = data["runs"][0]
        assert run["run_id"] == "20260511-120000-organize"
        assert run["command"] == "organize"
        assert run["mode"] == "preview"
        assert run["valid"] is True


# ── get ──


class TestCmdGet:
    def test_get_existing_run(self, tmp_path):
        runs_dir = tmp_path / "runs"
        run_dir = runs_dir / "20260511-test"
        run_dir.mkdir(parents=True)
        (run_dir / "command.json").write_text(json.dumps({
            "command": "organize", "apply_requested": True, "exit_code": 0, "created_at_utc": "2026-05-11T12:00:00Z"
        }))
        (run_dir / "report.json").write_text(json.dumps({
            "outcome_report": {"status": "ok", "next_action": "review"}
        }))
        (run_dir / "review.json").write_text("{}")
        (run_dir / "summary.txt").write_text("Organized 10 files.")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_get(runs_dir, "20260511-test")
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["run_id"] == "20260511-test"
        assert data["command"] == "organize"
        assert data["mode"] == "apply"
        assert data["summary"] == "Organized 10 files."
        assert data["command_json"]["command"] == "organize"
        assert data["report_outcome"]["status"] == "ok"

    def test_get_missing_run(self, tmp_path):
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            exit_code = cmd_get(runs_dir, "nonexistent")
        assert exit_code == 1
        assert "Run not found" in mock_stderr.getvalue()

    def test_get_partial_match(self, tmp_path):
        runs_dir = tmp_path / "runs"
        run_dir = runs_dir / "20260511-120000"
        run_dir.mkdir(parents=True)
        (run_dir / "command.json").write_text("{}")
        (run_dir / "report.json").write_text("{}")
        (run_dir / "review.json").write_text("{}")
        (run_dir / "summary.txt").write_text("x")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_get(runs_dir, "20260511-")
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["run_id"] == "20260511-120000"


# ── main ──


class TestMain:
    def test_main_list(self, tmp_path):
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        with patch("sys.stdout", new_callable=StringIO):
            exit_code = main(["list", "--run-dir", str(runs_dir)])
        assert exit_code == 0

    def test_main_get(self, tmp_path):
        runs_dir = tmp_path / "runs"
        run_dir = runs_dir / "test-run"
        run_dir.mkdir(parents=True)
        (run_dir / "command.json").write_text("{}")
        (run_dir / "report.json").write_text("{}")
        (run_dir / "review.json").write_text("{}")
        (run_dir / "summary.txt").write_text("ok")

        with patch("sys.stdout", new_callable=StringIO):
            exit_code = main(["get", "test-run", "--run-dir", str(runs_dir)])
        assert exit_code == 0

    def test_main_get_missing_run_id(self):
        with patch("sys.stderr", new_callable=StringIO):
            exit_code = main(["get"])
        assert exit_code == 2
