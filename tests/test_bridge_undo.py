from __future__ import annotations

import json
import os
import sys
from io import StringIO
from pathlib import Path
from unittest import mock

from media_manager.bridge_undo import cmd_preview, cmd_apply


def _write_journal(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": 1,
        "journal_type": "execution_journal",
        "command_name": "organize",
        "apply_requested": True,
        "exit_code": 0,
        "created_at_utc": "2024-01-01T00:00:00+00:00",
        "entry_count": len(entries),
        "reversible_entry_count": sum(1 for e in entries if e.get("reversible")),
        "outcome_summary": {},
        "reason_summary": {},
        "entries": entries,
    }, indent=2), encoding="utf-8")


def test_undo_preview_shows_planned_actions(tmp_path: Path) -> None:
    target = tmp_path / "target" / "photo.jpg"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"content")
    journal = tmp_path / "journal.json"
    _write_journal(journal, [{
        "source_path": str(tmp_path / "source" / "photo.jpg"),
        "target_path": str(target),
        "outcome": "copied",
        "reason": "executed organize action",
        "reversible": True,
        "undo_action": "delete_target",
        "undo_from_path": str(target),
        "undo_to_path": None,
    }])

    fake_stdin = StringIO(json.dumps({"journal_path": str(journal)}))
    fake_stdout = StringIO()
    with mock.patch.dict(os.environ, {"MEDIA_MANAGER_HOME": str(tmp_path)}), \
         mock.patch.object(sys, "stdin", fake_stdin), \
         mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_preview()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "preview"
    assert output["planned_count"] == 1
    assert output["undone_count"] == 0


def test_undo_apply_executes_reverse_actions(tmp_path: Path) -> None:
    target = tmp_path / "target" / "photo.jpg"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"content")
    journal = tmp_path / "journal.json"
    _write_journal(journal, [{
        "source_path": str(tmp_path / "source" / "photo.jpg"),
        "target_path": str(target),
        "outcome": "copied",
        "reason": "executed organize action",
        "reversible": True,
        "undo_action": "delete_target",
        "undo_from_path": str(target),
        "undo_to_path": None,
    }])

    assert target.exists()
    fake_stdin = StringIO(json.dumps({"journal_path": str(journal)}))
    fake_stdout = StringIO()
    with mock.patch.dict(os.environ, {"MEDIA_MANAGER_HOME": str(tmp_path)}), \
         mock.patch.object(sys, "stdin", fake_stdin), \
         mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_apply()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "apply"
    assert output["undone_count"] == 1
    assert not target.exists()


def test_undo_apply_move_back(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    target = tmp_path / "target" / "photo.jpg"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"content")

    journal = tmp_path / "journal.json"
    _write_journal(journal, [{
        "source_path": str(source / "photo.jpg"),
        "target_path": str(target),
        "outcome": "moved",
        "reason": "executed organize action",
        "reversible": True,
        "undo_action": "move_back",
        "undo_from_path": str(target),
        "undo_to_path": str(source / "photo.jpg"),
    }])

    fake_stdin = StringIO(json.dumps({"journal_path": str(journal)}))
    fake_stdout = StringIO()
    with mock.patch.dict(os.environ, {"MEDIA_MANAGER_HOME": str(tmp_path)}), \
         mock.patch.object(sys, "stdin", fake_stdin), \
         mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_apply()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["undone_count"] == 1
    assert not target.exists()
    assert (source / "photo.jpg").exists()
