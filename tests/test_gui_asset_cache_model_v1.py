from media_manager.core.gui_asset_cache_model import build_asset_cache_key, build_asset_cache_manifest, prune_asset_cache_manifest


def test_asset_cache_manifest_marks_sensitive_faces(tmp_path) -> None:
    manifest = build_asset_cache_manifest([
        {"path": "a.jpg", "role": "face_crop"},
        {"path": "b.jpg", "role": "preview"},
    ], cache_dir=tmp_path)

    assert manifest["entry_count"] == 2
    assert manifest["sensitive_count"] == 1
    assert manifest["entries"][0]["cache_key"] == build_asset_cache_key("a.jpg", role="face_crop", size=256)


def test_asset_cache_prune_plan() -> None:
    manifest = {"entries": [{"cache_key": "a"}, {"cache_key": "b"}, {"cache_key": "c"}]}
    plan = prune_asset_cache_manifest(manifest, keep_limit=2)

    assert plan["kept_count"] == 2
    assert plan["removed_count"] == 1
