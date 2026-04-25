from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.duplicate_report import build_duplicate_review_export, build_duplicate_summary
from media_manager.duplicate_workflow import build_duplicate_workflow_bundle
from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates
from media_manager.media_formats import get_media_format_capability, summarize_supported_media_formats


def test_media_format_catalog_includes_common_video_and_raw_extensions() -> None:
    for extension in [".mp4", ".mov", ".mkv", ".webm", ".mts", ".m2ts", ".ts", ".mxf", ".vob"]:
        capability = get_media_format_capability(extension)
        assert capability is not None
        assert capability.media_kind == "video"
        assert capability.exact_duplicates is True

    for extension in [".dng", ".arw", ".cr3", ".nef", ".raf", ".pef", ".srw"]:
        capability = get_media_format_capability(extension)
        assert capability is not None
        assert capability.media_kind == "raw-image"
        assert capability.exact_duplicates is True

    summary = summarize_supported_media_formats()
    assert summary["media_kind_summary"]["video"] >= 30
    assert summary["media_kind_summary"]["raw-image"] >= 20
    assert summary["media_kind_summary"]["audio"] >= 15


def test_exact_duplicate_scan_reports_video_and_extension_summaries(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    payload = b"video duplicate payload"
    (source / "clip-a.mp4").write_bytes(payload)
    (source / "clip-b.mov").write_bytes(payload)
    (source / "photo-a.jpg").write_bytes(b"image duplicate")
    (source / "photo-b.jpeg").write_bytes(b"image duplicate")

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))

    assert result.scanned_files == 4
    assert result.video_file_count == 2
    assert result.image_file_count == 2
    assert result.media_kind_summary == {"image": 2, "video": 2}
    assert result.extension_summary[".mp4"] == 1
    assert result.extension_summary[".mov"] == 1
    assert len(result.exact_groups) == 2
    video_groups = [group for group in result.exact_groups if group.media_kind_summary.get("video") == 2]
    assert len(video_groups) == 1
    assert video_groups[0].extension_summary == {".mov": 1, ".mp4": 1}


def test_exact_duplicate_scan_can_restrict_to_video_kind(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "clip-a.mp4").write_bytes(b"same")
    (source / "clip-b.mov").write_bytes(b"same")
    (source / "photo-a.jpg").write_bytes(b"same")
    (source / "photo-b.jpeg").write_bytes(b"same")

    result = scan_exact_duplicates(
        DuplicateScanConfig(
            source_dirs=[source],
            media_extensions=frozenset({".mp4", ".mov"}),
        )
    )

    assert result.scanned_files == 2
    assert result.video_file_count == 2
    assert result.image_file_count == 0
    assert len(result.exact_groups) == 1
    assert result.exact_groups[0].media_kind_summary == {"video": 2}


def test_duplicate_review_export_marks_video_groups_for_review(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "clip-a.mp4").write_bytes(b"same video")
    (source / "clip-b.mov").write_bytes(b"same video")

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))
    bundle = build_duplicate_workflow_bundle(result.exact_groups, {}, "copy")
    review = build_duplicate_review_export(scan_result=result, bundle=bundle)

    assert review["reason_summary"]["video_duplicate_group"] == 1
    assert review["reason_summary"]["mixed_extensions"] == 1
    candidate = review["candidates"][0]
    assert candidate["media_kind_summary"] == {"video": 2}
    assert candidate["extension_summary"] == {".mov": 1, ".mp4": 1}
