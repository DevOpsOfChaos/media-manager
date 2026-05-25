from __future__ import annotations
import json, sys
from io import StringIO
from pathlib import Path
from unittest import mock
from media_manager.bridge_people import cmd_catalog_list, cmd_person_create, cmd_person_rename, cmd_person_reassign

def test_catalog_list_valid(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[]}))
    payload = {"catalog_path": str(catalog)}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_catalog_list() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["person_count"] == 0

def test_person_create(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[]}))
    payload = {"catalog_path": str(catalog), "name": "Test Person"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_person_create() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["name"] == "Test Person"

def test_person_rename(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[{"person_id":"person-test","name":"Old","aliases":[],"notes":"","embeddings":[]}]}))
    payload = {"catalog_path": str(catalog), "person_id": "person-test", "name": "New Name"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_person_rename() == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["name"] == "New Name"

def test_person_reassign(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    source = tmp_path / "img.jpg"
    catalog.write_text(json.dumps({"schema_version":1,"persons":[{"person_id":"person-a","name":"A","aliases":[],"notes":"","embeddings":[{"encoding":[0.1,0.2],"source_path":str(source),"box":None,"created_at_utc":None}]},{"person_id":"person-b","name":"B","aliases":[],"notes":"","embeddings":[]}]}))
    payload = {"catalog_path": str(catalog), "source_path": str(source), "face_index": 0, "from_person_id": "person-a", "to_person_id": "person-b"}
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        assert cmd_person_reassign() == 0
