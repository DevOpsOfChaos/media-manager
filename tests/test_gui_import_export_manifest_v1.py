from pathlib import Path

from media_manager.core.gui_import_export_manifest import build_export_manifest, build_import_manifest


def test_export_manifest_marks_people_files_sensitive(tmp_path: Path) -> None:
    catalog = tmp_path / "people.json"
    manifest = build_export_manifest(export_id="x", files=[{"path": catalog, "role": "people_catalog"}])

    assert manifest["sensitive_file_count"] == 1
    assert manifest["safe_to_share"] is False


def test_import_manifest_checks_existence(tmp_path: Path) -> None:
    path = tmp_path / "bundle.json"
    path.write_text("{}", encoding="utf-8")

    manifest = build_import_manifest(source_path=path, expected_kind="people_bundle")

    assert manifest["exists"] is True
    assert manifest["can_import"] is True
