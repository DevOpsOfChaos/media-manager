from datetime import datetime
from pathlib import Path

import media_manager.renamer as renamer
from media_manager.renamer import RenameConfig, rename_media, render_rename_filename


class DummyDateTime(datetime):
    pass


def test_render_rename_filename_uses_template_and_suffix() -> None:
    file_path = Path("holiday.jpg")
    media_dt = datetime(2024, 7, 18, 13, 45, 9)
    rendered = render_rename_filename(file_path, media_dt, "{year}{month}{day}_{stem}{suffix}", 1)
    assert rendered == "20240718_holiday.jpg"


def test_rename_media_preview_uses_unique_names_for_collisions(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"a")
    (source / "b.jpg").write_bytes(b"b")

    monkeypatch.setattr(renamer, "resolve_media_datetime", lambda *args, **kwargs: datetime(2024, 7, 18, 13, 45, 9))
    result = rename_media(RenameConfig(source_dirs=[source], template="same{suffix}", dry_run=True))

    assert result.processed == 2
    assert result.renamed == 2
    assert result.entries[0].target.name == "same.jpg"
    assert result.entries[1].target.name == "same_1.jpg"


def test_rename_media_apply_renames_file(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "source"
    source.mkdir()
    original = source / "old.jpg"
    original.write_bytes(b"x")

    monkeypatch.setattr(renamer, "resolve_media_datetime", lambda *args, **kwargs: datetime(2024, 7, 18, 13, 45, 9))
    result = rename_media(RenameConfig(source_dirs=[source], template="renamed{suffix}", dry_run=False))

    assert result.processed == 1
    assert result.renamed == 1
    assert not original.exists()
    assert (source / "renamed.jpg").exists()
