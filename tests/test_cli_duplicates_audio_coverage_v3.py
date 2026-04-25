from __future__ import annotations

import json
from pathlib import Path

import pytest

from media_manager.cli_duplicates import main
from media_manager.core.duplicate_report import build_duplicate_review_export
from media_manager.duplicate_workflow import build_duplicate_workflow_bundle
from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates
from media_manager.media_formats import get_media_format_capability, summarize_supported_media_formats


def test_media_format_catalog_includes_common_audio_extensions() -> None:
    for extension in [".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg", ".opus", ".wma"]:
        capability = get_media_format_capability(extension)
        assert capability is not None
        assert capability.media_kind == "audio"
        assert capability.exact_duplicates is True
        assert capability.similar_images is False

    summary = summarize_supported_media_formats()
    assert summary["media_kind_summary"]["audio"] >= 15


def test_exact_duplicate_scan_reports_audio_kind_and_review_reason(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "track-a.mp3").write_bytes(b"same audio")
    (source / "track-b.wav").write_bytes(b"same audio")
    (source / "clip-a.mp4").write_bytes(b"same video")
    (source / "clip-b.mov").write_bytes(b"same video")

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))

    assert result.scanned_files == 4
    assert result.audio_file_count == 2
    assert result.video_file_count == 2
    assert result.media_kind_summary == {"audio": 2, "video": 2}

    bundle = build_duplicate_workflow_bundle(result.exact_groups, {}, "copy")
    review = build_duplicate_review_export(scan_result=result, bundle=bundle)
    assert review["reason_summary"]["audio_duplicate_group"] == 1
    assert review["reason_summary"]["video_duplicate_group"] == 1


def test_cli_duplicates_can_restrict_to_audio_kind(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "track-a.mp3").write_bytes(b"same audio")
    (source / "track-b.wav").write_bytes(b"same audio")
    (source / "clip-a.mp4").write_bytes(b"same video")
    (source / "clip-b.mov").write_bytes(b"same video")
    report_path = tmp_path / "report.json"

    code = main([
        "--source", str(source),
        "--media-kind", "audio",
        "--report-json", str(report_path),
    ])

    assert code == 0
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["media_kinds"] == ["audio"]
    assert payload["scan"]["audio_file_count"] == 2
    assert payload["scan"]["video_file_count"] == 0
    assert payload["scan"]["media_kind_summary"] == {"audio": 2}


def test_cli_duplicates_rejects_unsupported_extension(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()

    with pytest.raises(SystemExit) as exc_info:
        main([
            "--source", str(source),
            "--include-extension", ".notmedia",
        ])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "Unsupported --include-extension" in captured.err
