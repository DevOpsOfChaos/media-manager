"""Tests for the runtime diagnostics bridge module."""

import json
from io import StringIO
from unittest.mock import patch

from media_manager.bridge_diagnostics import cmd_diagnostics, main


class TestCmdDiagnostics:
    def test_returns_valid_json(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cmd_diagnostics()
        assert exit_code == 0
        data = json.loads(mock_stdout.getvalue())
        assert isinstance(data, dict)

    def test_reports_python_version(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cmd_diagnostics()
        data = json.loads(mock_stdout.getvalue())
        assert "python_version" in data
        assert len(data["python_version"]) > 0

    def test_media_manager_import_ok(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cmd_diagnostics()
        data = json.loads(mock_stdout.getvalue())
        assert data["media_manager_import"]["ok"] is True

    def test_bridge_settings_import_ok(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cmd_diagnostics()
        data = json.loads(mock_stdout.getvalue())
        assert data["bridge_settings_import"]["ok"] is True

    def test_reports_settings_path(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cmd_diagnostics()
        data = json.loads(mock_stdout.getvalue())
        assert "settings_path" in data
        assert data["settings_path"].endswith("gui-settings.json")

    def test_reports_settings_file_exists(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cmd_diagnostics()
        data = json.loads(mock_stdout.getvalue())
        assert "settings_file_exists" in data
        assert isinstance(data["settings_file_exists"], bool)


class TestMain:
    def test_main_returns_zero(self):
        with patch("sys.stdout", new_callable=StringIO):
            exit_code = main([])
        assert exit_code == 0

    def test_main_output_structure(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main([])
        data = json.loads(mock_stdout.getvalue())
        required_keys = [
            "python_version",
            "media_manager_import",
            "bridge_settings_import",
            "settings_path",
            "settings_file_exists",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"
