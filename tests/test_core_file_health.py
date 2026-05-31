from __future__ import annotations

from pathlib import Path

from media_manager.core.file_health import check_file_health, detect_file_type, scan_directory_health


_jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01'
_jpeg_body = b'\x01' * 100
_jpeg_tail = b'\xff\xd9'
_jpeg_complete = _jpeg_header + _jpeg_body + _jpeg_tail
_jpeg_truncated = _jpeg_header + _jpeg_body  # missing EOI
_jpeg_no_soi = b'\xff\xe0\x00' + _jpeg_body + _jpeg_tail

_png_header = b'\x89PNG\r\n\x1a\n'
_png_body = b'\x00' * 50
_png_iend = b'\x00\x00\x00\x00IEND\xaeB`\x82'
_png_complete = _png_header + _png_body + _png_iend
_png_no_iend = _png_header + _png_body

_gif_header = b'GIF89a' + b'\x00' * 20


class TestDetectFileType:
    def test_jpeg(self, tmp_path: Path) -> None:
        f = tmp_path / "test.jpg"
        f.write_bytes(_jpeg_header)
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/jpeg"

    def test_png(self, tmp_path: Path) -> None:
        f = tmp_path / "test.png"
        f.write_bytes(_png_header)
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/png"

    def test_gif(self, tmp_path: Path) -> None:
        f = tmp_path / "test.gif"
        f.write_bytes(_gif_header)
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/gif"

    def test_unknown(self, tmp_path: Path) -> None:
        f = tmp_path / "test.bin"
        f.write_bytes(b'\x00' * 20)
        result = detect_file_type(f)
        assert result is None

    def test_unreadable(self, tmp_path: Path) -> None:
        result = detect_file_type(tmp_path / "nonexistent.file")
        assert result is None

    def test_video_by_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "video.mp4"
        f.write_bytes(b'\x00' * 50)
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "video/mp4"

    def test_audio_by_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "song.mp3"
        f.write_bytes(b'\x00' * 50)
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/mp3"


class TestCheckFileHealth:
    def test_healthy_jpeg(self, tmp_path: Path) -> None:
        f = tmp_path / "healthy.jpg"
        f.write_bytes(_jpeg_complete)
        result = check_file_health(f)
        assert result["healthy"] is True
        assert result["detected_type"] == "JPEG image"
        assert result["issues"] == []

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.jpg"
        f.write_bytes(b'')
        result = check_file_health(f)
        assert result["healthy"] is False
        assert "0 bytes" in result["issues"][0]

    def test_file_not_found(self, tmp_path: Path) -> None:
        result = check_file_health(tmp_path / "missing.jpg")
        assert result["healthy"] is False
        assert any("Cannot access" in i for i in result["issues"])

    def test_unknown_format(self, tmp_path: Path) -> None:
        f = tmp_path / "unknown.bin"
        f.write_bytes(b'\x00' * 200)
        result = check_file_health(f)
        assert result["healthy"] is False
        assert any("Unknown" in i for i in result["issues"])

    def test_jpeg_missing_eoi(self, tmp_path: Path) -> None:
        f = tmp_path / "truncated.jpg"
        f.write_bytes(_jpeg_truncated)
        result = check_file_health(f)
        assert "EOI" in str(result.get("warnings", []))

    def test_jpeg_missing_soi_detected(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.jpg"
        f.write_bytes(_jpeg_no_soi)
        result = check_file_health(f)
        assert result["healthy"] is False
        assert any("Unknown" in i or "corrupted" in i for i in result["issues"])

    def test_png_healthy(self, tmp_path: Path) -> None:
        f = tmp_path / "healthy.png"
        f.write_bytes(_png_complete)
        result = check_file_health(f)
        assert result["healthy"] is True
        assert result["detected_type"] == "PNG image"

    def test_png_missing_iend(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.png"
        f.write_bytes(_png_no_iend)
        result = check_file_health(f)
        assert "IEND" in str(result.get("warnings", []))

    def test_file_size_below_minimum(self, tmp_path: Path) -> None:
        f = tmp_path / "small.jpg"
        f.write_bytes(_jpeg_complete[:50])
        result = check_file_health(f)
        assert "below minimum" in str(result.get("warnings", []))


class TestScanDirectoryHealth:
    def test_scan_mixed(self, tmp_path: Path) -> None:
        (tmp_path / "good1.jpg").write_bytes(_jpeg_complete)
        (tmp_path / "good2.jpg").write_bytes(_jpeg_complete)
        (tmp_path / "bad.jpg").write_bytes(_jpeg_no_soi)
        (tmp_path / "empty.jpg").write_bytes(b'')

        result = scan_directory_health(tmp_path, max_files=10)
        assert result["total_scanned"] == 4
        assert result["healthy_count"] == 2
        assert result["unhealthy_count"] == 2
        assert result["health_score"] == 50

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        result = scan_directory_health(tmp_path, max_files=10)
        assert result["total_scanned"] == 0
        assert result["healthy_count"] == 0
        assert result["unhealthy_count"] == 0

    def test_scan_respects_max_files(self, tmp_path: Path) -> None:
        for i in range(20):
            (tmp_path / f"img{i:03d}.jpg").write_bytes(_jpeg_complete)

        result = scan_directory_health(tmp_path, max_files=5)
        assert result["total_scanned"] == 5

    def test_scan_skips_directories(self, tmp_path: Path) -> None:
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.jpg").write_bytes(_jpeg_complete)

        result = scan_directory_health(tmp_path, max_files=10)
        assert result["total_scanned"] >= 1
        assert result["healthy_count"] >= 1
