from __future__ import annotations

import importlib


def test_core_package_import_is_lightweight() -> None:
    package = importlib.import_module("media_manager.core")

    assert package.__name__ == "media_manager.core"
    assert hasattr(package, "__all__")
