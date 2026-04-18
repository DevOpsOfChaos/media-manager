from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from media_manager.similar_images import SimilarImageScanConfig, scan_similar_images


def _create_variant(path: Path, *, inverse: bool = False, shifted: bool = False) -> None:
    background = "white" if not inverse else "black"
    foreground = "black" if not inverse else "white"
    image = Image.new("RGB", (64, 64), background)
    draw = ImageDraw.Draw(image)
    left = 18 if shifted else 16
    top = 18 if shifted else 16
    draw.rectangle([left, top, left + 24, top + 24], fill=foreground)
    image.save(path)


def test_scan_similar_images_groups_visually_related_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    first = source / "first.jpg"
    second = source / "second.jpg"
    third = source / "third.jpg"
    _create_variant(first)
    _create_variant(second, shifted=True)
    _create_variant(third, inverse=True)

    result = scan_similar_images(SimilarImageScanConfig(source_dirs=[source], max_distance=10))

    assert result.scanned_files == 3
    assert result.image_files == 3
    assert result.hashed_files == 3
    assert len(result.similar_groups) == 1
    assert {member.path.name for member in result.similar_groups[0].members} == {"first.jpg", "second.jpg"}


def test_scan_similar_images_supports_jfif_as_common_jpeg_alias(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    first = source / "first.jfif"
    second = source / "second.jfif"

    image = Image.new("RGB", (64, 64), "white")
    image.save(first, format="JPEG")
    image.save(second, format="JPEG")

    result = scan_similar_images(SimilarImageScanConfig(source_dirs=[source], max_distance=0))

    assert result.scanned_files == 2
    assert result.image_files == 2
    assert result.hashed_files == 2
    assert len(result.similar_groups) == 1


def test_scan_similar_images_excludes_heic_from_similarity_stage_by_default(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    (source / "phone.heic").write_bytes(b"not-a-real-heic")
    image = Image.new("RGB", (64, 64), "white")
    image.save(source / "preview.jpg")

    result = scan_similar_images(SimilarImageScanConfig(source_dirs=[source], max_distance=0))

    assert result.scanned_files == 2
    assert result.image_files == 1
    assert result.hashed_files == 1
    assert result.errors == 0
