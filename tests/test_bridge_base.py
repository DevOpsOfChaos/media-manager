"""Tests for the bridge_base utility module."""
from __future__ import annotations

import json
from io import StringIO
from unittest.mock import patch

from media_manager.bridge_base import emit, fail


class TestEmit:
    def test_emit_writes_json_to_stdout(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            emit({"key": "value", "num": 42})
        data = json.loads(mock_stdout.getvalue())
        assert data == {"key": "value", "num": 42}

    def test_emit_empty_dict(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            emit({})
        data = json.loads(mock_stdout.getvalue())
        assert data == {}

    def test_emit_unicode_keys(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            emit({"name": "J\u00fcrgen", "city": "M\u00fcnchen"})
        data = json.loads(mock_stdout.getvalue())
        assert data["name"] == "J\u00fcrgen"
        assert data["city"] == "M\u00fcnchen"

    def test_emit_nested_structures(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            emit({"data": [1, 2, 3], "nested": {"a": 1}})
        data = json.loads(mock_stdout.getvalue())
        assert data["data"] == [1, 2, 3]
        assert data["nested"]["a"] == 1

    def test_emit_large_payload(self):
        payload = {"items": list(range(1000))}
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            emit(payload)
        data = json.loads(mock_stdout.getvalue())
        assert len(data["items"]) == 1000


class TestFail:
    def test_fail_writes_error_json_to_stderr(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            exit_code = fail("something went wrong")
        assert exit_code == 1
        data = json.loads(mock_stderr.getvalue())
        assert data == {"error": "something went wrong"}

    def test_fail_custom_exit_code(self):
        with patch("sys.stderr", new_callable=StringIO):
            exit_code = fail("not found", exit_code=4)
        assert exit_code == 4

    def test_fail_empty_message(self):
        with patch("sys.stderr", new_callable=StringIO):
            exit_code = fail("")
        assert exit_code == 1

    def test_fail_unicode_message(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            exit_code = fail("error \u2603 snowman")
        assert exit_code == 1
        err = mock_stderr.getvalue()
        data = json.loads(err)
        assert data["error"] == "error \u2603 snowman"

    def test_fail_default_exit_code_is_one(self):
        exit_code = fail("test")
        assert exit_code == 1


class TestEmitAndFailIntegration:
    """Verify emit and fail don't interfere with each other."""
    def test_emit_then_fail_separate_streams(self):
        with (
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
            patch("sys.stderr", new_callable=StringIO) as mock_stderr,
        ):
            emit({"ok": True})
            fail("error occurred")
        stdout_data = json.loads(mock_stdout.getvalue())
        stderr_data = json.loads(mock_stderr.getvalue())
        assert stdout_data == {"ok": True}
        assert stderr_data == {"error": "error occurred"}
