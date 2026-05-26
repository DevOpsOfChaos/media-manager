from __future__ import annotations

import json
import os
from pathlib import Path

from media_manager.core.people_recognition import (
    _load_face_process_cache,
    _save_face_process_cache,
)


class TestFaceProcessCacheLoad:
    def test_load_empty_when_no_file(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "nonexistent.json"
        result = _load_face_process_cache(cache_path)
        assert result == {}

    def test_load_valid_cache(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.json"
        data = {
            "C:\\photos\\a.jpg": {"mtime": 1234567890.0, "faces": [[{"top": 0, "right": 100, "bottom": 100, "left": 0}, [0.1, 0.2, 0.3]]]},
            "C:\\photos\\b.jpg": {"mtime": 1234567891.0, "faces": []},
        }
        cache_path.write_text(json.dumps(data), encoding="utf-8")

        result = _load_face_process_cache(cache_path)
        assert len(result) == 2
        assert result["C:\\photos\\a.jpg"]["mtime"] == 1234567890.0
        assert len(result["C:\\photos\\a.jpg"]["faces"]) == 1
        assert result["C:\\photos\\b.jpg"]["mtime"] == 1234567891.0

    def test_load_legacy_numeric_mtime(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "legacy.json"
        data = {"C:\\img.jpg": 1234567890.0}
        cache_path.write_text(json.dumps(data), encoding="utf-8")

        result = _load_face_process_cache(cache_path)
        assert result["C:\\img.jpg"]["mtime"] == 1234567890.0
        assert result["C:\\img.jpg"]["faces"] == []

    def test_load_corrupted_file_returns_empty(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "bad.json"
        cache_path.write_text("not valid json", encoding="utf-8")

        result = _load_face_process_cache(cache_path)
        assert result == {}

    def test_load_ignores_non_dict_entries(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "mixed.json"
        data = {
            "C:\\ok.jpg": {"mtime": 100.0, "faces": []},
            "C:\\list.jpg": [1, 2, 3],
        }
        cache_path.write_text(json.dumps(data), encoding="utf-8")

        result = _load_face_process_cache(cache_path)
        assert "C:\\ok.jpg" in result
        assert "C:\\list.jpg" not in result
        assert len(result) == 1


class TestFaceProcessCacheSave:
    def test_save_and_reload_roundtrip(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.json"
        cache = {
            "C:\\pics\\x.jpg": {
                "mtime": 1234567890.0,
                "faces": [[{"top": 10, "right": 200, "bottom": 210, "left": 10}, [0.5, 0.6, 0.7]]],
            },
        }
        _save_face_process_cache(cache_path, cache)
        assert cache_path.exists()

        reloaded = _load_face_process_cache(cache_path)
        assert reloaded["C:\\pics\\x.jpg"]["mtime"] == 1234567890.0
        assert len(reloaded["C:\\pics\\x.jpg"]["faces"]) == 1

    def test_save_creates_parent_directory(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "subdir" / "nested" / "cache.json"
        cache = {"key": {"mtime": 1.0, "faces": []}}
        _save_face_process_cache(cache_path, cache)
        assert cache_path.exists()

    def test_save_empty_cache(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "empty.json"
        _save_face_process_cache(cache_path, {})
        assert cache_path.exists()
        assert json.loads(cache_path.read_text()) == {}


class TestFaceCacheRematch:
    def test_cache_mtime_check_within_tolerance(self, tmp_path: Path) -> None:
        f = tmp_path / "photo.jpg"
        f.write_bytes(b"jpg")
        mtime = f.stat().st_mtime

        cache_path = tmp_path / "fcache.json"
        norm_key = os.path.normcase(str(f))
        cache = {norm_key: {"mtime": mtime, "faces": []}}
        _save_face_process_cache(cache_path, cache)

        reloaded = _load_face_process_cache(cache_path)
        cached_mtime = reloaded[norm_key]["mtime"]
        assert abs(mtime - cached_mtime) < 1.0

    def test_cache_mtime_stale_detection(self, tmp_path: Path) -> None:
        f = tmp_path / "stale.jpg"
        f.write_bytes(b"jpg")
        mtime = f.stat().st_mtime

        cache_path = tmp_path / "fcache_stale.json"
        norm_key = os.path.normcase(str(f))
        cache = {norm_key: {"mtime": mtime - 10.0, "faces": []}}
        _save_face_process_cache(cache_path, cache)

        reloaded = _load_face_process_cache(cache_path)
        cached_mtime = reloaded[norm_key]["mtime"]
        assert abs(mtime - cached_mtime) >= 1.0
