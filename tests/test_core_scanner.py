from __future__ import annotations

from pathlib import Path

from media_manager.core.scanner import ScanOptions, scan_media_sources



def test_scan_media_sources_discovers_media_and_skips_non_media(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    (source / "photo.jpg").write_bytes(b"jpg")
    (source / "clip.mp4").write_bytes(b"mp4")
    (source / "notes.txt").write_text("ignore", encoding="utf-8")

    summary = scan_media_sources(ScanOptions(source_dirs=(source,)))

    assert summary.media_file_count == 2
    assert summary.skipped_non_media_files == 1
    assert [item.relative_path.as_posix() for item in summary.files] == ["clip.mp4", "photo.jpg"]



def test_scan_media_sources_skips_hidden_paths_by_default(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    hidden_dir = source / ".secret"
    hidden_dir.mkdir()
    (hidden_dir / "hidden.jpg").write_bytes(b"hidden")
    (source / "visible.jpg").write_bytes(b"visible")

    summary = scan_media_sources(ScanOptions(source_dirs=(source,)))

    assert summary.media_file_count == 1
    assert summary.skipped_hidden_paths == 1
    assert [item.relative_path.as_posix() for item in summary.files] == ["visible.jpg"]



def test_scan_media_sources_can_include_hidden_paths(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    hidden_dir = source / ".secret"
    hidden_dir.mkdir()
    (hidden_dir / "hidden.jpg").write_bytes(b"hidden")
    (source / "visible.jpg").write_bytes(b"visible")

    summary = scan_media_sources(
        ScanOptions(
            source_dirs=(source,),
            include_hidden=True,
        )
    )

    assert summary.media_file_count == 2
    assert summary.skipped_hidden_paths == 0
    assert [item.relative_path.as_posix() for item in summary.files] == [".secret/hidden.jpg", "visible.jpg"]



def test_scan_media_sources_reports_missing_sources(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    missing = tmp_path / "missing"

    (source / "photo.jpg").write_bytes(b"jpg")

    summary = scan_media_sources(ScanOptions(source_dirs=(missing, source)))

    assert summary.media_file_count == 1
    assert summary.missing_sources == [missing]
