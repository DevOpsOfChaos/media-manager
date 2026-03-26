from __future__ import annotations

import importlib.util
import sys
from importlib import resources
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

_THIS_DIR = Path(__file__).resolve().parent
_LEGACY_MODULE_PATH = _THIS_DIR.parent / "qml_app_fixed.py"
_SPEC = importlib.util.spec_from_file_location(
    "media_manager._qml_app_fixed_file",
    _LEGACY_MODULE_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Could not load legacy qml app module from {_LEGACY_MODULE_PATH}")

_LEGACY_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_LEGACY_MODULE)

QmlAppState = _LEGACY_MODULE.QmlAppState


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Media Manager QML")

    engine = QQmlApplicationEngine()
    state = QmlAppState()
    engine.rootContext().setContextProperty("appState", state)

    qml_file = resources.files("media_manager").joinpath("qml/ModernMain.qml")
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        return 1
    return app.exec()


__all__ = ["QmlAppState", "main"]
