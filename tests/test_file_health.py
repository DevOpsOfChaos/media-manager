from __future__ import annotations

from io import StringIO
import json
import sys
from pathlib import Path
from unittest import mock

from media_manager.core.file_health import check_file_health, detect_file_type, scan_directory_health


def test_detect_jpeg(tmp_path: Path) -> None:
    path = tmp_path / "test.jpg"
    path.write_bytes(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01')
    result = detect_file_type(path)
    assert result is not None
    assert result["mime_type"] == "image/jpeg"


def test_detect_png(tmp_path: Path) -> None:
    path = tmp_path / "test.png"
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    result = detect_file_type(path)
    assert result is not None
    assert result["mime_type"] == "image/png"


def test_detect_gif(tmp_path: Path) -> None:
    path = tmp_path / "test.gif"
    path.write_bytes(b'GIF89a' + b'\x00' * 100)
    result = detect_file_type(path)
    assert result is not None
    assert result["mime_type"] == "image/gif"


def test_detect_webp(tmp_path: Path) -> None:
    path = tmp_path / "test.webp"
    path.write_bytes(b'RIFF\x10\x00\x00\x00WEBP' + b'\x00' * 100)
    result = detect_file_type(path)
    assert result is not None
    assert result["mime_type"] == "image/webp"


def test_detect_unknown(tmp_path: Path) -> None:
    path = tmp_path / "test.xyz"
    path.write_bytes(b'\x00\x01\x02\x03')
    result = detect_file_type(path)
    assert result is None


def test_detect_file_missing(tmp_path: Path) -> None:
    result = detect_file_type(tmp_path / "nonexistent.xyz")
    assert result is None


def test_check_healthy_jpeg(tmp_path: Path) -> None:
    path = tmp_path / "healthy.jpg"
    path.write_bytes(b'\xff\xd8' + b'\x00' * 200 + b'\xff\xd9')
    result = check_file_health(path)
    assert result["healthy"] is True
    assert result["detected_type"] == "JPEG image"
    assert result["issues"] == []


def test_check_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.jpg"
    path.write_bytes(b'')
    result = check_file_health(path)
    assert result["healthy"] is False
    assert "empty" in " ".join(result["issues"]).lower()


def test_check_truncated_jpeg(tmp_path: Path) -> None:
    path = tmp_path / "truncated.jpg"
    path.write_bytes(b'\xff\xd8' + b'\x00' * 200)
    result = check_file_health(path)
    assert "Missing JPEG end marker" in " ".join(result["warnings"])


def test_check_healthy_png(tmp_path: Path) -> None:
    path = tmp_path / "healthy.png"
    png_data = (
        b'\x89PNG\r\n\x1a\n'
        + b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        + b'\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    path.write_bytes(png_data)
    result = check_file_health(path)
    assert result["healthy"] is True
    assert result["detected_type"] == "PNG image"


def test_check_missing_eoi_warning(tmp_path: Path) -> None:
    path = tmp_path / "no_eoi.png"
    png_data = (
        b'\x89PNG\r\n\x1a\n'
        + b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
    )
    path.write_bytes(png_data)
    result = check_file_health(path)
    assert "Missing PNG end chunk" in " ".join(result["warnings"])


def test_scan_directory_health(tmp_path: Path) -> None:
    (tmp_path / "good.jpg").write_bytes(b'\xff\xd8' + b'\x00' * 200 + b'\xff\xd9')
    (tmp_path / "empty.jpg").write_bytes(b'')
    (tmp_path / "text.txt").write_bytes(b'hello')
    result = scan_directory_health(tmp_path, max_files=10)
    assert result["total_scanned"] >= 2
    assert result["health_score"] > 0
    assert "healthy_count" in result
    assert "unhealthy_count" in result


def test_bridge_check_file(tmp_path: Path) -> None:
    from media_manager.bridge_health import cmd_check_file

    path = tmp_path / "test.jpg"
    path.write_bytes(b'\xff\xd8' + b'\x00' * 200 + b'\xff\xd9')

    fake_stdin = StringIO(json.dumps({"path": str(path)}))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_check_file()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["healthy"] is True
    assert output["detected_type"] == "JPEG image"


def test_bridge_scan_directory(tmp_path: Path) -> None:
    from media_manager.bridge_health import cmd_scan_directory

    (tmp_path / "good.jpg").write_bytes(b'\xff\xd8' + b'\x00' * 200 + b'\xff\xd9')

    fake_stdin = StringIO(json.dumps({"source_dir": str(tmp_path)}))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_scan_directory()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["total_scanned"] >= 1
    assert output["health_score"] >= 0
