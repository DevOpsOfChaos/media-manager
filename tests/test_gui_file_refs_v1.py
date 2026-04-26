from __future__ import annotations

from pathlib import Path

from media_manager.core.gui_file_refs import build_asset_ref, build_local_file_ref, collect_asset_refs


def test_build_local_file_ref_marks_existing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "image.jpg"
    file_path.write_bytes(b"data")

    ref = build_local_file_ref(file_path, role="image", base_dir=tmp_path)

    assert ref["type"] == "local_path"
    assert ref["role"] == "image"
    assert ref["exists"] is True
    assert ref["is_file"] is True
    assert ref["relative_path"] == "image.jpg"
    assert isinstance(ref["uri"], str)


def test_collect_asset_refs_normalizes_people_assets(tmp_path: Path) -> None:
    crop = tmp_path / "assets" / "faces" / "face-1.jpg"
    crop.parent.mkdir(parents=True)
    crop.write_bytes(b"data")
    manifest = {
        "assets": [
            {
                "face_id": "face-1",
                "asset_path": str(crop),
                "path": "photos/a.jpg",
                "review_group_id": "unknown-1",
                "selected_name": "Jane",
                "include": True,
                "status": "ok",
            }
        ]
    }

    refs = collect_asset_refs(manifest, bundle_dir=tmp_path)

    assert len(refs) == 1
    assert refs[0]["face_id"] == "face-1"
    assert refs[0]["exists"] is True
    assert refs[0]["review_group_id"] == "unknown-1"
