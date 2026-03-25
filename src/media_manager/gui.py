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
    border: 1px solid #334155;
}
QPushButton[variant="secondary"]:hover {
    background: #273449;
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


class MediaManagerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Media Manager")
        self.resize(1240, 780)
        self.setMinimumSize(1020, 700)

        self.target_input = QLineEdit()
        self.exiftool_input = QLineEdit()
        self.template_input = QLineEdit("{year}/{month}")
        self.apply_checkbox = QCheckBox("Apply changes for real")

        self.source_list = QListWidget()
        self.source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.source_list.setAlternatingRowColors(True)

        self.copy_radio = QRadioButton("Copy")
        self.move_radio = QRadioButton("Move")
        self.copy_radio.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.copy_radio)
        self.mode_group.addButton(self.move_radio)

        self.results_summary_label = QLabel("No run executed yet.")
        self.results_summary_label.setWordWrap(True)
        self.results_summary_label.setStyleSheet("color: #94A3B8;")

        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(["Status", "Source", "Target", "Details"])
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.sources_card = StatCard("Source folders", "0")
        self.target_card = StatCard("Target folder", "Not set")
        self.mode_card = StatCard("File mode", "Copy")
        self.run_mode_card = StatCard("Run mode", "Preview")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self._build_ui()
        self._wire_signals()
        self._refresh_summary_cards()

    def _build_ui(self) -> None:
        container = QWidget()
        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(18, 18, 18, 18)
        outer_layout.setSpacing(16)

        outer_layout.addWidget(self._build_header_card())
        outer_layout.addLayout(self._build_summary_row())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

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

        splitter.addWidget(controls_panel)
        splitter.addWidget(results_group)
        splitter.setSizes([430, 760])

        outer_layout.addWidget(splitter)
        self.setCentralWidget(container)

    def _build_header_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(6)

        title = QLabel("Media Manager")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel(
            "Organizer baseline for photos and videos with multiple source folders, one target folder, and safer preview-first execution."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #94A3B8;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return card

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

        hint = QLabel(
            "Add one or more source folders. The organizer will deduplicate repeated path input before processing files."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #94A3B8;")
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

        open_target_button = QPushButton("Open target")
        open_target_button.setProperty("variant", "secondary")
        open_target_button.clicked.connect(self._open_target_folder)

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
        layout.addWidget(open_target_button, 4, 2)

        return group

    def _build_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)

        info = QLabel(
            "Use preview first. Only enable real apply mode once the target structure looks correct."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #94A3B8;")
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

    def _wire_signals(self) -> None:
        self.target_input.textChanged.connect(self._refresh_summary_cards)
        self.apply_checkbox.stateChanged.connect(self._refresh_summary_cards)
        self.copy_radio.toggled.connect(self._refresh_summary_cards)
        self.move_radio.toggled.connect(self._refresh_summary_cards)

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

    def _add_source_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not selected:
            return
        normalized = str(Path(selected))
        existing = {self.source_list.item(index).text() for index in range(self.source_list.count())}
        if normalized not in existing:
            self.source_list.addItem(QListWidgetItem(normalized))
            self.status_bar.showMessage(f"Added source folder: {normalized}")
            self._refresh_summary_cards()

    def _remove_selected_sources(self) -> None:
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))
        self.status_bar.showMessage("Selected source folders removed")
        self._refresh_summary_cards()

    def _clear_sources(self) -> None:
        self.source_list.clear()
        self.status_bar.showMessage("Source folder list cleared")
        self._refresh_summary_cards()

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
        self.results_summary_label.setText("No run executed yet.")
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

        self.results_summary_label.setText(
            f"Run finished with {results.processed} processed file(s), {results.organized} planned/executed action(s), and {results.errors} error(s)."
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
