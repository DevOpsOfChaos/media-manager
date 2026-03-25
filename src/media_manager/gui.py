from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .exiftool import resolve_exiftool_path
from .settings import (
    DEFAULT_TARGET_TEMPLATE,
    get_import_set,
    list_import_sets,
    load_app_settings,
    remove_import_set,
    save_app_settings,
    upsert_import_set,
)
from .sorter import SortConfig, organize_media

APP_STYLESHEET = """
QMainWindow {
    background: #0B1220;
}
QWidget {
    color: #E5E7EB;
    font-size: 13px;
}
QFrame#Card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 18px;
}
QFrame#Nav {
    background: #0F172A;
    border: 1px solid #1F2937;
    border-radius: 18px;
}
QGroupBox {
    border: 1px solid #1F2937;
    border-radius: 16px;
    margin-top: 12px;
    padding-top: 16px;
    background: #111827;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 4px;
    color: #F9FAFB;
    font-weight: 600;
}
QLineEdit, QListWidget, QTableWidget, QComboBox {
    background: #0F172A;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 8px;
    selection-background-color: #2563EB;
    alternate-background-color: #101A2D;
}
QListWidget::item {
    padding: 8px;
    border-radius: 8px;
}
QPushButton {
    background: #2563EB;
    color: #F9FAFB;
    border: none;
    border-radius: 12px;
    padding: 9px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #1D4ED8;
}
QPushButton:disabled {
    background: #374151;
    color: #9CA3AF;
}
QPushButton[variant="secondary"] {
    background: #1F2937;
    color: #F9FAFB;
    border: 1px solid #334155;
}
QPushButton[variant="secondary"]:hover {
    background: #273449;
}
QPushButton[nav="true"] {
    text-align: left;
    padding: 12px 14px;
}
QHeaderView::section {
    background: #111827;
    color: #F9FAFB;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #334155;
}
QStatusBar {
    background: #0B1220;
    border-top: 1px solid #111827;
}
QCheckBox, QRadioButton {
    spacing: 8px;
}
"""

STATUS_LABELS = {
    "preview-copy": "Preview copy",
    "preview-move": "Preview move",
    "copied": "Copied",
    "moved": "Moved",
    "error": "Error",
}


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "-") -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(14)
        value_font.setBold(True)
        self.value_label.setFont(value_font)

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class ModuleCard(QFrame):
    def __init__(self, title: str, description: str, button_text: str, enabled: bool = True) -> None:
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #94A3B8;")

        self.button = QPushButton(button_text)
        if not enabled:
            self.button.setEnabled(False)
            self.button.setProperty("variant", "secondary")
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch(1)
        layout.addWidget(self.button)


def compact_path_label(path: Path) -> str:
    name = path.name or str(path)
    parent = path.parent.name or path.anchor or str(path.parent)
    if name == str(path):
        return name
    return f"{name}  [{parent}]"


def relative_target_folder(target_path: Path, target_root: Path) -> str:
    try:
        relative = target_path.parent.relative_to(target_root)
        return relative.as_posix() if str(relative) != "." else "/"
    except ValueError:
        return str(target_path.parent)


class MediaManagerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Media Manager")
        self.resize(1560, 980)
        self.setMinimumSize(1360, 860)
        self.app_settings: dict[str, object] = {}

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target folder")
        self.exiftool_input = QLineEdit()
        self.exiftool_input.setPlaceholderText("Auto-detect when empty")
        self.template_input = QLineEdit(DEFAULT_TARGET_TEMPLATE)
        self.apply_checkbox = QCheckBox("Apply")

        self.import_set_combo = QComboBox()
        self.import_set_combo.setMinimumWidth(260)

        self.source_list = QListWidget()
        self.source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.source_list.setAlternatingRowColors(True)

        self.source_details_label = QLabel("No source folder selected.")
        self.source_details_label.setWordWrap(True)
        self.source_details_label.setStyleSheet("color: #94A3B8;")

        self.copy_radio = QRadioButton("Copy")
        self.move_radio = QRadioButton("Move")
        self.copy_radio.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.copy_radio)
        self.mode_group.addButton(self.move_radio)

        self.results_summary_label = QLabel("No run yet.")
        self.results_summary_label.setWordWrap(True)
        self.results_summary_label.setStyleSheet("color: #94A3B8;")

        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels(["Status", "File", "Source", "Target", "Details"])
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.sources_card = StatCard("Sources", "0")
        self.target_card = StatCard("Target", "Not set")
        self.mode_card = StatCard("Mode", "Copy")
        self.run_mode_card = StatCard("Run", "Preview")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.stack = QStackedWidget()
        self.home_button = QPushButton("Home")
        self.home_button.setProperty("nav", "true")
        self.home_button.setProperty("variant", "secondary")
        self.organize_button = QPushButton("Organize")
        self.organize_button.setProperty("nav", "true")
        self.organize_button.setProperty("variant", "secondary")

        self._build_ui()
        self._wire_signals()
        self._load_settings()
        self._refresh_summary_cards()
        self._set_current_page(0)

    def _build_ui(self) -> None:
        container = QWidget()
        root_layout = QHBoxLayout(container)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(16)

        nav = QFrame()
        nav.setObjectName("Nav")
        nav.setFixedWidth(220)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(16, 16, 16, 16)
        nav_layout.setSpacing(10)

        app_title = QLabel("Media Manager")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        app_title.setFont(title_font)

        app_subtitle = QLabel("Desktop media workflow")
        app_subtitle.setStyleSheet("color: #94A3B8;")

        nav_layout.addWidget(app_title)
        nav_layout.addWidget(app_subtitle)
        nav_layout.addSpacing(12)
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.organize_button)
        nav_layout.addStretch(1)

        self.stack.addWidget(self._build_home_page())
        self.stack.addWidget(self._build_organize_page())

        root_layout.addWidget(nav)
        root_layout.addWidget(self.stack, 1)
        self.setCentralWidget(container)

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(6)

        title = QLabel("Choose a workspace")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Start in Organize now. The other modules stay visible so the product direction is clear.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #94A3B8;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        organize_card = ModuleCard("Organize", "Sort media from one or more source folders into one target folder.", "Open")
        organize_card.button.clicked.connect(lambda: self._set_current_page(1))

        rename_card = ModuleCard("Rename", "Template-based media renaming will live here.", "Planned", enabled=False)
        duplicates_card = ModuleCard("Duplicates", "Exact duplicate review and keep decisions will live here.", "Planned", enabled=False)
        compare_card = ModuleCard("Compare", "Visual image and video comparison workflows will live here.", "Planned", enabled=False)

        grid.addWidget(organize_card, 0, 0)
        grid.addWidget(rename_card, 0, 1)
        grid.addWidget(duplicates_card, 1, 0)
        grid.addWidget(compare_card, 1, 1)
        layout.addLayout(grid)
        layout.addStretch(1)
        return page

    def _build_organize_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(6)

        title = QLabel("Organize")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Multiple sources. One target. Preview first.")
        subtitle.setStyleSheet("color: #94A3B8;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        outer_layout.addWidget(header)
        outer_layout.addLayout(self._build_summary_row())

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(14)
        controls_layout.addWidget(self._build_sources_group())
        controls_layout.addWidget(self._build_destination_group())
        controls_layout.addWidget(self._build_run_group())
        controls_layout.addStretch(1)

        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setSpacing(10)
        results_layout.addWidget(self.results_summary_label)
        results_layout.addWidget(self.results_table)

        content_layout.addWidget(controls_panel, 4)
        content_layout.addWidget(results_group, 7)

        outer_layout.addLayout(content_layout)
        return page

    def _build_summary_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self.sources_card)
        row.addWidget(self.target_card)
        row.addWidget(self.mode_card)
        row.addWidget(self.run_mode_card)
        return row

    def _build_sources_group(self) -> QGroupBox:
        group = QGroupBox("Source folders")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        import_sets_row = QHBoxLayout()
        self.save_import_set_button = QPushButton("Save set")
        self.load_import_set_button = QPushButton("Load")
        self.delete_import_set_button = QPushButton("Delete")
        self.load_import_set_button.setProperty("variant", "secondary")
        self.delete_import_set_button.setProperty("variant", "secondary")
        self.save_import_set_button.clicked.connect(self._save_import_set)
        self.load_import_set_button.clicked.connect(self._load_import_set)
        self.delete_import_set_button.clicked.connect(self._delete_import_set)
        import_sets_row.addWidget(self.import_set_combo, 1)
        import_sets_row.addWidget(self.save_import_set_button)
        import_sets_row.addWidget(self.load_import_set_button)
        import_sets_row.addWidget(self.delete_import_set_button)

        layout.addLayout(import_sets_row)
        layout.addWidget(self.source_list)
        layout.addWidget(self.source_details_label)

        buttons_row = QHBoxLayout()
        self.add_source_button = QPushButton("Add")
        self.remove_source_button = QPushButton("Remove")
        self.clear_sources_button = QPushButton("Clear")
        self.remove_source_button.setProperty("variant", "secondary")
        self.clear_sources_button.setProperty("variant", "secondary")
        self.add_source_button.clicked.connect(self._add_source_folder)
        self.remove_source_button.clicked.connect(self._remove_selected_sources)
        self.clear_sources_button.clicked.connect(self._clear_sources)

        buttons_row.addWidget(self.add_source_button)
        buttons_row.addWidget(self.remove_source_button)
        buttons_row.addWidget(self.clear_sources_button)
        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)
        return group

    def _build_destination_group(self) -> QGroupBox:
        group = QGroupBox("Target and options")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)
        layout.setColumnStretch(1, 1)

        self.target_browse_button = QPushButton("Browse")
        self.target_browse_button.clicked.connect(self._choose_target_folder)

        self.exiftool_browse_button = QPushButton("Browse")
        self.exiftool_browse_button.setProperty("variant", "secondary")
        self.exiftool_browse_button.clicked.connect(self._choose_exiftool)

        self.open_target_button = QPushButton("Open target")
        self.open_target_button.setProperty("variant", "secondary")
        self.open_target_button.clicked.connect(self._open_target_folder)

        layout.addWidget(QLabel("Target"), 0, 0)
        layout.addWidget(self.target_input, 0, 1)
        layout.addWidget(self.target_browse_button, 0, 2)

        layout.addWidget(QLabel("ExifTool"), 1, 0)
        layout.addWidget(self.exiftool_input, 1, 1)
        layout.addWidget(self.exiftool_browse_button, 1, 2)

        layout.addWidget(QLabel("Template"), 2, 0)
        layout.addWidget(self.template_input, 2, 1, 1, 2)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode"))
        mode_row.addWidget(self.copy_radio)
        mode_row.addWidget(self.move_radio)
        mode_row.addSpacing(16)
        mode_row.addWidget(self.apply_checkbox)
        mode_row.addStretch(1)
        layout.addLayout(mode_row, 3, 0, 1, 3)
        layout.addWidget(self.open_target_button, 4, 2)

        return group

    def _build_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.clear_results_button = QPushButton("Clear results")
        self.clear_results_button.setProperty("variant", "secondary")
        self.run_button.clicked.connect(self._run)
        self.clear_results_button.clicked.connect(self._clear_results)
        row.addWidget(self.run_button)
        row.addWidget(self.clear_results_button)
        row.addStretch(1)
        layout.addLayout(row)
        return group

    def _wire_signals(self) -> None:
        self.home_button.clicked.connect(lambda: self._set_current_page(0))
        self.organize_button.clicked.connect(lambda: self._set_current_page(1))
        self.target_input.textChanged.connect(self._refresh_summary_cards)
        self.apply_checkbox.stateChanged.connect(self._refresh_summary_cards)
        self.copy_radio.toggled.connect(self._refresh_summary_cards)
        self.move_radio.toggled.connect(self._refresh_summary_cards)
        self.source_list.itemSelectionChanged.connect(self._refresh_source_details)

    def _set_current_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        home_active = index == 0
        self.home_button.setProperty("variant", None if home_active else "secondary")
        self.organize_button.setProperty("variant", None if index == 1 else "secondary")
        self.home_button.style().unpolish(self.home_button)
        self.home_button.style().polish(self.home_button)
        self.organize_button.style().unpolish(self.organize_button)
        self.organize_button.style().polish(self.organize_button)

    def _path_from_item(self, item: QListWidgetItem) -> Path:
        return Path(item.data(Qt.ItemDataRole.UserRole))

    def _add_source_item(self, path: Path) -> None:
        normalized = str(path)
        existing = {self._path_from_item(self.source_list.item(index)) for index in range(self.source_list.count())}
        if path in existing:
            return
        item = QListWidgetItem(compact_path_label(path))
        item.setData(Qt.ItemDataRole.UserRole, normalized)
        item.setToolTip(normalized)
        self.source_list.addItem(item)

    def _populate_source_list(self, source_dirs: list[str]) -> None:
        self.source_list.clear()
        for raw_path in source_dirs:
            self._add_source_item(Path(raw_path))
        self._refresh_summary_cards()
        self._refresh_source_details()

    def _refresh_source_details(self) -> None:
        selected_items = self.source_list.selectedItems()
        if not selected_items:
            self.source_details_label.setText("No source folder selected.")
            return
        if len(selected_items) == 1:
            self.source_details_label.setText(str(self._path_from_item(selected_items[0])))
            return
        self.source_details_label.setText(f"{len(selected_items)} source folders selected.")

    def _refresh_summary_cards(self) -> None:
        source_count = self.source_list.count()
        self.sources_card.set_value(f"{source_count} folder" if source_count == 1 else f"{source_count} folders")

        target_text = self.target_input.text().strip()
        if target_text:
            self.target_card.set_value(Path(target_text).name or target_text)
        else:
            self.target_card.set_value("Not set")

        self.mode_card.set_value("Move" if self.move_radio.isChecked() else "Copy")
        self.run_mode_card.set_value("Apply" if self.apply_checkbox.isChecked() else "Preview")

    def _refresh_import_set_combo(self, selected_name: str | None = None) -> None:
        import_sets = list_import_sets(self.app_settings)
        self.import_set_combo.blockSignals(True)
        self.import_set_combo.clear()
        if not import_sets:
            self.import_set_combo.addItem("No saved set", None)
            self.load_import_set_button.setEnabled(False)
            self.delete_import_set_button.setEnabled(False)
        else:
            for item in import_sets:
                self.import_set_combo.addItem(item["name"], item["name"])
            target_name = selected_name or import_sets[0]["name"]
            index = self.import_set_combo.findData(target_name)
            self.import_set_combo.setCurrentIndex(index if index >= 0 else 0)
            self.load_import_set_button.setEnabled(True)
            self.delete_import_set_button.setEnabled(True)
        self.import_set_combo.blockSignals(False)

    def _load_settings(self) -> None:
        self.app_settings = load_app_settings()
        target_text = str(self.app_settings.get("target_dir", "")).strip()
        exiftool_text = str(self.app_settings.get("exiftool_path", "")).strip()
        template_text = str(self.app_settings.get("target_template", DEFAULT_TARGET_TEMPLATE)).strip() or DEFAULT_TARGET_TEMPLATE

        if target_text:
            self.target_input.setText(target_text)
        self.template_input.setText(template_text)
        if exiftool_text and Path(exiftool_text).is_file():
            self.exiftool_input.setText(exiftool_text)
        else:
            auto_path = resolve_exiftool_path()
            if auto_path is not None:
                self.exiftool_input.setText(str(auto_path))
        self._refresh_import_set_combo()

    def _save_settings(self) -> None:
        updated = dict(self.app_settings)
        updated["target_dir"] = self.target_input.text().strip()
        updated["exiftool_path"] = self.exiftool_input.text().strip()
        updated["target_template"] = self.template_input.text().strip() or DEFAULT_TARGET_TEMPLATE
        save_app_settings(updated)
        self.app_settings = updated

    def closeEvent(self, event) -> None:  # pragma: no cover - GUI runtime
        self._save_settings()
        super().closeEvent(event)

    def _set_run_state(self, running: bool) -> None:
        enabled = not running
        for widget in [
            self.run_button,
            self.clear_results_button,
            self.save_import_set_button,
            self.load_import_set_button,
            self.delete_import_set_button,
            self.import_set_combo,
            self.add_source_button,
            self.remove_source_button,
            self.clear_sources_button,
            self.target_input,
            self.exiftool_input,
            self.template_input,
            self.apply_checkbox,
            self.copy_radio,
            self.move_radio,
            self.source_list,
            self.target_browse_button,
            self.exiftool_browse_button,
            self.open_target_button,
            self.home_button,
            self.organize_button,
        ]:
            widget.setEnabled(enabled)
        QApplication.processEvents()

    def _handle_progress(self, message: str) -> None:
        self.results_summary_label.setText(message)
        self.status_bar.showMessage(message)
        QApplication.processEvents()

    def _resize_result_columns(self) -> None:
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

    def _make_result_item(
        self,
        display_value: str,
        tooltip_value: str,
        *,
        emphasize: bool = False,
        center: bool = False,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(display_value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setToolTip(tooltip_value)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if emphasize:
            font = item.font()
            font.setBold(True)
            font.setPointSize(max(font.pointSize(), 14))
            item.setFont(font)
        return item

    def _format_status(self, action: str) -> str:
        return STATUS_LABELS.get(action, action.replace("-", " ").title())

    def _save_import_set(self) -> None:
        source_dirs = [str(path) for path in self._collect_source_dirs()]
        if not source_dirs:
            QMessageBox.information(self, "Save import set", "Add at least one source folder first.")
            return

        target_text = self.target_input.text().strip()
        if not target_text:
            QMessageBox.information(self, "Save import set", "Select a target folder first.")
            return

        name, accepted = QInputDialog.getText(self, "Save import set", "Name")
        if not accepted or not name.strip():
            return

        try:
            self.app_settings = upsert_import_set(
                self.app_settings,
                name,
                source_dirs,
                target_text,
                self.template_input.text().strip() or DEFAULT_TARGET_TEMPLATE,
            )
        except ValueError as exc:
            QMessageBox.information(self, "Save import set", str(exc))
            return

        self._save_settings()
        self._refresh_import_set_combo(selected_name=name.strip())
        self.status_bar.showMessage(f"Saved import set: {name.strip()}")

    def _load_import_set(self) -> None:
        selected_name = self.import_set_combo.currentData()
        if not selected_name:
            return

        item = get_import_set(self.app_settings, str(selected_name))
        if item is None:
            return

        self._populate_source_list(item["source_dirs"])
        self.target_input.setText(item["target_dir"])
        self.template_input.setText(item["target_template"])
        self._refresh_summary_cards()
        self.status_bar.showMessage(f"Loaded import set: {item['name']}")

    def _delete_import_set(self) -> None:
        selected_name = self.import_set_combo.currentData()
        if not selected_name:
            return

        reply = QMessageBox.question(
            self,
            "Delete import set",
            f"Delete '{selected_name}'?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.app_settings = remove_import_set(self.app_settings, str(selected_name))
        self._save_settings()
        self._refresh_import_set_combo()
        self.status_bar.showMessage(f"Deleted import set: {selected_name}")

    def _add_source_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not selected:
            return

        path = Path(selected)
        self._add_source_item(path)
        self.status_bar.showMessage(f"Added source folder: {path}")
        self._refresh_summary_cards()

    def _remove_selected_sources(self) -> None:
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))
        self.status_bar.showMessage("Selected source folders removed")
        self._refresh_summary_cards()
        self._refresh_source_details()

    def _clear_sources(self) -> None:
        self.source_list.clear()
        self.status_bar.showMessage("Source folder list cleared")
        self._refresh_summary_cards()
        self._refresh_source_details()

    def _choose_target_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select target folder")
        if selected:
            self.target_input.setText(str(Path(selected)))
            self._refresh_summary_cards()

    def _choose_exiftool(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Select ExifTool executable",
            filter="Executable (*.exe);;All files (*.*)",
        )
        if selected:
            self.exiftool_input.setText(str(Path(selected)))
            self._save_settings()

    def _open_target_folder(self) -> None:
        target_text = self.target_input.text().strip()
        if not target_text:
            QMessageBox.information(self, "Open target", "Set a target folder first.")
            return
        target_dir = Path(target_text)
        if not target_dir.exists():
            QMessageBox.information(self, "Open target", "The target folder does not exist yet.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target_dir)))

    def _clear_results(self) -> None:
        self.results_table.setRowCount(0)
        self.results_summary_label.setText("No run yet.")
        self.status_bar.showMessage("Results cleared")

    def _collect_source_dirs(self) -> list[Path]:
        return [self._path_from_item(self.source_list.item(index)) for index in range(self.source_list.count())]

    def _run(self) -> None:
        source_dirs = self._collect_source_dirs()
        target_text = self.target_input.text().strip()
        exiftool_text = self.exiftool_input.text().strip()

        if not source_dirs:
            QMessageBox.critical(self, "Error", "Please add at least one source folder.")
            return

        invalid_sources = [path for path in source_dirs if not path.is_dir()]
        if invalid_sources:
            QMessageBox.critical(
                self,
                "Error",
                "The following source folders are invalid:\n- " + "\n- ".join(str(path) for path in invalid_sources),
            )
            return

        if not target_text:
            QMessageBox.critical(self, "Error", "Please select a target folder.")
            return

        target_dir = Path(target_text)
        target_dir.mkdir(parents=True, exist_ok=True)
        exiftool_path = Path(exiftool_text) if exiftool_text else None

        config = SortConfig(
            source_dirs=source_dirs,
            target_dir=target_dir,
            target_template=self.template_input.text().strip() or DEFAULT_TARGET_TEMPLATE,
            dry_run=not self.apply_checkbox.isChecked(),
            mode="move" if self.move_radio.isChecked() else "copy",
            exiftool_path=exiftool_path,
        )

        self._save_settings()
        self.results_table.setRowCount(0)
        self.results_summary_label.setText("Preparing organizer run ...")
        self.status_bar.showMessage("Preparing organizer run ...")
        self._set_run_state(True)

        try:
            results = organize_media(config, progress_callback=self._handle_progress)
        except Exception as exc:  # pragma: no cover - GUI fallback
            QMessageBox.critical(self, "Error", str(exc))
            self.results_summary_label.setText("An error occurred.")
            self.status_bar.showMessage("An error occurred")
            return
        finally:
            self._set_run_state(False)

        self.results_table.setRowCount(len(results.entries))
        for row_index, entry in enumerate(results.entries):
            target_value = "-"
            target_tooltip = "-"
            if entry.target is not None:
                target_value = relative_target_folder(entry.target, target_dir)
                target_tooltip = str(entry.target)

            values = [
                (self._format_status(entry.action), entry.action, True, True),
                (entry.source.name, str(entry.source), False, False),
                (entry.source.parent.name or str(entry.source.parent), str(entry.source.parent), False, False),
                (target_value, target_tooltip, False, False),
                (entry.reason or "-", entry.reason or "-", False, False),
            ]
            for column_index, (display_value, tooltip_value, emphasize, center) in enumerate(values):
                item = self._make_result_item(display_value, tooltip_value, emphasize=emphasize, center=center)
                self.results_table.setItem(row_index, column_index, item)

        self._resize_result_columns()
        mode_label = "Apply" if self.apply_checkbox.isChecked() else "Preview"
        self.results_summary_label.setText(
            f"{mode_label} finished — {results.processed} file(s), {results.organized} action(s), {results.errors} error(s)."
        )
        self.status_bar.showMessage(
            f"Processed: {results.processed} | Planned/Executed: {results.organized} | "
            f"Skipped: {results.skipped} | Errors: {results.errors}"
        )


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    window = MediaManagerWindow()
    window.show()
    return app.exec()
