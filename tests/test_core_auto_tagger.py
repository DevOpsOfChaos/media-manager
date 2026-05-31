from __future__ import annotations

from pathlib import Path

from media_manager.core.auto_tagger import extract_deep_metadata, generate_tags


_rich_metadata: dict = {
    "Make": "Canon",
    "Model": "EOS R5",
    "LensModel": "EF24-70mm f/2.8L II USM",
    "DateTimeOriginal": "2024:07:15 14:30:00",
    "ISO": "400",
    "FocalLength": "50 mm",
    "FocalLength35efl": "50.0 mm",
    "Flash": "Fired, Return not detected",
    "Orientation": "Rotate 90 CW",
    "GPSLatitude": "48.8566",
    "GPSLongitude": "2.3522",
    "GPSAltitude": "35.0",
}

_minimal_metadata: dict = {
    "Make": "Sony",
    "DateTimeOriginal": "2023:12:25 08:00:00",
}

_fallback_metadata: dict = {
    "Model": "iPhone 14",
    "CreateDate": "2024:01:15 10:00:00",
    "ISO": "1600",
    "FocalLength": "24 mm",
}


def test_extract_deep_metadata_rich(monkeypatch) -> None:
    monkeypatch.setattr("media_manager.exiftool.read_exiftool_metadata",
                        lambda path, **kw: (_rich_metadata, True, None, None))

    deep = extract_deep_metadata(Path("test.jpg"))
    assert deep["camera"]["make"] == "Canon"
    assert deep["camera"]["model"] == "EOS R5"
    assert deep["camera"]["lens"] == "EF24-70mm f/2.8L II USM"
    assert deep["shot"]["datetime"] == "2024:07:15 14:30:00"
    assert deep["shot"]["iso"] == "400"
    assert deep["shot"]["focal_length"] == "50 mm"
    assert deep["shot"]["flash"] == "Fired, Return not detected"
    assert deep["shot"]["orientation"] == "Rotate 90 CW"
    assert deep["gps"]["latitude"] == "48.8566"
    assert deep["gps"]["longitude"] == "2.3522"
    assert deep["gps"]["altitude"] == "35.0"
    assert deep["meta_score"]["score"] == 75


def test_extract_deep_metadata_minimal(monkeypatch) -> None:
    monkeypatch.setattr("media_manager.exiftool.read_exiftool_metadata",
                        lambda path, **kw: (_minimal_metadata, True, None, None))

    deep = extract_deep_metadata(Path("test.jpg"))
    assert deep["camera"]["make"] == "Sony"
    assert deep["shot"]["datetime"] == "2023:12:25 08:00:00"
    assert deep["meta_score"]["score"] > 0


def test_extract_deep_metadata_fallback_model(monkeypatch) -> None:
    monkeypatch.setattr("media_manager.exiftool.read_exiftool_metadata",
                        lambda path, **kw: (_fallback_metadata, True, None, None))

    deep = extract_deep_metadata(Path("test.jpg"))
    assert deep["camera"]["model"] == "iPhone 14"
    assert deep["shot"]["datetime"] == "2024:01:15 10:00:00"
    assert deep["shot"]["iso"] == "1600"


def test_extract_deep_metadata_no_metadata(monkeypatch) -> None:
    monkeypatch.setattr("media_manager.exiftool.read_exiftool_metadata",
                        lambda path, **kw: ({}, False, "NoFile", "Not found"))

    deep = extract_deep_metadata(Path("nonexistent.jpg"))
    assert deep["meta_score"]["score"] == 0
    assert deep["camera"] == {}


def test_extract_deep_metadata_exiftool_import_error(monkeypatch) -> None:
    def _raise(*args, **kwargs):
        raise ImportError("exiftool not found")
    monkeypatch.setattr("media_manager.exiftool.read_exiftool_metadata", _raise)

    deep = extract_deep_metadata(Path("test.jpg"))
    assert deep["meta_score"]["score"] == 0


