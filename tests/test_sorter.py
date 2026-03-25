from datetime import datetime
from pathlib import Path

from media_manager.sorter import build_relative_target, unique_destination


def test_build_relative_target_uses_template():
    dt = datetime(2024, 5, 7, 13, 45)
    result = build_relative_target(dt, ".jpg", "{year}/{month_num}-{month_name}/{day}")
    assert result == Path("2024/05-Mai/07")


def test_unique_destination_adds_suffix(tmp_path):
    original = tmp_path / "image.jpg"
    original.write_text("a", encoding="utf-8")

    candidate = unique_destination(original)
    assert candidate.name == "image_1.jpg"
