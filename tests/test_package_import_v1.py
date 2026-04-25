from __future__ import annotations

import importlib


def test_top_level_package_import_is_lightweight() -> None:
    package = importlib.import_module("media_manager")

    assert package.__version__ == "0.6.0"
