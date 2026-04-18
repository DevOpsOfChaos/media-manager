from pathlib import Path

from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates


def test_scan_exact_duplicates_continues_after_unreadable_file_size(monkeypatch, tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    source_a.mkdir()
    source_b.mkdir()

    duplicate_a = source_a / "one.jpg"
    duplicate_b = source_b / "two.jpg"
    broken = source_b / "broken.jpg"
    duplicate_a.write_bytes(b"duplicate-bytes")
    duplicate_b.write_bytes(b"duplicate-bytes")
    broken.write_bytes(b"broken")

    original_safe_file_size = __import__("media_manager.duplicates", fromlist=["_safe_file_size"])._safe_file_size

    def fake_safe_file_size(path: Path) -> int | None:
        if path == broken:
            return None
        return original_safe_file_size(path)

    monkeypatch.setattr("media_manager.duplicates._safe_file_size", fake_safe_file_size)

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source_a, source_b]))

    assert result.scanned_files == 3
    assert result.size_group_errors == 1
    assert result.errors == 1
    assert len(result.exact_groups) == 1
    assert sorted(path.name for path in result.exact_groups[0].files) == ["one.jpg", "two.jpg"]



def test_scan_exact_duplicates_reports_sample_stage_errors(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "first.jpg"
    second = source / "second.jpg"
    first.write_bytes(b"duplicate-bytes")
    second.write_bytes(b"duplicate-bytes")

    original_compute_sample_fingerprint = __import__("media_manager.duplicates", fromlist=["compute_sample_fingerprint"]).compute_sample_fingerprint

    def fake_compute_sample_fingerprint(path: Path, sample_size: int = 64 * 1024) -> str:
        if path == second:
            raise OSError("sample failed")
        return original_compute_sample_fingerprint(path, sample_size=sample_size)

    monkeypatch.setattr("media_manager.duplicates.compute_sample_fingerprint", fake_compute_sample_fingerprint)

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))

    assert result.sample_errors == 1
    assert result.errors == 1
    assert result.exact_groups == []



def test_scan_exact_duplicates_reports_hash_stage_errors(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "first.jpg"
    second = source / "second.jpg"
    first.write_bytes(b"duplicate-bytes")
    second.write_bytes(b"duplicate-bytes")

    original_compute_full_hash = __import__("media_manager.duplicates", fromlist=["compute_full_hash"]).compute_full_hash

    def fake_compute_full_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
        if path == second:
            raise OSError("hash failed")
        return original_compute_full_hash(path, chunk_size=chunk_size)

    monkeypatch.setattr("media_manager.duplicates.compute_full_hash", fake_compute_full_hash)

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))

    assert result.hash_errors == 1
    assert result.errors == 1
    assert result.exact_groups == []



def test_scan_exact_duplicates_reports_compare_stage_errors(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "first.jpg"
    second = source / "second.jpg"
    first.write_bytes(b"duplicate-bytes")
    second.write_bytes(b"duplicate-bytes")

    def fake_files_are_identical(first_path: Path, second_path: Path, chunk_size: int = 1024 * 1024) -> bool:
        raise OSError("compare failed")

    monkeypatch.setattr("media_manager.duplicates.files_are_identical", fake_files_are_identical)

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))

    assert result.compare_errors == 1
    assert result.errors == 1
    assert result.exact_groups == []