class TestGenerateTags:
    def test_generate_tags_rich(self) -> None:
        deep_meta = {
            "camera": {
                "make": "Canon",
                "model": "EOS R5",
                "lens": "EF24-70mm f/2.8L II USM",
            },
            "shot": {
                "datetime": "2024:07:15 14:30:00",
                "iso": "400",
                "focal_length": "50 mm",
                "flash": "Fired, Return not detected",
                "orientation": "Rotate 90 CW",
            },
            "gps": {
                "latitude": "48.8566",
            },
            "meta_score": {"score": 90},
        }
        tags = generate_tags(deep_meta, "IMG_0001.CR2")
        assert "camera:Canon" in tags
        assert "camera:EOS R5" in tags
        assert "lens:EF24-70mm f/2.8L II USM" in tags
        assert "year:2024" in tags
        assert "month:2024-07" in tags
        assert "season:summer" in tags
        assert "time:night" in tags
        assert "iso:medium" in tags
        assert "focal:normal" in tags
        assert "has:gps" in tags
        assert "flash:on" in tags
        assert "orientation:portrait" in tags
        assert "type:raw" in tags
        assert "meta:excellent" in tags
        assert len(tags) > 10

    def test_generate_tags_minimal(self) -> None:
        deep_meta = {
            "camera": {"make": "Nikon"},
            "shot": {"datetime": "2022:01:10 12:00:00"},
            "gps": {},
            "meta_score": {"score": 30},
        }
        tags = generate_tags(deep_meta, "photo.jpg")
        assert "camera:Nikon" in tags
        assert "year:2022" in tags
        assert "season:winter" in tags
        assert "type:jpeg" in tags

    def test_generate_tags_no_metadata(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "type:jpeg" in tags
        assert len([t for t in tags if not t.startswith("type:")]) == 0

    def test_generate_tags_invalid_date(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"datetime": "not-a-date"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "year:" not in tags

    def test_generate_tags_invalid_iso(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"iso": "auto"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "iso:" not in tags

    def test_generate_tags_invalid_focal(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"focal_length": "unknown"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "focal:" not in tags

    def test_generate_tags_decade(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"datetime": "1998:03:15 10:00:00"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "decade:1990s" in tags
        assert "season:spring" in tags
        assert "time:night" in tags

    def test_generate_tags_evening(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"datetime": "2024:01:01 18:00:00"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "time:night" in tags

    def test_generate_tags_night(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"datetime": "2024:01:01 23:00:00"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "time:night" in tags

    def test_generate_tags_weekend(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"datetime": "2024:07:13 12:00:00"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "weekend" in tags

    def test_generate_tags_iso_boundaries(self) -> None:
        meta = {"camera": {}, "shot": {}, "gps": {}, "meta_score": {"score": 0}}

        meta["shot"] = {"iso": "100"}
        assert "iso:low" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"iso": "200"}
        assert "iso:low" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"iso": "400"}
        assert "iso:medium" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"iso": "800"}
        assert "iso:medium" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"iso": "1600"}
        assert "iso:high" in generate_tags(meta, "f.jpg")

    def test_generate_tags_focal_boundaries(self) -> None:
        meta = {"camera": {}, "shot": {}, "gps": {}, "meta_score": {"score": 0}}

        meta["shot"] = {"focal_length": "18 mm"}
        assert "focal:wide" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"focal_length": "24 mm"}
        assert "focal:wide" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"focal_length": "50 mm"}
        assert "focal:normal" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"focal_length": "70 mm"}
        assert "focal:normal" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"focal_length": "135 mm"}
        assert "focal:tele" in generate_tags(meta, "f.jpg")

        meta["shot"] = {"focal_length": "300 mm"}
        assert "focal:supertele" in generate_tags(meta, "f.jpg")

    def test_generate_tags_flash_off(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"flash": "No Flash"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "flash:on" not in tags

    def test_generate_tags_orientation_normal(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"orientation": "Horizontal (normal)"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "orientation:portrait" not in tags

    def test_generate_tags_file_type_video(self) -> None:
        deep_meta = {"camera": {}, "shot": {}, "gps": {}, "meta_score": {"score": 0}}
        tags = generate_tags(deep_meta, "movie.mp4")
        assert "type:video" in tags

    def test_generate_tags_file_type_png(self) -> None:
        deep_meta = {"camera": {}, "shot": {}, "gps": {}, "meta_score": {"score": 0}}
        tags = generate_tags(deep_meta, "screenshot.png")
        assert "type:png" in tags

    def test_generate_tags_meta_excellent(self) -> None:
        deep_meta = {"camera": {}, "shot": {}, "gps": {}, "meta_score": {"score": 80}}
        tags = generate_tags(deep_meta, "test.jpg")
        assert "meta:excellent" in tags

    def test_generate_tags_meta_good(self) -> None:
        deep_meta = {"camera": {}, "shot": {}, "gps": {}, "meta_score": {"score": 60}}
        tags = generate_tags(deep_meta, "test.jpg")
        assert "meta:good" in tags
        assert "meta:excellent" not in tags

    def test_generate_tags_date_only_defaults_afternoon(self) -> None:
        deep_meta = {
            "camera": {},
            "shot": {"datetime": "2024:01:01"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert "time:afternoon" in tags

    def test_generate_tags_returns_sorted(self) -> None:
        deep_meta = {
            "camera": {"make": "Canon"},
            "shot": {"datetime": "2024:01:01 12:00:00"},
            "gps": {},
            "meta_score": {"score": 0},
        }
        tags = generate_tags(deep_meta, "test.jpg")
        assert tags == sorted(tags)
