from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QFileDialog,
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
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSplitter,
)

from .sorter import SortConfig, organize_media


APP_STYLESHEET = """
QMainWindow {
    background: #111827;
}
QWidget {
    color: #E5E7EB;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #374151;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 16px;
    background: #1F2937;
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
    border: 1px solid #374151;
    border-radius: 10px;
    padding: 8px;
    selection-background-color: #2563EB;
}
QPushButton {
    background: #2563EB;
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
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
    background: #374151;
}
QPushButton[variant="secondary"]:hover {
    background: #4B5563;
}
QHeaderView::section {
    background: #1F2937;
    color: #F9FAFB;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #374151;
}
QStatusBar {
    background: #111827;
    border-top: 1px solid #1F2937;
}
"""


class MediaManagerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Media Manager")
        self.resize(1180, 760)
        self.setMinimumSize(980, 680)

        self.target_input = QLineEdit()
        self.exiftool_input = QLineEdit()
        self.template_input = QLineEdit("{year}/{month}")
        self.apply_checkbox = QCheckBox("Apply changes for real")

        self.source_list = QListWidget()
        self.source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.copy_radio = QRadioButton("Copy")
        self.move_radio = QRadioButton("Move")
        self.copy_radio.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.copy_radio)
        self.mode_group.addButton(self.move_radio)

        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(["Status", "Source", "Target", "Details"])
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget()
        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(18, 18, 18, 18)
        outer_layout.setSpacing(16)

        title = QLabel("Media Manager")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel(
            "Desktop foundation for organizing photos and videos with multiple source folders and one target folder."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #9CA3AF;")

        outer_layout.addWidget(title)
        outer_layout.addWidget(subtitle)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(14)

        controls_layout.addWidget(self._build_sources_group())
        controls_layout.addWidget(self._build_destination_group())
        controls_layout.addWidget(self._build_run_group())

        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.addWidget(self.results_table)

        splitter.addWidget(controls_panel)
        splitter.addWidget(results_group)
        splitter.setSizes([320, 360])

        outer_layout.addWidget(splitter)
        self.setCentralWidget(container)

    def _build_sources_group(self) -> QGroupBox:
        group = QGroupBox("Source folders")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        hint = QLabel("Add one or more source folders. Duplicate paths are ignored.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #9CA3AF;")
        layout.addWidget(hint)
        layout.addWidget(self.source_list)

        buttons_row = QHBoxLayout()
        add_button = QPushButton("Add folder")
        remove_button = QPushButton("Remove selected")
        clear_button = QPushButton("Clear all")
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
        group = QGroupBox("Target and processing")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)
        layout.setColumnStretch(1, 1)

        target_button = QPushButton("Browse")
        target_button.clicked.connect(self._choose_target_folder)

        exiftool_button = QPushButton("Browse")
        exiftool_button.setProperty("variant", "secondary")
        exiftool_button.clicked.connect(self._choose_exiftool)

        layout.addWidget(QLabel("Target folder"), 0, 0)
        layout.addWidget(self.target_input, 0, 1)
        layout.addWidget(target_button, 0, 2)

        layout.addWidget(QLabel("ExifTool path"), 1, 0)
        layout.addWidget(self.exiftool_input, 1, 1)
        layout.addWidget(exiftool_button, 1, 2)

        layout.addWidget(QLabel("Target template"), 2, 0)
        layout.addWidget(self.template_input, 2, 1, 1, 2)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode"))
        mode_row.addWidget(self.copy_radio)
        mode_row.addWidget(self.move_radio)
        mode_row.addSpacing(20)
        mode_row.addWidget(self.apply_checkbox)
        mode_row.addStretch(1)
        layout.addLayout(mode_row, 3, 0, 1, 3)

        return group

    def _build_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)

        info = QLabel(
            "Use preview first. Only enable real apply mode once the target structure looks correct."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #9CA3AF;")
        layout.addWidget(info)

        row = QHBoxLayout()
        preview_button = QPushButton("Preview / Run")
        clear_button = QPushButton("Clear results")
        clear_button.setProperty("variant", "secondary")
        preview_button.clicked.connect(self._run)
        clear_button.clicked.connect(self._clear_results)
        row.addWidget(preview_button)
        row.addWidget(clear_button)
        row.addStretch(1)
        layout.addLayout(row)
        return group

    def _add_source_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not selected:
            return
        normalized = str(Path(selected))
        existing = {self.source_list.item(index).text() for index in range(self.source_list.count())}
        if normalized not in existing:
            self.source_list.addItem(QListWidgetItem(normalized))
            self.status_bar.showMessage(f"Added source folder: {normalized}")

    def _remove_selected_sources(self) -> None:
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))
        self.status_bar.showMessage("Selected source folders removed")

    def _clear_sources(self) -> None:
        self.source_list.clear()
        self.status_bar.showMessage("Source folder list cleared")

    def _choose_target_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select target folder")
        if selected:
            self.target_input.setText(str(Path(selected)))

    def _choose_exiftool(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Select ExifTool executable",
            filter="Executable (*.exe);;All files (*.*)",
        )
        if selected:
            self.exiftool_input.setText(str(Path(selected)))

    def _clear_results(self) -> None:
        self.results_table.setRowCount(0)
        self.status_bar.showMessage("Results cleared")

    def _collect_source_dirs(self) -> list[Path]:
        return [Path(self.source_list.item(index).text()) for index in range(self.source_list.count())]

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

        self._clear_results()
        self.results_table.setRowCount(len(results.entries))
        for row_index, entry in enumerate(results.entries):
            values = [
                entry.action,
                str(entry.source),
                str(entry.target) if entry.target is not None else "-",
                entry.reason or "-",
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.results_table.setItem(row_index, column_index, item)

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
