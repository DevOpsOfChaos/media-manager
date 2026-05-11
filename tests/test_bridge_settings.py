"""Tests for the Tauri desktop settings bridge module."""

import json
import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from media_manager.bridge_settings import (
    DEFAULT_SETTINGS_PATH,
    _resolve_settings_path,
    build_parser,
    cmd_read,
    cmd_reset,
    cmd_write,
    main,
)
from media_manager.core.gui_settings_model import default_gui_settings


# ── path resolution tests ──


class TestResolveSettingsPath:
    def test_default_returns_home_path(self):
        result = _resolve_settings_path()
        assert result == DEFAULT_SETTINGS_PATH

    def test_cli_arg_has_priority(self):
        result = _resolve_settings_path(cli_path="/custom/path.json")
        assert result == Path("/custom/path.json")

    def test_env_var_falls_back(self, monkeypatch):
        monkeypatch.setenv("MEDIA_MANAGER_SETTINGS_PATH", "/env/path.json")
        result = _resolve_settings_path()
        assert result == Path("/env/path.json")

    def test_cli_overrides_env(self, monkeypatch):
        monkeypatch.setenv("MEDIA_MANAGER_SETTINGS_PATH", "/env/path.json")
        result = _resolve_settings_path(cli_path="/cli/path.json")
        assert result == Path("/cli/path.json")


# ── read ──


class TestBridgeRead:
    def test_read_returns_valid_json(self, tmp_path):
        sp = tmp_path / "settings.json"
        sp.write_text(json.dumps({"language": "de", "theme": "modern-dark"}))
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_read(sp)
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["language"] == "de"
        assert data["theme"] == "modern-dark"

    def test_read_output_is_dict(self, tmp_path):
        sp = tmp_path / "settings.json"
        sp.write_text(json.dumps({}))
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_read(sp)
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert isinstance(data, dict)

    def test_read_missing_file_uses_defaults(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_read(Path("/nonexistent/settings.json"))
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["language"] == "en"

    def test_read_bad_permissions_reports_error(self, tmp_path):
        sp = tmp_path / "settings.json"
        sp.mkdir()  # directory, not file — will fail to read
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            exit_code = cmd_read(sp)
        assert exit_code == 1
        assert "Cannot read" in mock_stderr.getvalue()


# ── write ──


class TestBridgeWrite:
    def test_write_normalizes_input(self, tmp_path):
        sp = tmp_path / "settings.json"
        input_json = json.dumps({"language": "de", "theme": "dark"})
        with (
            patch("sys.stdin", StringIO(input_json)),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            exit_code = cmd_write(sp)
        assert exit_code == 0
        output = json.loads(mock_stdout.getvalue())
        assert output["language"] == "de"
        assert output["theme"] == "modern-dark"
        # Verify file was written
        assert sp.exists()
        written = json.loads(sp.read_text())
        assert written["language"] == "de"

    def test_write_rejects_invalid_json(self, tmp_path):
        sp = tmp_path / "settings.json"
        with (
            patch("sys.stdin", StringIO("not json")),
            patch("sys.stderr", new_callable=StringIO),
        ):
            exit_code = cmd_write(sp)
        assert exit_code == 1

    def test_write_rejects_non_dict(self, tmp_path):
        sp = tmp_path / "settings.json"
        with (
            patch("sys.stdin", StringIO("[1, 2, 3]")),
            patch("sys.stderr", new_callable=StringIO),
        ):
            exit_code = cmd_write(sp)
        assert exit_code == 1

    def test_write_to_custom_path(self, tmp_path):
        sp = tmp_path / "custom" / "nested" / "settings.json"
        input_json = json.dumps({"language": "de"})
        with (
            patch("sys.stdin", StringIO(input_json)),
            patch("sys.stdout", new_callable=StringIO),
        ):
            exit_code = cmd_write(sp)
        assert exit_code == 0
        assert sp.exists()


# ── reset ──


class TestBridgeReset:
    def test_reset_returns_defaults(self, tmp_path):
        sp = tmp_path / "settings.json"
        # Pre-populate with non-default values
        sp.write_text(json.dumps({"language": "de", "theme": "modern-light"}))
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_reset(sp)
        assert exit_code == 0
        output = json.loads(mock_stdout.getvalue())
        assert output["language"] == "en"
        assert output["theme"] == "modern-dark"

    def test_reset_output_matches_defaults(self, tmp_path):
        sp = tmp_path / "settings.json"
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_reset(sp)
        defaults = default_gui_settings()
        output = json.loads(mock_stdout.getvalue())
        for key in defaults:
            assert key in output


# ── main with argparse ──


class TestBridgeMain:
    def test_main_read_default_path(self):
        with patch("sys.stdout", new_callable=StringIO):
            exit_code = main(["read"])
        assert exit_code == 0

    def test_main_read_custom_path(self, tmp_path):
        sp = tmp_path / "s.json"
        sp.write_text(json.dumps({"language": "en"}))
        with patch("sys.stdout", new_callable=StringIO):
            exit_code = main(["read", "--settings-path", str(sp)])
        assert exit_code == 0

    def test_main_write(self, tmp_path):
        sp = tmp_path / "s.json"
        input_json = json.dumps({"language": "en"})
        with (
            patch("sys.stdin", StringIO(input_json)),
            patch("sys.stdout", new_callable=StringIO),
        ):
            exit_code = main(["write", "--settings-path", str(sp)])
        assert exit_code == 0
        assert sp.exists()

    def test_main_reset(self, tmp_path):
        sp = tmp_path / "s.json"
        with patch("sys.stdout", new_callable=StringIO):
            exit_code = main(["reset", "--settings-path", str(sp)])
        assert exit_code == 0

    def test_main_unknown_action(self):
        with patch("sys.stderr", new_callable=StringIO):
            try:
                main(["bogus"])
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 2

    def test_main_no_args_shows_usage(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            try:
                main([])
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 2
        usage_output = mock_stderr.getvalue()
        assert "arguments" in usage_output.lower()


# ── parser ──


class TestParser:
    def test_parser_accepts_settings_path(self):
        parser = build_parser()
        args = parser.parse_args(["read", "--settings-path", "/test/path.json"])
        assert args.action == "read"
        assert args.settings_path == "/test/path.json"

    def test_parser_defaults_settings_path_to_none(self):
        parser = build_parser()
        args = parser.parse_args(["read"])
        assert args.settings_path is None


# ── env var override in main ──


class TestMainEnvVarOverride:
    def test_main_respects_settings_path_env(self, tmp_path, monkeypatch):
        sp = tmp_path / "env_settings.json"
        sp.write_text(json.dumps({"language": "de"}))
        monkeypatch.setenv("MEDIA_MANAGER_SETTINGS_PATH", str(sp))
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = main(["read"])
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert data["language"] == "de"
