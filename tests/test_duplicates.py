from pathlib import Path

from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates


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
