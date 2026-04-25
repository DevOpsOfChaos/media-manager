from __future__ import annotations

import json
from pathlib import Path

import pytest

from media_manager.cli_people import main as people_main
from media_manager.core.people_recognition import (
    PeopleCatalog,
    PeopleScanConfig,
    add_embedding_to_person,
    add_person_to_catalog,
    build_people_review_payload,
    inspect_people_backend,
    load_people_catalog,
    rename_person_in_catalog,
    scan_people,
    write_people_catalog,
)


def test_people_catalog_round_trip_and_rename(tmp_path: Path) -> None:
    catalog_path = tmp_path / "people.json"
    catalog = PeopleCatalog()
    person = add_person_to_catalog(catalog, name="Jane Doe", aliases=["Janie"])
    add_embedding_to_person(catalog, person_id=person.person_id, encoding=[0.1, 0.2, 0.3], source_path="a.jpg")
    write_people_catalog(catalog_path, catalog)

    loaded = load_people_catalog(catalog_path)
    assert list(loaded.persons) == [person.person_id]
    assert loaded.persons[person.person_id].name == "Jane Doe"
    assert loaded.persons[person.person_id].aliases == ["Janie"]
    assert loaded.persons[person.person_id].embeddings[0].encoding == pytest.approx((0.1, 0.2, 0.3))

    renamed = rename_person_in_catalog(loaded, person_id=person.person_id, name="Jane Example")
    assert renamed.name == "Jane Example"


def test_people_scan_without_backend_is_safe(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"not really an image")

    monkeypatch.setattr("media_manager.core.people_recognition._load_backend", lambda: None)
    monkeypatch.setattr("media_manager.core.people_recognition._load_opencv_backend", lambda: None)
    result = scan_people(PeopleScanConfig(source_dirs=[source]))

    assert result.status == "backend_missing"
    assert result.backend_available is False
    assert result.scanned_files == 1
    assert result.face_count == 0


def test_people_backend_auto_can_fallback_to_opencv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("media_manager.core.people_recognition._load_backend", lambda: None)
    monkeypatch.setattr("media_manager.core.people_recognition._load_opencv_backend", lambda: {"cv2": object(), "classifier": object()})

    status = inspect_people_backend("auto")

    assert status.available is True
    assert status.selected_backend == "opencv"
    assert status.detection_available is True
    assert status.matching_available is False


def test_people_review_payload_lists_unknown_faces() -> None:
    scan_payload = {
        "detections": [
            {"path": "a.jpg", "face_index": 0, "box": {"top": 1}, "matched_person_id": None, "unknown_cluster_id": "unknown-1"},
            {"path": "b.jpg", "face_index": 0, "box": {"top": 2}, "matched_person_id": "person-jane", "unknown_cluster_id": None},
        ]
    }

    review = build_people_review_payload(scan_payload)

    assert review["candidate_count"] == 1
    assert review["reason_summary"] == {"unknown_face": 1}
    assert review["candidates"][0]["path"] == "a.jpg"


def test_people_cli_catalog_commands(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    catalog_path = tmp_path / "people.json"

    assert people_main(["catalog-init", "--catalog", str(catalog_path)]) == 0
    assert catalog_path.exists()
    capsys.readouterr()

    assert people_main(["person-add", "--catalog", str(catalog_path), "--name", "Jane Doe", "--json"]) == 0
    add_output = json.loads(capsys.readouterr().out)
    person_id = add_output["person"]["person_id"]
    assert person_id.startswith("person-jane-doe")

    assert people_main(["person-rename", "--catalog", str(catalog_path), "--person-id", person_id, "--name", "Jane Example"]) == 0
    capsys.readouterr()
    assert people_main(["catalog-list", "--catalog", str(catalog_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["person_count"] == 1
    assert payload["persons"][0]["name"] == "Jane Example"


def test_people_cli_backend_json_reports_capabilities(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("media_manager.core.people_recognition._load_backend", lambda: None)
    monkeypatch.setattr("media_manager.core.people_recognition._load_opencv_backend", lambda: {"cv2": object(), "classifier": object()})

    assert people_main(["backend", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["selected_backend"] == "opencv"
    assert payload["capabilities"]["face_detection"] is True
    assert payload["capabilities"]["named_person_matching"] is False
