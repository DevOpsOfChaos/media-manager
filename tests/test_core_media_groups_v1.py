from __future__ import annotations

from pathlib import Path

from media_manager.core.media_groups import (
    build_media_group_index,
    build_media_groups,
    find_group_for_path,
    summarize_media_groups,
)
from media_manager.core.scanner.models import ScannedFile


def _scanned(source_root: str, relative_path: str, *, size_bytes: int = 1) -> ScannedFile:
    source = Path(source_root)
    rel = Path(relative_path)
    return ScannedFile(
        source_root=source,
        path=source / rel,
        relative_path=rel,
        extension=(source / rel).suffix.lower(),
        size_bytes=size_bytes,
    )


def test_single_jpg_returns_single_group() -> None:
    groups = build_media_groups([_scanned("C:/Photos", "IMG_0001.jpg")])

    assert len(groups) == 1
    assert groups[0].group_kind == "single"
    assert groups[0].main_path.name == "IMG_0001.jpg"
    assert groups[0].associated_file_count == 0


def test_jpg_plus_xmp_returns_sidecar_group() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_0001.jpg"),
        _scanned("C:/Photos", "IMG_0001.xmp"),
    ])

    assert len(groups) == 1
    assert groups[0].group_kind == "sidecar"
    assert groups[0].main_path.name == "IMG_0001.jpg"
    assert [item.name for item in groups[0].associated_paths] == ["IMG_0001.xmp"]


def test_heic_plus_aae_returns_sidecar_group() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_0002.heic"),
        _scanned("C:/Photos", "IMG_0002.aae"),
    ])

    assert len(groups) == 1
    assert groups[0].group_kind == "sidecar"
    assert groups[0].main_path.name == "IMG_0002.heic"
    assert [item.name for item in groups[0].associated_paths] == ["IMG_0002.aae"]


def test_cr3_plus_jpg_returns_raw_jpeg_pair_with_raw_as_main() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_1001.cr3"),
        _scanned("C:/Photos", "IMG_1001.jpg"),
    ])

    assert len(groups) == 1
    assert groups[0].group_kind == "raw_jpeg_pair"
    assert groups[0].main_path.name == "IMG_1001.cr3"
    assert [item.name for item in groups[0].associated_paths] == ["IMG_1001.jpg"]


def test_jpg_plus_mov_returns_photo_video_pair_with_jpg_as_main() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_2001.jpg"),
        _scanned("C:/Photos", "IMG_2001.mov"),
    ])

    assert len(groups) == 1
    assert groups[0].group_kind == "photo_video_pair"
    assert groups[0].main_path.name == "IMG_2001.jpg"
    assert [item.name for item in groups[0].associated_paths] == ["IMG_2001.mov"]


def test_jpg_plus_xmp_plus_mov_returns_mixed_group() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_3001.jpg"),
        _scanned("C:/Photos", "IMG_3001.xmp"),
        _scanned("C:/Photos", "IMG_3001.mov"),
    ])

    assert len(groups) == 1
    assert groups[0].group_kind == "mixed"
    assert groups[0].main_path.name == "IMG_3001.jpg"
    assert sorted(item.name for item in groups[0].associated_paths) == ["IMG_3001.mov", "IMG_3001.xmp"]


def test_ambiguous_video_pair_produces_warnings_and_leaves_videos_single() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_4001.jpg"),
        _scanned("C:/Photos", "IMG_4001.mov"),
        _scanned("C:/Photos", "IMG_4001.mp4"),
    ])

    assert len(groups) == 3
    jpg_group = next(item for item in groups if item.main_path.name == "IMG_4001.jpg")
    assert jpg_group.group_kind == "single"
    assert len(jpg_group.association_warnings) >= 1
    video_singles = [item for item in groups if item.main_path.suffix.lower() in {".mov", ".mp4"}]
    assert len(video_singles) == 2
    assert any(item.association_warnings for item in video_singles)


def test_summary_counts_match_expected_totals() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_0001.jpg"),
        _scanned("C:/Photos", "IMG_0001.xmp"),
        _scanned("C:/Photos", "IMG_0002.cr3"),
        _scanned("C:/Photos", "IMG_0002.jpg"),
        _scanned("C:/Photos", "IMG_0003.jpg"),
    ])

    summary = summarize_media_groups(groups)

    assert summary.group_count == 3
    assert summary.single_file_count == 1
    assert summary.associated_file_count == 2
    assert summary.group_kind_summary == {"raw_jpeg_pair": 1, "sidecar": 1, "single": 1}


def test_group_index_and_lookup_resolve_all_member_paths() -> None:
    groups = build_media_groups([
        _scanned("C:/Photos", "IMG_9001.jpg"),
        _scanned("C:/Photos", "IMG_9001.mov"),
        _scanned("C:/Photos", "IMG_9001.xmp"),
    ])

    group = groups[0]
    index = build_media_group_index(groups)

    for member in group.members:
        assert index[member.path].group_id == group.group_id
        assert find_group_for_path(groups, member.path).group_id == group.group_id
