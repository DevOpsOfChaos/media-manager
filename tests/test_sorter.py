from pathlib import Path

from media_manager.sorter import SortConfig, build_target_dir, ensure_unique_path


class DummyDate:
    year = 2024
    month = 7
    day = 18


def test_build_target_dir_uses_template() -> None:
    target = build_target_dir(Path("/dest"), DummyDate(), "{year}/{month}/{day}")
    assert target.as_posix() == "/dest/2024/07/18"


def test_ensure_unique_path_returns_incremented_name(tmp_path: Path) -> None:
    existing = tmp_path / "photo.jpg"
    existing.write_bytes(b"x")
    unique = ensure_unique_path(existing)
    assert unique.name == "photo_1.jpg"
