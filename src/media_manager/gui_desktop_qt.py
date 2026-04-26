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


def _build_card(QtWidgets, title: str, subtitle: str = "", metrics: Mapping[str, Any] | None = None, *, hero: bool = False):
    card = QtWidgets.QFrame()
    card.setObjectName("HeroCard" if hero else "Card")
    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(10)
    _add_label(layout, QtWidgets, title, object_name="HeroTitle" if hero else "PageTitle")
    if subtitle:
        _add_label(layout, QtWidgets, subtitle, object_name="Muted")
    for key, value in dict(metrics or {}).items():
        _add_label(layout, QtWidgets, f"{key}: {value}", object_name="Muted")
    return card


def _render_dashboard(QtWidgets, layout, page: Mapping[str, Any]) -> None:
    hero = _mapping(page.get("hero"))
    if hero:
        layout.addWidget(_build_card(QtWidgets, _text(hero.get("title")), _text(hero.get("subtitle")), hero=True))
    metrics = [item for item in _list(page.get("metric_tiles")) if isinstance(item, Mapping)]
    if metrics:
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(14)
        for index, metric in enumerate(metrics):
            grid.addWidget(_build_card(QtWidgets, _text(metric.get("label")), _text(metric.get("helper")), {"value": metric.get("value")}), index // 3, index % 3)
        layout.addLayout(grid)
    cards = [item for item in _list(page.get("cards")) if isinstance(item, Mapping)]
    if cards:
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(14)
        for index, card in enumerate(cards):
            grid.addWidget(_build_card(QtWidgets, _text(card.get("title")), _text(card.get("subtitle")), _mapping(card.get("metrics"))), index // 2, index % 2)
        layout.addLayout(grid)


def _render_people_review(QtWidgets, layout, page: Mapping[str, Any]) -> None:
    overview = _mapping(page.get("overview"))
    layout.addWidget(_build_card(QtWidgets, _text(page.get("title")), _text(page.get("description")), overview, hero=True))
    editor = _mapping(page.get("editor"))
    groups = [item for item in _list(editor.get("groups")) if isinstance(item, Mapping)]
    if not groups:
        _add_label(layout, QtWidgets, _text(page.get("empty_state"), "Open a people review bundle."), object_name="Muted")
        return
    split = QtWidgets.QSplitter()
    group_list = QtWidgets.QListWidget()
    detail = QtWidgets.QFrame()
    detail.setObjectName("Card")
    detail_layout = QtWidgets.QVBoxLayout(detail)
    detail_layout.setContentsMargins(18, 18, 18, 18)
    for group in groups[:250]:
        group_list.addItem(f"{group.get('display_label')}  ·  {group.get('status')}  ·  {group.get('face_count')} faces")
    selected = _mapping(editor.get("selected_group"))
    if selected:
        _add_label(detail_layout, QtWidgets, _text(selected.get("display_label") or selected.get("group_id")), object_name="PageTitle")
        _add_label(detail_layout, QtWidgets, f"Status: {selected.get('status')}", object_name="Muted")
        _add_label(detail_layout, QtWidgets, f"Faces: {selected.get('face_count', 0)} | Included: {selected.get('included_faces', 0)} | Excluded: {selected.get('excluded_faces', 0)}", object_name="Muted")
    split.addWidget(group_list)
    split.addWidget(detail)
    split.setStretchFactor(0, 2)
    split.setStretchFactor(1, 3)
    layout.addWidget(split)


def _render_table(QtWidgets, layout, page: Mapping[str, Any]) -> None:
    table_model = _mapping(page.get("table")) or page
    rows = [item for item in _list(table_model.get("rows")) if isinstance(item, Mapping)]
    columns = [str(item) for item in _list(table_model.get("columns"))]
    if not columns:
        columns = ["id", "title", "status"]
    table = QtWidgets.QTableWidget(max(0, len(rows)), len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.setAlternatingRowColors(True)
    for row_index, raw_row in enumerate(rows):
        row = _mapping(raw_row)
        for col_index, col_name in enumerate(columns):
            table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(_text(row.get(col_name))))
    table.horizontalHeader().setStretchLastSection(True)
    layout.addWidget(table)
    if not rows and table_model.get("empty_state"):
        _add_label(layout, QtWidgets, _text(table_model.get("empty_state")), object_name="Muted")


def _render_page_content(QtWidgets, page: Mapping[str, Any]):
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(30, 28, 30, 28)
    layout.setSpacing(18)
    if page.get("kind") != "dashboard_page":
        _add_label(layout, QtWidgets, _text(page.get("title"), "Media Manager"), object_name="PageTitle")
        if page.get("description"):
            _add_label(layout, QtWidgets, _text(page.get("description")), object_name="Muted")
    kind = page.get("kind")
    if kind == "dashboard_page":
        _render_dashboard(QtWidgets, layout, page)
    elif kind == "people_review_page":
        _render_people_review(QtWidgets, layout, page)
    elif kind == "table_page":
        _render_table(QtWidgets, layout, page)
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
    window.resize(int(win.get("width", 1400)), int(win.get("height", 900)))
    central = QtWidgets.QWidget()
    root = QtWidgets.QHBoxLayout(central)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    sidebar = QtWidgets.QFrame()
    sidebar.setObjectName("Sidebar")
    sidebar.setFixedWidth(292)
    side_layout = QtWidgets.QVBoxLayout(sidebar)
    side_layout.setContentsMargins(20, 24, 20, 18)
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
