from __future__ import annotations

from pathlib import Path

from media_manager.associated_files import (
    associated_key_for_path,
    build_associated_file_map,
    classify_associated_path,
    group_associated_files,
)


def test_associated_key_for_path_is_case_insensitive() -> None:
    assert associated_key_for_path(Path("IMG_0001.JPG")) == "img_0001"
    assert associated_key_for_path(Path("img_0001.xmp")) == "img_0001"


def test_classify_associated_path_recognizes_primary_sidecar_and_other() -> None:
    assert classify_associated_path(Path("IMG_0001.CR3")) == "primary"
    assert classify_associated_path(Path("IMG_0001.XMP")) == "sidecar"
    assert classify_associated_path(Path("IMG_0001.txt")) == "other"


def test_group_associated_files_groups_raw_jpeg_and_xmp() -> None:
    paths = [
        Path("/library/IMG_0001.CR3"),
        Path("/library/IMG_0001.JPG"),
        Path("/library/IMG_0001.XMP"),
        Path("/library/IMG_0002.JPG"),
    ]

    groups = group_associated_files(paths)

    assert len(groups) == 1
    group = groups[0]
    assert [path.name for path in group.primaries] == ["IMG_0001.CR3", "IMG_0001.JPG"]
    assert [path.name for path in group.sidecars] == ["IMG_0001.XMP"]
    assert group.others == []


def test_group_associated_files_groups_video_with_srt_thm_and_lrv() -> None:
    paths = [
        Path("/clips/CLIP_9001.MP4"),
        Path("/clips/CLIP_9001.SRT"),
        Path("/clips/CLIP_9001.THM"),
        Path("/clips/CLIP_9001.LRV"),
    ]

    groups = group_associated_files(paths)

    assert len(groups) == 1
    group = groups[0]
    assert [path.name for path in group.primaries] == ["CLIP_9001.MP4"]
    assert [path.name for path in group.sidecars] == ["CLIP_9001.LRV", "CLIP_9001.SRT", "CLIP_9001.THM"]


def test_group_associated_files_requires_at_least_one_primary() -> None:
    paths = [
        Path("/library/IMG_0001.XMP"),
        Path("/library/IMG_0001.AAE"),
    ]

    groups = group_associated_files(paths)

    assert groups == []


def test_build_associated_file_map_returns_peer_relationships() -> None:
    paths = [
        Path("/library/IMG_0001.CR3"),
        Path("/library/IMG_0001.JPG"),
        Path("/library/IMG_0001.XMP"),
    ]

    relation_map = build_associated_file_map(paths)

    expected_map = {
        str(paths[0]): sorted([str(paths[1]), str(paths[2])]),
        str(paths[2]): sorted([str(paths[0]), str(paths[1])]),
    }

    assert sorted(relation_map[str(paths[0])]) == expected_map[str(paths[0])]
    assert sorted(relation_map[str(paths[2])]) == expected_map[str(paths[2])]
