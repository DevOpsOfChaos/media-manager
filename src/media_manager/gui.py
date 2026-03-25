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
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
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
from .settings import load_app_settings, save_app_settings
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
QLineEdit, QListWidget, QTableWidget {
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
        self.resize(1280, 800)
        self.setMinimumSize(1080, 720)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target folder")
        self.exiftool_input = QLineEdit()
        self.exiftool_input.setPlaceholderText("Auto-detect when empty")
        self.template_input = QLineEdit("{year}/{month}")
        self.apply_checkbox = QCheckBox("Apply")

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
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

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
        content_layout.addWidget(results_group, 6)

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
        layout.addWidget(self.source_list)
        layout.addWidget(self.source_details_label)

        buttons_row = QHBoxLayout()
        add_button = QPushButton("Add")
        remove_button = QPushButton("Remove")
        clear_button = QPushButton("Clear")
        remove_button.setProperty("variant", "secondary")
        clear_button.setProperty("variant", "secondary")
        add_button.clicked.connect(self._add_source_folder)
        remove_button.clicked.connect(self._remove_selected_sources)
        clear_button.clicked.connect(self._clear_sources)

        buttons_row.addWidget(add_button)
        buttons_row.addWidget(remove_button)
        buttons_row.addWidget(clear_button)
        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)
        return group

    def _build_destination_group(self) -> QGroupBox:
        group = QGroupBox("Target and options")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)
        layout.setColumnStretch(1, 1)

        target_button = QPushButton("Browse")
        target_button.clicked.connect(self._choose_target_folder)

        exiftool_button = QPushButton("Browse")
        exiftool_button.setProperty("variant", "secondary")
        exiftool_button.clicked.connect(self._choose_exiftool)

        open_target_button = QPushButton("Open target")
        open_target_button.setProperty("variant", "secondary")
        open_target_button.clicked.connect(self._open_target_folder)

        layout.addWidget(QLabel("Target"), 0, 0)
        layout.addWidget(self.target_input, 0, 1)
        layout.addWidget(target_button, 0, 2)

        layout.addWidget(QLabel("ExifTool"), 1, 0)
        layout.addWidget(self.exiftool_input, 1, 1)
        layout.addWidget(exiftool_button, 1, 2)

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
        layout.addWidget(open_target_button, 4, 2)

        return group

    def _build_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        preview_button = QPushButton("Run")
        clear_button = QPushButton("Clear results")
        clear_button.setProperty("variant", "secondary")
        preview_button.clicked.connect(self._run)
        clear_button.clicked.connect(self._clear_results)
        row.addWidget(preview_button)
        row.addWidget(clear_button)
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

    def _load_settings(self) -> None:
        settings = load_app_settings()
        target_text = settings.get("target_dir", "")
        exiftool_text = settings.get("exiftool_path", "")
        template_text = settings.get("target_template", "{year}/{month}")

        if target_text:
            self.target_input.setText(target_text)
        if template_text:
            self.template_input.setText(template_text)
        if exiftool_text and Path(exiftool_text).is_file():
            self.exiftool_input.setText(exiftool_text)
        else:
            auto_path = resolve_exiftool_path()
            if auto_path is not None:
                self.exiftool_input.setText(str(auto_path))

    def _save_settings(self) -> None:
        save_app_settings(
            {
                "target_dir": self.target_input.text().strip(),
                "exiftool_path": self.exiftool_input.text().strip(),
                "target_template": self.template_input.text().strip() or "{year}/{month}",
            }
        )

    def closeEvent(self, event) -> None:  # pragma: no cover - GUI runtime
        self._save_settings()
        super().closeEvent(event)

    def _add_source_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not selected:
            return

        path = Path(selected)
        normalized = str(path)
        existing = {self._path_from_item(self.source_list.item(index)) for index in range(self.source_list.count())}
        if path not in existing:
            item = QListWidgetItem(compact_path_label(path))
            item.setData(Qt.ItemDataRole.UserRole, normalized)
            item.setToolTip(normalized)
            self.source_list.addItem(item)
            self.status_bar.showMessage(f"Added source folder: {normalized}")
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
            target_template=self.template_input.text().strip() or "{year}/{month}",
            dry_run=not self.apply_checkbox.isChecked(),
            mode="move" if self.move_radio.isChecked() else "copy",
            exiftool_path=exiftool_path,
        )

        try:
            self.status_bar.showMessage("Processing ...")
            QApplication.processEvents()
            results = organize_media(config)
        except Exception as exc:  # pragma: no cover - GUI fallback
            QMessageBox.critical(self, "Error", str(exc))
            self.status_bar.showMessage("An error occurred")
            return

        self.results_table.setRowCount(len(results.entries))
        for row_index, entry in enumerate(results.entries):
            target_value = "-"
            target_tooltip = "-"
            if entry.target is not None:
                target_value = relative_target_folder(entry.target, target_dir)
                target_tooltip = str(entry.target)

            values = [
                (entry.action, entry.action),
                (entry.source.name, str(entry.source)),
                (entry.source.parent.name or str(entry.source.parent), str(entry.source.parent)),
                (target_value, target_tooltip),
                (entry.reason or "-", entry.reason or "-"),
            ]
            for column_index, (display_value, tooltip_value) in enumerate(values):
                item = QTableWidgetItem(display_value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(tooltip_value)
                self.results_table.setItem(row_index, column_index, item)

        mode_label = "Apply" if self.apply_checkbox.isChecked() else "Preview"
        self.results_summary_label.setText(
            f"{mode_label} finished — {results.processed} file(s), {results.organized} action(s), {results.errors} error(s)."
        )
        self.status_bar.showMessage(
            f"Processed: {results.processed} | Planned/Executed: {results.organized} | "
            f"Skipped: {results.skipped} | Errors: {results.errors}"
        )
        self._save_settings()


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    window = MediaManagerWindow()
    window.show()
    return app.exec()
