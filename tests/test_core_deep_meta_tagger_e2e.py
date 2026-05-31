from __future__ import annotations

from pathlib import Path

import pytest


def _build_minimal_jpeg() -> bytes:
    """Build a minimal valid JPEG with EXIF containing DateTimeOriginal."""
    soi = b'\xff\xd8'
    app1 = bytearray()
    app1 += b'\xff\xe1'                 # APP1 marker
    # EXIF header
    exif_header = b'Exif\x00\x00'
    tiff_header = b'MM\x00*\x00\x00\x00\x08'
    # IFD0 with one entry
    ifd_count = b'\x00\x01'             # 1 entry
    # Tag 0x9003 DateTimeOriginal (ASCII, tag=0x9003, type=2=ASCII, count=19, data="2024:07:15 14:30:00\0")
    tag_entry = (
        b'\x90\x03'      # tag
        b'\x00\x02'      # type ASCII
        b'\x00\x00\x00\x14'  # count = 20
        b'\x00\x00\x00\x1a'  # offset to value (26)
    )
    ifd0 = ifd_count + tag_entry + b'\x00\x00\x00\x00'  # next IFD offset = 0
    # Value data
    value_data = b'2024:07:15 14:30:00\x00'
    exif_data = exif_header + tiff_header + ifd0 + value_data
    # APP1 length (2 bytes for length field itself not included, so length = len(exif_data) + 2)
    length = len(exif_data) + 2
    app1[2:2] = length.to_bytes(2, 'big')
    app1 += exif_data

    eoi = b'\xff\xd9'
    return soi + bytes(app1) + eoi


class TestDeepMetaTaggerE2E:
    def test_real_jpeg_deep_meta(self, tmp_path: Path) -> None:
        """Integration test: create a minimal real JPEG, run deep meta extraction."""
        jpeg_path = tmp_path / "test_deep.jpg"
        jpeg_path.write_bytes(_build_minimal_jpeg())

        from media_manager.core.metadata.inspect import extract_deep_metadata
        result = extract_deep_metadata(jpeg_path)

        assert "error" not in result
        assert "camera" in result
        assert "shot" in result
        assert "gps" in result
        assert "image" in result
        assert "copyright" in result
        assert "software" in result
        assert "file" in result
        assert "raw_tags_count" in result
        assert isinstance(result["raw_tags_count"], int)

    def test_real_jpeg_deep_meta_score(self, tmp_path: Path) -> None:
        jpeg_path = tmp_path / "test_score.jpg"
        jpeg_path.write_bytes(_build_minimal_jpeg())

        from media_manager.core.metadata.inspect import extract_deep_metadata, compute_metadata_score
        meta = extract_deep_metadata(jpeg_path)
        score = compute_metadata_score(meta)
        assert "score" in score
        assert "grade" in score
        assert "missing" in score
        assert "complete" in score
        assert 0 <= score["score"] <= 100
        assert score["grade"] in ("A", "B", "C", "D")

    def test_real_jpeg_to_tags_pipeline(self, tmp_path: Path) -> None:
        """Full pipeline: real JPEG -> deep_meta -> auto_tagger tags."""
        jpeg_path = tmp_path / "test_pipeline.jpg"
        jpeg_path.write_bytes(_build_minimal_jpeg())

        from media_manager.core.metadata.inspect import extract_deep_metadata as edm
        from media_manager.core.auto_tagger import generate_tags

        deep = edm(jpeg_path)
        assert "error" not in deep

        tags = generate_tags(deep, jpeg_path.name)
        assert isinstance(tags, list)
        assert len(tags) >= 1
        assert all(isinstance(t, str) for t in tags)

    def test_real_jpeg_date_comes_through(self, tmp_path: Path) -> None:
        """Verify that DateTimeOriginal flows through deep meta into tags."""
        jpeg_path = tmp_path / "test_date.jpg"
        jpeg_path.write_bytes(_build_minimal_jpeg())

        from media_manager.core.metadata.inspect import extract_deep_metadata
        from media_manager.core.auto_tagger import generate_tags

        deep = extract_deep_metadata(jpeg_path)
        dt = deep.get("shot", {}).get("datetime")
        print(f"DEBUG: shot.datetime = {dt!r}")
        print(f"DEBUG: shot keys = {list(deep.get('shot', {}).keys())}")

        tags = generate_tags(deep, jpeg_path.name)
        # With DateTimeOriginal 2024:07:15, we should get year/month/day/season tags
        assert any(t.startswith("year:") for t in tags), f"Expected year: tag in {tags}"
        assert any(t.startswith("month:") for t in tags), f"Expected month: tag in {tags}"

    @pytest.mark.skip(reason="Requires an actual JPEG file with real EXIF data")
    def test_real_file_manual(self) -> None:
        """Manual test with a real file - skipped by default."""
        from media_manager.core.metadata.inspect import extract_deep_metadata, compute_metadata_score
        from media_manager.core.auto_tagger import generate_tags

        import sys
        if len(sys.argv) < 2:
            pytest.skip("No file path provided")

        path = Path(sys.argv[1])
        if not path.is_file():
            pytest.skip(f"File not found: {path}")

        meta = extract_deep_metadata(path)
        score = compute_metadata_score(meta)
        tags = generate_tags(meta, path.name)

        print(f"\nScore: {score['score']} ({score['grade']})")
        print(f"Tags: {tags}")
        assert meta is not None
