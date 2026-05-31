from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


def _build_minimal_jpeg() -> bytes:
    """Build a valid JPEG with EXIF containing DateTimeOriginal."""
    from io import BytesIO

    image = Image.new("RGB", (16, 16), color=(64, 96, 128))
    exif = Image.Exif()
    exif[36867] = "2024:07:15 14:30:00"  # DateTimeOriginal
    buf = BytesIO()
    image.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


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
