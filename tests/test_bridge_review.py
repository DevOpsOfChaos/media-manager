from __future__ import annotations

import json
import os
import sys
from io import StringIO
from pathlib import Path
from unittest import mock

from media_manager.bridge_review import cmd_save_session, cmd_load_session


def test_save_session_writes_decisions(tmp_path: Path) -> None:
    session_path = tmp_path / "review_session.json"
    decisions = {"group-1": "/keep/path.jpg", "group-2": "/keep/other.jpg"}

    payload = {
        "session_path": str(session_path),
        "decisions": decisions,
        "source_kind": "exact",
    }
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.dict(os.environ, {"MEDIA_MANAGER_HOME": str(tmp_path)}), \
         mock.patch.object(sys, "stdin", fake_stdin), \
         mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_save_session()

    assert exit_code == 0
    assert session_path.exists()
    saved = json.loads(session_path.read_text(encoding="utf-8"))
    assert saved["decision_count"] == 2
    assert saved["decisions"] == decisions


def test_load_session_reads_decisions(tmp_path: Path) -> None:
    session_path = tmp_path / "review_session.json"
    session_data = {
        "schema_version": 1,
        "source_kind": "similar",
        "decisions": {"g1": "keep.jpg"},
        "decision_count": 1,
    }
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text(json.dumps(session_data), encoding="utf-8")

    payload = {"session_path": str(session_path)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.dict(os.environ, {"MEDIA_MANAGER_HOME": str(tmp_path)}), \
         mock.patch.object(sys, "stdin", fake_stdin), \
         mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_load_session()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["decision_count"] == 1
    assert output["decisions"] == {"g1": "keep.jpg"}


def test_save_then_load_roundtrip(tmp_path: Path) -> None:
    session_path = tmp_path / "roundtrip.json"
    decisions = {"group-a": "/a.jpg"}

    # Save
    payload = {"session_path": str(session_path), "decisions": decisions}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.dict(os.environ, {"MEDIA_MANAGER_HOME": str(tmp_path)}), \
         mock.patch.object(sys, "stdin", fake_stdin), \
         mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_save_session() == 0

    # Load
    payload2 = {"session_path": str(session_path)}
    fake_stdin2 = StringIO(json.dumps(payload2))
    fake_stdout2 = StringIO()
    with mock.patch.dict(os.environ, {"MEDIA_MANAGER_HOME": str(tmp_path)}), \
         mock.patch.object(sys, "stdin", fake_stdin2), \
         mock.patch.object(sys, "stdout", fake_stdout2):
        assert cmd_load_session() == 0

    output = json.loads(fake_stdout2.getvalue())
    assert output["decisions"] == decisions
