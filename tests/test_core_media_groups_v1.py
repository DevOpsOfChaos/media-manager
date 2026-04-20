from __future__ import annotations

from pathlib import Path

from media_manager.core.media_groups import (
    build_media_group_index,
    build_media_groups,
    find_group_for_path,
    summarize_media_groups,
)
from media_manager.core.scanner.models import ScannedFile


def _scanned(source_root: Path, relative_path: str, *, size_bytes: int = 1) -> ScannedFile:
    relative = Path(relative_path)
    return ScannedFile(
        source_root=source_root,
        path=source_root / relative,
        relative_path=relative,
        extension=(source_root / relative).suffix.lower(),
        size_bytes=size_bytes,
    )


def test_single_jpg_returns_single_group(tmp_path: Path) -> None:
    source = tmp_path / "source"
    item = _scanned(source, "IMG_0001.jpg")

    groups = build_media_groups([item])

    assert len(groups) == 1
    assert groups[0].group_kind == "single"
    assert groups[0].main_path == item.path
    assert groups[0].associated_paths == ()


def test_jpg_and_xmp_return_sidecar_group(tmp_path: Path) -> None:
    source = tmp_path / "source"
    jpg = _scanned(source, "IMG_0001.jpg")
    xmp = _scanned(source, "IMG_0001.xmp")

    groups = build_media_groups([jpg, xmp])

    assert len(groups) == 1
    assert groups[0].group_kind == "sidecar"
    assert groups[0].main_path == jpg.path
    assert groups[0].associated_paths == (xmp.path,)


def test_heic_and_aae_return_sidecar_group(tmp_path: Path) -> None:
    source = tmp_path / "source"
    heic = _scanned(source, "IMG_0001.heic")
    aae = _scanned(source, "IMG_0001.aae")

    groups = build_media_groups([heic, aae])

    assert len(groups) == 1
    assert groups[0].group_kind == "sidecar"
    assert groups[0].main_path == heic.path
    assert groups[0].associated_paths == (aae.path,)


def test_cr3_and_jpg_return_raw_jpeg_pair_with_raw_main(tmp_path: Path) -> None:
    source = tmp_path / "source"
    raw = _scanned(source, "IMG_0001.cr3")
    jpg = _scanned(source, "IMG_0001.jpg")

    groups = build_media_groups([jpg, raw])

    assert len(groups) == 1
    assert groups[0].group_kind == "raw_jpeg_pair"
    assert groups[0].main_path == raw.path
    assert groups[0].associated_paths == (jpg.path,)


def test_jpg_and_mov_return_photo_video_pair_with_image_main(tmp_path: Path) -> None:
    source = tmp_path / "source"
    jpg = _scanned(source, "IMG_0001.jpg")
    mov = _scanned(source, "IMG_0001.mov")

    groups = build_media_groups([mov, jpg])

    assert len(groups) == 1
    assert groups[0].group_kind == "photo_video_pair"
    assert groups[0].main_path == jpg.path
    assert groups[0].associated_paths == (mov.path,)


def test_jpg_xmp_and_mov_return_mixed_group(tmp_path: Path) -> None:
    source = tmp_path / "source"
    jpg = _scanned(source, "IMG_0001.jpg")
    xmp = _scanned(source, "IMG_0001.xmp")
    mov = _scanned(source, "IMG_0001.mov")

    groups = build_media_groups([jpg, xmp, mov])

    assert len(groups) == 1
    assert groups[0].group_kind == "mixed"
    assert groups[0].main_path == jpg.path
    assert groups[0].associated_file_count == 2


def test_ambiguous_video_candidates_produce_warnings_and_safe_singles(tmp_path: Path) -> None:
    source = tmp_path / "source"
    jpg = _scanned(source, "IMG_0001.jpg")
    mov = _scanned(source, "IMG_0001.mov")
    mp4 = _scanned(source, "IMG_0001.mp4")

    groups = build_media_groups([jpg, mov, mp4])

    assert len(groups) == 3
    assert all(item.group_kind == "single" for item in groups)
    assert all(item.association_warnings for item in groups)
    assert any(w.warning_code == "ambiguous_photo_video_pair" for item in groups for w in item.association_warnings)


def test_summary_counts_match_expected_totals(tmp_path: Path) -> None:
    source = tmp_path / "source"
    groups = build_media_groups(
        [
            _scanned(source, "IMG_0001.jpg"),
            _scanned(source, "IMG_0001.xmp"),
            _scanned(source, "IMG_0002.cr3"),
            _scanned(source, "IMG_0002.jpg"),
            _scanned(source, "IMG_0003.jpg"),
        ]
    )

    summary = summarize_media_groups(groups)

    assert summary.group_count == 3
    assert summary.single_file_count == 1
    assert summary.associated_file_count == 2
    assert summary.group_kind_summary == {"raw_jpeg_pair": 1, "sidecar": 1, "single": 1}


def test_group_index_resolves_all_member_paths_to_same_group(tmp_path: Path) -> None:
    source = tmp_path / "source"
    jpg = _scanned(source, "IMG_0001.jpg")
    xmp = _scanned(source, "IMG_0001.xmp")

    groups = build_media_groups([jpg, xmp])
    group = groups[0]
    index = build_media_group_index(groups)

    assert index[jpg.path] is group
    assert index[xmp.path] is group
    assert find_group_for_path(groups, jpg.path) is group
    assert find_group_for_path(groups, xmp.path) is group
