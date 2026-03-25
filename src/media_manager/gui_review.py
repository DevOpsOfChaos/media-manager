from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from .duplicate_review import (
    count_marked_for_removal,
    default_keep_path,
    newest_keep_path,
    oldest_keep_path,
    paths_marked_for_removal,
)
from .duplicates import DuplicateScanConfig, ExactDuplicateGroup, scan_exact_duplicates
from .gui import APP_STYLESHEET, MediaManagerWindow as BaseMediaManagerWindow, format_file_size


class MediaManagerWindow(BaseMediaManagerWindow):
    def __init__(self) -> None:
        super().__init__()
        self.duplicate_groups: list[ExactDuplicateGroup] = []
        self.duplicate_keep_paths: dict[int, Path] = {}
        self.duplicate_row_map: list[tuple[int, Path]] = []
        self._install_duplicate_review_panel()
        self._set_duplicate_card_titles()
        self._refresh_duplicate_review_controls()

    def _set_duplicate_card_titles(self) -> None:
        self._set_card_title(self.duplicates_files_card, "Files in groups")
        self._set_card_title(self.duplicates_extra_card, "Marked remove")

    def _set_card_title(self, card, title: str) -> None:
        title_widget = card.layout().itemAt(0).widget()
        if isinstance(title_widget, QLabel):
            title_widget.setText(title)

    def _install_duplicate_review_panel(self) -> None:
        review_group = QGroupBox("Review and apply")
        review_layout = QVBoxLayout(review_group)
        review_layout.setSpacing(10)

        keep_row = QHBoxLayout()
        self.duplicates_keep_selected_button = QPushButton("Keep selected")
        self.duplicates_keep_newest_button = QPushButton("Keep newest")
        self.duplicates_keep_oldest_button = QPushButton("Keep oldest")
        self.duplicates_reset_group_button = QPushButton("Reset group")
        for button in [
            self.duplicates_keep_selected_button,
            self.duplicates_keep_newest_button,
            self.duplicates_keep_oldest_button,
            self.duplicates_reset_group_button,
        ]:
            button.setProperty("variant", "secondary")
        self.duplicates_keep_selected_button.clicked.connect(self._keep_selected_duplicate)
        self.duplicates_keep_newest_button.clicked.connect(self._keep_newest_duplicate)
        self.duplicates_keep_oldest_button.clicked.connect(self._keep_oldest_duplicate)
        self.duplicates_reset_group_button.clicked.connect(self._reset_selected_duplicate_group)
        keep_row.addWidget(self.duplicates_keep_selected_button)
        keep_row.addWidget(self.duplicates_keep_newest_button)
        keep_row.addWidget(self.duplicates_keep_oldest_button)
        keep_row.addWidget(self.duplicates_reset_group_button)
        keep_row.addStretch(1)
        review_layout.addLayout(keep_row)

        apply_row = QHBoxLayout()
        self.duplicates_open_folder_button = QPushButton("Open selected folder")
        self.duplicates_apply_review_button = QPushButton("Send marked files to Recycle Bin")
        self.duplicates_open_folder_button.setProperty("variant", "secondary")
        self.duplicates_apply_review_button.setProperty("variant", "secondary")
        self.duplicates_open_folder_button.clicked.connect(self._open_selected_duplicate_folder)
        self.duplicates_apply_review_button.clicked.connect(self._apply_duplicate_review_to_trash)
        apply_row.addWidget(self.duplicates_open_folder_button)
        apply_row.addWidget(self.duplicates_apply_review_button)
        apply_row.addStretch(1)
        review_layout.addLayout(apply_row)

        self.duplicates_review_hint_label = QLabel("Run a duplicate scan to start review actions.")
        self.duplicates_review_hint_label.setWordWrap(True)
        self.duplicates_review_hint_label.setStyleSheet("color: #AFC1D9;")
        review_layout.addWidget(self.duplicates_review_hint_label)

        self.duplicates_results_table.setColumnCount(6)
        self.duplicates_results_table.setHorizontalHeaderLabels(["Group", "Decision", "File", "Folder", "Size", "Notes"])
        self.duplicates_results_table.itemSelectionChanged.connect(self._refresh_duplicate_selection_hint)

        duplicates_page = self.stack.widget(4)
        outer_layout = duplicates_page.layout()
        content_layout = outer_layout.itemAt(2).layout()
        controls_panel = content_layout.itemAt(0).widget()
        controls_layout = controls_panel.layout()
        controls_layout.insertWidget(2, review_group)
        self._resize_result_columns(self.duplicates_results_table)

    def _selected_duplicate_context(self) -> tuple[int, Path] | None:
        selection_model = self.duplicates_results_table.selectionModel()
        if selection_model is None:
            return None
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        if row < 0 or row >= len(self.duplicate_row_map):
            return None
        return self.duplicate_row_map[row]

    def _count_marked_duplicates(self) -> int:
        total = 0
        for group_index, group in enumerate(self.duplicate_groups):
            keep_path = self.duplicate_keep_paths.get(group_index)
            if keep_path is None:
                continue
            total += count_marked_for_removal(group.files, keep_path)
        return total

    def _refresh_duplicates_summary_cards(
        self,
        groups: int | None = None,
        duplicate_files: int | None = None,
        extra_duplicates: int | None = None,
    ) -> None:
        super()._refresh_duplicates_summary_cards(groups, duplicate_files, extra_duplicates)
        if hasattr(self, "duplicates_files_card"):
            self._set_duplicate_card_titles()

    def _set_run_state(self, running: bool) -> None:
        super()._set_run_state(running)
        if hasattr(self, "duplicates_apply_review_button"):
            self._refresh_duplicate_review_controls(is_running=running)

    def _refresh_duplicate_selection_hint(self) -> None:
        context = self._selected_duplicate_context()
        if context is None:
            if self.duplicate_groups:
                self.duplicates_review_hint_label.setText(
                    f"Review loaded. Marked for removal: {self._count_marked_duplicates()} file(s)."
                )
            else:
                self.duplicates_review_hint_label.setText("Run a duplicate scan to start review actions.")
            self._refresh_duplicate_review_controls()
            return

        group_index, selected_path = context
        keep_path = self.duplicate_keep_paths.get(group_index)
        if keep_path is None:
            self.duplicates_review_hint_label.setText("No keep decision for this group yet.")
        else:
            remove_count = count_marked_for_removal(self.duplicate_groups[group_index].files, keep_path)
            decision = "KEEP" if selected_path == keep_path else "REMOVE"
            self.duplicates_review_hint_label.setText(
                f"Group {group_index + 1}: selected = {selected_path.name} ({decision}) | keep = {keep_path.name} | remove = {remove_count}"
            )
        self._refresh_duplicate_review_controls()

    def _refresh_duplicate_review_controls(self, *, is_running: bool = False) -> None:
        if not hasattr(self, "duplicates_keep_selected_button"):
            return
        has_selection = self._selected_duplicate_context() is not None
        has_groups = bool(self.duplicate_groups)
        has_marked = self._count_marked_duplicates() > 0
        self.duplicates_keep_selected_button.setEnabled(has_selection and not is_running)
        self.duplicates_keep_newest_button.setEnabled(has_selection and not is_running)
        self.duplicates_keep_oldest_button.setEnabled(has_selection and not is_running)
        self.duplicates_reset_group_button.setEnabled(has_selection and not is_running)
        self.duplicates_open_folder_button.setEnabled(has_selection and not is_running)
        self.duplicates_apply_review_button.setEnabled(has_groups and has_marked and not is_running)

    def _set_duplicate_keep_path(self, group_index: int, keep_path: Path) -> None:
        self.duplicate_keep_paths[group_index] = keep_path
        self._populate_duplicates_results_table()
        self._refresh_duplicate_selection_hint()

    def _keep_selected_duplicate(self) -> None:
        context = self._selected_duplicate_context()
        if context is None:
            return
        group_index, selected_path = context
        self._set_duplicate_keep_path(group_index, selected_path)
        self.status_bar.showMessage(f"Group {group_index + 1}: keep {selected_path.name}")

    def _keep_newest_duplicate(self) -> None:
        context = self._selected_duplicate_context()
        if context is None:
            return
        group_index, _ = context
        keep_path = newest_keep_path(self.duplicate_groups[group_index].files)
        self._set_duplicate_keep_path(group_index, keep_path)
        self.status_bar.showMessage(f"Group {group_index + 1}: keep newest {keep_path.name}")

    def _keep_oldest_duplicate(self) -> None:
        context = self._selected_duplicate_context()
        if context is None:
            return
        group_index, _ = context
        keep_path = oldest_keep_path(self.duplicate_groups[group_index].files)
        self._set_duplicate_keep_path(group_index, keep_path)
        self.status_bar.showMessage(f"Group {group_index + 1}: keep oldest {keep_path.name}")

    def _reset_selected_duplicate_group(self) -> None:
        context = self._selected_duplicate_context()
        if context is None:
            return
        group_index, _ = context
        keep_path = default_keep_path(self.duplicate_groups[group_index].files)
        self._set_duplicate_keep_path(group_index, keep_path)
        self.status_bar.showMessage(f"Group {group_index + 1}: reset keep decision")

    def _open_selected_duplicate_folder(self) -> None:
        context = self._selected_duplicate_context()
        if context is None:
            return
        _, selected_path = context
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(selected_path.parent)))

    def _apply_duplicate_review_to_trash(self) -> None:
        marked_paths: list[Path] = []
        for group_index, group in enumerate(self.duplicate_groups):
            keep_path = self.duplicate_keep_paths.get(group_index)
            if keep_path is None:
                continue
            marked_paths.extend(paths_marked_for_removal(group.files, keep_path))

        if not marked_paths:
            QMessageBox.information(self, "Duplicates", "No files are marked for removal.")
            return

        reply = QMessageBox.question(
            self,
            "Send duplicates to Recycle Bin",
            f"Send {len(marked_paths)} marked duplicate file(s) to the Recycle Bin?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            from send2trash import send2trash
        except ImportError:
            QMessageBox.critical(self, "Duplicates", "send2trash is not installed in the current environment.")
            return

        removed = 0
        errors = 0
        for path in marked_paths:
            try:
                send2trash(str(path))
                removed += 1
            except Exception:
                errors += 1

        self.duplicates_review_hint_label.setText(
            f"Recycle Bin action finished. Removed: {removed} | Errors: {errors}"
        )
        self.status_bar.showMessage(f"Duplicate review applied | Removed: {removed} | Errors: {errors}")
        self._run_duplicates()

    def _populate_duplicates_results_table(self) -> None:
        self.duplicate_row_map = []
        total_rows = sum(len(group.files) for group in self.duplicate_groups)
        self.duplicates_results_table.setRowCount(total_rows)
        row_index = 0
        for group_index, group in enumerate(self.duplicate_groups):
            keep_path = self.duplicate_keep_paths.get(group_index, default_keep_path(group.files))
            note = (
                f"{len(group.files)} files | same name: {'yes' if group.same_name else 'no'} | same suffix: {'yes' if group.same_suffix else 'no'}"
            )
            size_label = format_file_size(group.file_size)
            for path in group.files:
                decision = "Keep" if path == keep_path else "Remove"
                values = [
                    (str(group_index + 1), str(group_index + 1), True),
                    (decision, decision, True),
                    (path.name, str(path), False),
                    (path.parent.name or str(path.parent), str(path.parent), False),
                    (size_label, str(group.file_size), True),
                    (note, note, False),
                ]
                for column_index, (display_value, tooltip_value, center) in enumerate(values):
                    self.duplicates_results_table.setItem(
                        row_index,
                        column_index,
                        self._make_result_item(display_value, tooltip_value, center=center),
                    )
                self.duplicate_row_map.append((group_index, path))
                row_index += 1
        self._resize_result_columns(self.duplicates_results_table)
        self._refresh_duplicates_summary_cards(
            groups=len(self.duplicate_groups),
            duplicate_files=sum(len(group.files) for group in self.duplicate_groups),
            extra_duplicates=self._count_marked_duplicates(),
        )
        self._refresh_duplicate_review_controls()

    def _duplicates_clear_results(self) -> None:
        self.duplicate_groups = []
        self.duplicate_keep_paths = {}
        self.duplicate_row_map = []
        self.duplicates_results_table.setRowCount(0)
        self._resize_result_columns(self.duplicates_results_table)
        self._refresh_duplicates_summary_cards(groups=0, duplicate_files=0, extra_duplicates=0)
        self.duplicates_review_hint_label.setText("Run a duplicate scan to start review actions.")
        self._refresh_duplicate_review_controls()
        self.status_bar.showMessage("Results cleared")

    def _run_duplicates(self) -> None:
        source_dirs = self._collect_paths(self.duplicates_source_list)
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

        config = DuplicateScanConfig(source_dirs=source_dirs)
        self.duplicates_results_table.setRowCount(0)
        self._resize_result_columns(self.duplicates_results_table)
        self._refresh_duplicates_summary_cards(groups=0, duplicate_files=0, extra_duplicates=0)
        self.status_bar.showMessage("Preparing duplicate scan ...")
        self._set_run_state(True)
        try:
            result = scan_exact_duplicates(config, progress_callback=self._handle_progress)
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            self.status_bar.showMessage("An error occurred")
            return
        finally:
            self._set_run_state(False)

        self.duplicate_groups = result.exact_groups
        self.duplicate_keep_paths = {
            index: default_keep_path(group.files)
            for index, group in enumerate(self.duplicate_groups)
        }
        self._populate_duplicates_results_table()
        if self.duplicate_groups:
            self.duplicates_review_hint_label.setText(
                "Review loaded. Keep one file per group and send the marked files to the Recycle Bin when ready."
            )
        else:
            self.duplicates_review_hint_label.setText("No exact duplicate groups found.")

        self._set_workflow_step_status("duplicates", f"Done ({len(result.exact_groups)} groups)")
        self.workflow_current_step = "Organize"
        self._refresh_workflow_summary_cards()
        self.status_bar.showMessage(
            f"Duplicate scan finished | Scanned: {result.scanned_files} | Exact groups: {len(result.exact_groups)} | Files in groups: {sum(len(group.files) for group in result.exact_groups)} | Marked remove: {self._count_marked_duplicates()} | Errors: {result.errors}"
        )


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = MediaManagerWindow()
    window.show()
    return app.exec()
