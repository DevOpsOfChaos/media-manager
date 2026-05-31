from __future__ import annotations

from pathlib import Path

from media_manager.core.magic_bytes import detect_file_type, is_media_file, is_image_file


_sig_bytes: dict[str, bytes] = {
    "jpeg": b'\xff\xd8\xff\xe0\x00' + b'\x00' * 11,
    "jpeg_exif": b'\xff\xd8\xff\xe1\x00' + b'\x00' * 11,
    "png": b'\x89PNG\r\n\x1a\n\x00\x00\x00\x00',
    "gif87a": b'GIF87a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "gif89a": b'GIF89a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "bmp": b'BM\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "heic": b'\x00\x00\x00\x1cftypheic\x00\x00',
    "tiff_ii": b'II*\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "tiff_mm": b'MM\x00*\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "mp4": b'\x00\x00\x00\x1cftypmp42\x00\x00',
    "mov": b'\x00\x00\x00\x1cftypqt  \x00\x00',
    "webm": b'\x1aE\xdf\xa3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "mp3_id3": b'ID3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "mp3_mpeg": b'\xff\xfb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "flac": b'fLaC\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "ogg": b'OggS\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "riff_webp": b'RIFF\x00\x00\x00\x00WEBP\x00\x00\x00\x00',
    "riff_avi": b'RIFF\x00\x00\x00\x00AVI \x00\x00\x00\x00',
    "riff_wav": b'RIFF\x00\x00\x00\x00WAVE\x00\x00\x00\x00',
    "pdf": b'%PDF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "zip": b'PK\x03\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    "random": b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f',
}


def _make_file(tmp_path: Path, name: str, content: bytes) -> Path:
    p = tmp_path / name
    p.write_bytes(content)
    return p


class TestDetectJPEG:
    def test_jfif(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.jpg", _sig_bytes["jpeg"])
        result = detect_file_type(f)
        assert result is not None
        assert result["category"] == "photo"
        assert "JPEG" in result["description"]

    def test_exif(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.jpg", _sig_bytes["jpeg_exif"])
        result = detect_file_type(f)
        assert result is not None
        assert result["category"] == "photo"
        assert "EXIF" in result["description"]


class TestDetectPNG:
    def test_png(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.png", _sig_bytes["png"])
        result = detect_file_type(f)
        assert result is not None
        assert result["category"] == "photo"
        assert result["mime_type"] == "image/png"


class TestDetectGIF:
    def test_gif87a(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.gif", _sig_bytes["gif87a"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/gif"

    def test_gif89a(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.gif", _sig_bytes["gif89a"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/gif"


class TestDetectBMP:
    def test_bmp(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.bmp", _sig_bytes["bmp"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/bmp"


class TestDetectHEIC:
    def test_heic(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.heic", _sig_bytes["heic"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/heic"


class TestDetectTIFF:
    def test_intel(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.tiff", _sig_bytes["tiff_ii"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/tiff"

    def test_motorola(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.tiff", _sig_bytes["tiff_mm"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "image/tiff"


class TestDetectVideo:
    def test_mp4(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.mp4", _sig_bytes["mp4"])
        result = detect_file_type(f)
        assert result is not None
        assert result["category"] == "video"
        assert result["mime_type"] == "video/mp4"

    def test_mov(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.mov", _sig_bytes["mov"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "video/quicktime"

    def test_webm(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.webm", _sig_bytes["webm"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "video/webm"


class TestDetectAudio:
    def test_mp3_id3(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.mp3", _sig_bytes["mp3_id3"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/mpeg"

    def test_mp3_mpeg(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.mp3", _sig_bytes["mp3_mpeg"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/mpeg"

    def test_flac(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.flac", _sig_bytes["flac"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/flac"

    def test_ogg(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.ogg", _sig_bytes["ogg"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/ogg"


class TestDetectRIFFSubtypes:
    def test_webp(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.webp", _sig_bytes["riff_webp"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/wav"
        assert result["detected_by"] == "magic_bytes"

    def test_avi(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.avi", _sig_bytes["riff_avi"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/wav"
        assert result["detected_by"] == "magic_bytes"

    def test_wav(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.wav", _sig_bytes["riff_wav"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "audio/wav"
        assert result["detected_by"] == "magic_bytes"


class TestDetectOther:
    def test_pdf(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.pdf", _sig_bytes["pdf"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "application/pdf"
        assert result["category"] == "document"

    def test_zip(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.zip", _sig_bytes["zip"])
        result = detect_file_type(f)
        assert result is not None
        assert result["mime_type"] == "application/zip"
        assert result["category"] == "archive"


class TestDetectUnknown:
    def test_random_bytes(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "random.bin", _sig_bytes["random"])
        result = detect_file_type(f)
        assert result is None

    def test_short_file(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "short.bin", b'\xff')
        result = detect_file_type(f)
        assert result is None

    def test_empty_file(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "empty.bin", b'')
        result = detect_file_type(f)
        assert result is None


class TestHelperFunctions:
    def test_is_media_file_jpeg(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.jpg", _sig_bytes["jpeg"])
        assert is_media_file(f) is True

    def test_is_media_file_pdf(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.pdf", _sig_bytes["pdf"])
        assert is_media_file(f) is False

    def test_is_media_file_unknown(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.bin", _sig_bytes["random"])
        assert is_media_file(f) is False

    def test_is_image_file_jpeg(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.jpg", _sig_bytes["jpeg"])
        assert is_image_file(f) is True

    def test_is_image_file_tiff(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.tiff", _sig_bytes["tiff_ii"])
        assert is_image_file(f) is True

    def test_is_image_file_mp4(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.mp4", _sig_bytes["mp4"])
        assert is_image_file(f) is False


class TestConfidenceValues:
    def test_long_signature_high_confidence(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.png", _sig_bytes["png"])
        result = detect_file_type(f)
        assert result is not None
        assert result["confidence"] == 1.0

    def test_short_signature_lower_confidence(self, tmp_path: Path) -> None:
        f = _make_file(tmp_path, "test.bmp", _sig_bytes["bmp"])
        result = detect_file_type(f)
        assert result is not None
        assert result["confidence"] == 0.7
