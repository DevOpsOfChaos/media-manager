from __future__ import annotations

from pathlib import Path

from PIL import Image

from media_manager.similar_images import SimilarImageScanConfig, scan_similar_images


def test_scan_similar_images_reports_pair_counters_and_member_dimensions(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    first = source / "first.jpg"
    second = source / "second.jpg"
    image = Image.new("RGB", (80, 60), "white")
    image.save(first)
    image.save(second)

    result = scan_similar_images(SimilarImageScanConfig(source_dirs=[source], max_distance=0))

    assert result.image_files == 2
    assert result.hashed_files == 2
    assert result.candidate_pairs_checked == 1
    assert result.exact_hash_pairs == 1
    assert len(result.similar_groups) == 1
    member = result.similar_groups[0].members[0]
    assert member.width == 80
    assert member.height == 60


def test_scan_similar_images_counts_decode_errors_without_stopping_scan(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    good_a = source / "good_a.jpg"
    good_b = source / "good_b.jpg"
    broken = source / "broken.jpg"
    image = Image.new("RGB", (32, 32), "white")
    image.save(good_a)
    image.save(good_b)
    broken.write_bytes(b"not-a-real-image")

    result = scan_similar_images(SimilarImageScanConfig(source_dirs=[source], max_distance=0))

    assert result.image_files == 3
    assert result.hashed_files == 2
    assert result.decode_errors == 1
    assert result.errors == 1
    assert result.candidate_pairs_checked == 1
    assert len(result.similar_groups) == 1


def test_scan_similar_images_rejects_non_positive_hash_size(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    Image.new("RGB", (32, 32), "white").save(source / "photo.jpg")

    try:
        scan_similar_images(SimilarImageScanConfig(source_dirs=[source], hash_size=0))
    except ValueError as exc:
        assert "hash_size" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError for non-positive hash_size")
