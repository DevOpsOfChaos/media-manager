from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def shell_model_to_pretty_json(model: Mapping[str, Any]) -> str:
    """Compatibility helper kept for older tests; the active GUI is Qt/PySide6."""
    return json.dumps(dict(model), indent=2, ensure_ascii=False)


def run_tk_gui(model: Mapping[str, Any]) -> int:
    """Deprecated compatibility shim.

    Tkinter is intentionally no longer used. This avoids crashing on Windows
    Python environments where tkinter is not installed and points callers to the
    modern Qt backend instead.
    """
    raise RuntimeError("Tkinter GUI is deprecated. Use media-manager-gui with the optional PySide6 GUI backend.")


__all__ = ["run_tk_gui", "shell_model_to_pretty_json"]
