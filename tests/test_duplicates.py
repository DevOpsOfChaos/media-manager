from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from media_manager.duplicates import (
    DuplicateScanConfig,
    _group_by_date,
    scan_exact_duplicates,
    scan_exact_duplicates_fast,
)


def test_scan_exact_duplicates_finds_identical_files_across_sources(tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    source_a.mkdir()
    source_b.mkdir()

    (source_a / "one.jpg").write_bytes(b"duplicate-bytes")
    (source_b / "two.jpg").write_bytes(b"duplicate-bytes")
    (source_b / "other.jpg").write_bytes(b"different-content")

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source_a, source_b]))

    assert result.scanned_files == 3
    assert len(result.exact_groups) == 1
    assert sorted(path.name for path in result.exact_groups[0].files) == ["one.jpg", "two.jpg"]
    assert result.exact_duplicate_files == 2
    assert result.exact_duplicates == 1


def test_scan_exact_duplicates_does_not_use_name_or_suffix_as_final_truth(tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    source_a.mkdir()
    source_b.mkdir()

    (source_a / "same-name.jpg").write_bytes(b"AAAA1111BBBB2222CCCC")
    (source_b / "same-name.jpg").write_bytes(b"AAAA2222BBBB1111CCCC")

    result = scan_exact_duplicates(
        DuplicateScanConfig(source_dirs=[source_a, source_b], sample_size=4, hash_chunk_size=4)
    )

    assert result.scanned_files == 2
    assert result.size_candidate_files == 2
    assert result.sampled_files == 2
    assert result.hashed_files == 2
    assert result.exact_groups == []


def test_scan_exact_duplicates_confirms_identical_bytes_even_with_different_suffixes(tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    source_a.mkdir()
    source_b.mkdir()

    (source_a / "clip.mov").write_bytes(b"same-video-bytes")
    (source_b / "clip.mp4").write_bytes(b"same-video-bytes")

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source_a, source_b]))

    assert len(result.exact_groups) == 1
    assert result.exact_groups[0].same_name is False
    assert result.exact_groups[0].same_suffix is False


def test_scan_exact_duplicates_supports_heic_bytes_even_without_image_decoder(tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    source_a.mkdir()
    source_b.mkdir()

    (source_a / "phone.heic").write_bytes(b"same-heic-bytes")
    (source_b / "copy.heic").write_bytes(b"same-heic-bytes")

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source_a, source_b]))

    assert result.scanned_files == 2
    assert len(result.exact_groups) == 1
    assert sorted(path.name for path in result.exact_groups[0].files) == ["copy.heic", "phone.heic"]


class TestDatePrefilter:
    def test_groups_by_mtime_when_no_exif(self, tmp_path: Path) -> None:
        """Files without EXIF metadata are grouped by mtime fallback."""
        dates = [
            "2024-01-15", "2024-03-22", "2024-06-10",
            "2024-09-01", "2024-12-25", "2023-05-10",
            "2023-08-20", "2022-01-01", "2021-11-11", "2020-07-04",
        ]
        base = datetime(2024, 1, 1, 12, 0, 0)
        paths: list[Path] = []
        for i in range(100):
            date_str = dates[i % 10]
            date_idx = i % 10
            f = tmp_path / f"IMG_{date_str.replace('-', '')}_{i:04d}.jpg"
            f.write_bytes(b"\xff\xd8" + os.urandom(512))
            dt = base + timedelta(days=date_idx * 30)
            ts = time.mktime(dt.timetuple())
            os.utime(str(f), (ts, ts))
            paths.append(f)

        date_groups = _group_by_date(paths)
        assert len(date_groups) >= 5, f"Expected >=5 date groups, got {len(date_groups)}"
        for dk, plist in date_groups.items():
            assert len(plist) > 1, f"Date group {dk} should have >1 file"
            assert dk != "unknown"

    def test_large_date_group_handled(self, tmp_path: Path) -> None:
        """Many files with same date+size are still processed, not discarded."""
        ts = time.mktime(datetime(2024, 7, 4, 12, 0, 0).timetuple())
        paths: list[Path] = []
        for i in range(300):
            f = tmp_path / f"burst_{i:04d}.jpg"
            f.write_bytes(os.urandom(256))
            os.utime(str(f), (ts, ts))
            paths.append(f)

        date_groups = _group_by_date(paths, date_prefilter_threshold=50)
        assert len(date_groups) == 1
        assert len(date_groups["2024-07-04"]) == 300

    def test_fast_scan_honors_use_date_prefilter(self, tmp_path: Path) -> None:
        """Fast scan skips date grouping when use_date_prefilter=False."""
        src = tmp_path / "photos"
        src.mkdir()
        ts_a = time.mktime(datetime(2024, 1, 15, 12, 0, 0).timetuple())
        ts_b = time.mktime(datetime(2024, 6, 10, 12, 0, 0).timetuple())
        (src / "a1.jpg").write_bytes(b"identical-content")
        os.utime(str(src / "a1.jpg"), (ts_a, ts_a))
        (src / "b1.jpg").write_bytes(b"identical-content")
        os.utime(str(src / "b1.jpg"), (ts_b, ts_b))
        (src / "a2.jpg").write_bytes(b"different-stuff")
        os.utime(str(src / "a2.jpg"), (ts_a, ts_a))

        config_disabled = DuplicateScanConfig(
            source_dirs=[src], use_date_prefilter=False, date_prefilter_threshold=50,
        )
        result_disabled = scan_exact_duplicates_fast(config_disabled)
        assert result_disabled.scanned_files == 3

        config_enabled = DuplicateScanConfig(
            source_dirs=[src], use_date_prefilter=True, date_prefilter_threshold=50,
        )
        result_enabled = scan_exact_duplicates_fast(config_enabled)
        assert result_enabled.scanned_files == 3

    def test_duplicate_scan_config_defaults(self) -> None:
        """DuplicateScanConfig defaults use_date_prefilter to True."""
        config = DuplicateScanConfig(source_dirs=[Path("/tmp")])
        assert config.use_date_prefilter is True
        assert config.date_prefilter_threshold == 50
