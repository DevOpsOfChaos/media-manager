from __future__ import annotations

import importlib
import sys
from importlib import resources

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

_QML_BACKEND = importlib.import_module("media_manager.qml_app_fixed")
QmlAppState = _QML_BACKEND.QmlAppState


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Media Manager QML")

    engine = QQmlApplicationEngine()
    state = QmlAppState()
    engine.rootContext().setContextProperty("appState", state)

    qml_file = resources.files("media_manager").joinpath("qml/ModernMainV2.qml")
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        return 1
    return app.exec()


__all__ = ["QmlAppState", "main"]
