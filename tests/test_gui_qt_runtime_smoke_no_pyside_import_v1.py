from __future__ import annotations

import sys

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_guarded_runtime_smoke_flow_does_not_import_pyside6() -> None:
    sys.modules.pop("PySide6", None)

    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())

    assert bundle["summary"]["ready_for_shell_route"] is True
    assert "PySide6" not in sys.modules
    assert bundle["backend_probe"]["imports_backend"] is False
