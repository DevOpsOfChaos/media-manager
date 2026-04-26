from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .core.gui_theme import build_qt_stylesheet


class MissingQtDependencyError(RuntimeError):
    """Raised when the optional PySide6 GUI backend is not installed."""


def qt_install_guidance() -> str:
    return (
        "PySide6 is required for the modern desktop GUI.\n"
        "Install it with:\n"
        "  python -m pip install -e .[gui]\n"
        "Then run:\n"
        "  media-manager-gui"
    )


def load_qt_modules():
    try:  # pragma: no cover - depends on optional GUI dependency
        from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise MissingQtDependencyError(str(exc)) from exc
    return QtCore, QtGui, QtWidgets


def shell_model_to_pretty_json(model: Mapping[str, Any]) -> str:
    return json.dumps(dict(model), indent=2, ensure_ascii=False)


def _text(value: object, fallback: str = "") -> str:
    return str(value) if value is not None else fallback


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _add_label(layout, QtWidgets, text: str, *, object_name: str | None = None, word_wrap: bool = True):
    label = QtWidgets.QLabel(text)
    if object_name:
        label.setObjectName(object_name)
    label.setWordWrap(word_wrap)
    layout.addWidget(label)
    return label


def _build_metric_card(QtWidgets, title: str, subtitle: str, metrics: Mapping[str, Any]):
    card = QtWidgets.QFrame()
    card.setObjectName("Card")
    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(8)
    _add_label(layout, QtWidgets, title, object_name="PageTitle")
    if subtitle:
        _add_label(layout, QtWidgets, subtitle, object_name="Muted")
    if metrics:
        row = QtWidgets.QHBoxLayout()
        for key, value in metrics.items():
            metric = QtWidgets.QLabel(f"{key}: {value}")
            metric.setObjectName("Muted")
            row.addWidget(metric)
        row.addStretch(1)
        layout.addLayout(row)
    return card


def _render_page_content(QtWidgets, page: Mapping[str, Any]):
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(28, 28, 28, 28)
    layout.setSpacing(18)
    _add_label(layout, QtWidgets, _text(page.get("title"), "Media Manager"), object_name="PageTitle")
    if page.get("description"):
        _add_label(layout, QtWidgets, _text(page.get("description")), object_name="Muted")

    kind = page.get("kind")
    if kind == "dashboard_page":
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(16)
        for index, raw_card in enumerate(_list(page.get("cards"))):
            card = _mapping(raw_card)
            grid.addWidget(
                _build_metric_card(QtWidgets, _text(card.get("title")), _text(card.get("subtitle")), _mapping(card.get("metrics"))),
                index // 2,
                index % 2,
            )
        layout.addLayout(grid)
    elif kind == "people_review_page":
        overview = _mapping(page.get("overview"))
        layout.addWidget(_build_metric_card(QtWidgets, "People review", "Curate detected people groups.", overview))
        groups = _list(page.get("groups"))[:10]
        for raw_group in groups:
            group = _mapping(raw_group)
            layout.addWidget(
                _build_metric_card(
                    QtWidgets,
                    _text(group.get("display_label") or group.get("group_id")),
                    f"status={group.get('status')}",
                    {"faces": group.get("face_count", 0), "included": group.get("included_faces", 0), "excluded": group.get("excluded_faces", 0)},
                )
            )
        if not groups and page.get("empty_state"):
            _add_label(layout, QtWidgets, _text(page.get("empty_state")), object_name="Muted")
    elif kind == "table_page":
        rows = _list(page.get("rows"))
        table = QtWidgets.QTableWidget(max(1, len(rows)), len(_list(page.get("columns"))))
        columns = [str(item) for item in _list(page.get("columns"))]
        table.setHorizontalHeaderLabels(columns)
        for row_index, raw_row in enumerate(rows):
            row = _mapping(raw_row)
            for col_index, col_name in enumerate(columns):
                table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(_text(row.get(col_name))))
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
    else:
        empty = page.get("empty_state") or "This view is ready for the next GUI iteration."
        _add_label(layout, QtWidgets, _text(empty), object_name="Muted")
    layout.addStretch(1)
    return container


def run_qt_gui(model: Mapping[str, Any]) -> int:  # pragma: no cover - GUI runtime
    QtCore, QtGui, QtWidgets = load_qt_modules()
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    theme = _mapping(model.get("theme"))
    app.setStyleSheet(build_qt_stylesheet(str(theme.get("theme") or "modern-dark")))

    window = QtWidgets.QMainWindow()
    win = _mapping(model.get("window"))
    window.setWindowTitle(_text(win.get("title"), "Media Manager"))
    window.resize(int(win.get("width", 1320)), int(win.get("height", 860)))
    central = QtWidgets.QWidget()
    root = QtWidgets.QHBoxLayout(central)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    sidebar = QtWidgets.QFrame()
    sidebar.setObjectName("Sidebar")
    sidebar.setFixedWidth(260)
    side_layout = QtWidgets.QVBoxLayout(sidebar)
    side_layout.setContentsMargins(18, 24, 18, 18)
    side_layout.setSpacing(12)
    app_info = _mapping(model.get("application"))
    _add_label(side_layout, QtWidgets, _text(app_info.get("title"), "Media Manager"), object_name="AppTitle")
    _add_label(side_layout, QtWidgets, _text(app_info.get("subtitle")), object_name="Muted")
    for item in _list(model.get("navigation")):
        nav = _mapping(item)
        button = QtWidgets.QPushButton(_text(nav.get("label")))
        button.setCheckable(True)
        button.setChecked(bool(nav.get("active")))
        button.setEnabled(bool(nav.get("enabled", True)))
        side_layout.addWidget(button)
    side_layout.addStretch(1)

    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(_render_page_content(QtWidgets, _mapping(model.get("page"))))
    root.addWidget(sidebar)
    root.addWidget(scroll, 1)
    window.setCentralWidget(central)
    status = _mapping(model.get("status_bar"))
    window.statusBar().showMessage(_text(status.get("text"), "Ready."))
    window.show()
    return int(app.exec())


__all__ = [
    "MissingQtDependencyError",
    "load_qt_modules",
    "qt_install_guidance",
    "run_qt_gui",
    "shell_model_to_pretty_json",
]
