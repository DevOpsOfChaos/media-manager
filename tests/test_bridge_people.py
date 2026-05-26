from __future__ import annotations
import json
import sys
from io import StringIO
from pathlib import Path
from unittest import mock
from media_manager.bridge_people import cmd_catalog_list, cmd_face_ignore, cmd_person_create, cmd_person_merge, cmd_person_rename, cmd_person_reassign

def test_catalog_list_valid(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[]}))
    payload = {"catalog_path": str(catalog)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_catalog_list() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["person_count"] == 0

def test_person_create(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[]}))
    payload = {"catalog_path": str(catalog), "name": "Test Person"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_person_create() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["name"] == "Test Person"

def test_person_rename(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[{"person_id":"person-test","name":"Old","aliases":[],"notes":"","embeddings":[]}]}))
    payload = {"catalog_path": str(catalog), "person_id": "person-test", "name": "New Name"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_person_rename() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["name"] == "New Name"

def test_person_reassign(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    source = tmp_path / "img.jpg"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[{"person_id":"person-a","name":"A","aliases":[],"notes":"","embeddings":[{"encoding":[0.1,0.2],"source_path":str(source),"box":None,"created_at_utc":None}]},{"person_id":"person-b","name":"B","aliases":[],"notes":"","embeddings":[]}]}))
    payload = {"catalog_path": str(catalog), "source_path": str(source), "face_index": 0, "from_person_id": "person-a", "to_person_id": "person-b"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_person_reassign() == 0


# ── cmd_face_ignore ──

def test_face_ignore_add(tmp_path: Path) -> None:
    payload = {"action": "add", "face_id": "img.jpg::0", "catalog_dir": str(tmp_path)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_face_ignore()
    assert exit_code in (None, 0)
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "face_ignore"
    assert output["action"] == "add"
    assert output["added"] is True


def test_face_ignore_add_duplicate(tmp_path: Path) -> None:
    payload = {"action": "add", "face_id": "dup.jpg::0", "catalog_dir": str(tmp_path)}
    # Add once
    fake_stdin = StringIO(json.dumps(payload))
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", StringIO()):
        assert cmd_face_ignore() in (None, 0)
    # Add again — should report not added
    fake_stdin2 = StringIO(json.dumps(payload))
    fake_stdout2 = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin2), mock.patch.object(sys, "stdout", fake_stdout2):
        assert cmd_face_ignore() in (None, 0)
    output2 = json.loads(fake_stdout2.getvalue())
    assert output2["added"] is False


def test_face_ignore_remove(tmp_path: Path) -> None:
    face_id = "rm.jpg::0"
    # Add first
    payload_add = {"action": "add", "face_id": face_id, "catalog_dir": str(tmp_path)}
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload_add))), mock.patch.object(sys, "stdout", StringIO()):
        assert cmd_face_ignore() in (None, 0)
    # Remove
    payload_rm = {"action": "remove", "face_id": face_id, "catalog_dir": str(tmp_path)}
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload_rm))), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_face_ignore() in (None, 0)
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "face_ignore"
    assert output["removed"] is True


def test_face_ignore_remove_nonexistent(tmp_path: Path) -> None:
    payload = {"action": "remove", "face_id": "never_added::0", "catalog_dir": str(tmp_path)}
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_face_ignore() in (None, 0)
    output = json.loads(fake_stdout.getvalue())
    assert output["removed"] is False


def test_face_ignore_list(tmp_path: Path) -> None:
    # Add two faces then list
    for fid in ("a::0", "b::1"):
        with mock.patch.object(sys, "stdin", StringIO(json.dumps({"action": "add", "face_id": fid, "catalog_dir": str(tmp_path)}))), mock.patch.object(sys, "stdout", StringIO()):
            cmd_face_ignore()
    fake_stdout = StringIO()
    payload = {"action": "list", "face_id": "ignored", "catalog_dir": str(tmp_path)}
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_face_ignore() in (None, 0)
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "face_ignore_list"
    assert output["count"] == 2
    assert set(output["ignored_faces"]) == {"a::0", "b::1"}


def test_face_ignore_missing_face_id(tmp_path: Path) -> None:
    payload = {"action": "add", "catalog_dir": str(tmp_path)}
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_face_ignore()
    assert exit_code == 1
    assert "face_id" in fake_stderr.getvalue()


def test_face_ignore_nonexistent_catalog_dir() -> None:
    payload = {"action": "add", "face_id": "f::0", "catalog_dir": "/nonexistent/path"}
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_face_ignore()
    assert exit_code == 1
    assert "not found" in fake_stderr.getvalue()


def test_face_ignore_unknown_action(tmp_path: Path) -> None:
    payload = {"action": "invalid_op", "face_id": "f::0", "catalog_dir": str(tmp_path)}
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_face_ignore()
    assert exit_code == 1
    assert "Unknown action" in fake_stderr.getvalue()


def test_face_ignore_invalid_json() -> None:
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO("broken json")), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_face_ignore()
    assert exit_code == 1
    assert "Invalid JSON" in fake_stderr.getvalue()


# ── cmd_person_merge ──

def test_person_merge_success(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({
        "schema_version": 1,
        "persons": [
            {"person_id": "p1", "name": "Alice", "aliases": ["Ally"], "notes": "", "embeddings": [{"encoding": [1.0], "source_path": "a.jpg", "box": None, "created_at_utc": None}]},
            {"person_id": "p2", "name": "Bob", "aliases": [], "notes": "", "embeddings": [{"encoding": [2.0], "source_path": "b.jpg", "box": None, "created_at_utc": None}]},
        ]
    }))
    payload = {"catalog_path": str(catalog), "from_person_id": "p1", "to_person_id": "p2"}
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_person_merge()
    assert exit_code in (None, 0)
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "person_merged"
    assert output["from_person_id"] == "p1"
    assert output["to_person_id"] == "p2"
    assert output["merged_embeddings"] == 1
    assert output["new_face_count"] == 2


def test_person_merge_missing_ids(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "persons": []}))
    payload = {"catalog_path": str(catalog)}
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_person_merge()
    assert exit_code == 1
    assert "from_person_id" in fake_stderr.getvalue()


def test_person_merge_same_id_rejected(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "persons": [{"person_id": "p1", "name": "X", "aliases": [], "notes": "", "embeddings": []}]}))
    payload = {"catalog_path": str(catalog), "from_person_id": "p1", "to_person_id": "p1"}
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_person_merge()
    assert exit_code == 1
    assert "Cannot merge" in fake_stderr.getvalue()


def test_person_merge_source_not_found(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "persons": [{"person_id": "p2", "name": "B", "aliases": [], "notes": "", "embeddings": []}]}))
    payload = {"catalog_path": str(catalog), "from_person_id": "ghost", "to_person_id": "p2"}
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_person_merge()
    assert exit_code == 1
    assert "not found" in fake_stderr.getvalue()


def test_person_merge_target_not_found(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "persons": [{"person_id": "p1", "name": "A", "aliases": [], "notes": "", "embeddings": []}]}))
    payload = {"catalog_path": str(catalog), "from_person_id": "p1", "to_person_id": "ghost"}
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_person_merge()
    assert exit_code == 1
    assert "not found" in fake_stderr.getvalue()


def test_person_merge_invalid_json() -> None:
    fake_stderr = StringIO()
    with mock.patch.object(sys, "stdin", StringIO("bad")), mock.patch.object(sys, "stderr", fake_stderr):
        exit_code = cmd_person_merge()
    assert exit_code == 1
    assert "Invalid JSON" in fake_stderr.getvalue()
