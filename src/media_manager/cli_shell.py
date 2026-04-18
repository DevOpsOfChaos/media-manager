from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core.workflows import (
    build_gui_shell_model,
    build_profile_bound_workflow_form_model,
    build_preset_bound_workflow_form_model,
    build_shell_command_preview_for_problem,
    build_shell_command_preview_for_workflow,
    build_workflow_form_model,
    build_workflow_launcher_model,
    list_workflow_form_models,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager shell",
        description="Launch the new GUI shell scaffold or inspect workflow models in headless mode.",
    )
    parser.add_argument(
        "--dump-model",
        action="store_true",
        help="Print the GUI shell model as JSON without launching the desktop window.",
    )
    parser.add_argument(
        "--dump-forms",
        action="store_true",
        help="Print all workflow form models as JSON without launching the desktop window.",
    )
    parser.add_argument(
        "--dump-launchers",
        action="store_true",
        help="Print preset/profile launcher cards as JSON without launching the desktop window.",
    )
    parser.add_argument(
        "--profiles-dir",
        type=Path,
        help="Optional directory containing workflow profile JSON files.",
    )
    parser.add_argument(
        "--preview-workflow",
        help="Print the example command preview for a workflow without launching the desktop window.",
    )
    parser.add_argument(
        "--preview-problem",
        help="Print the recommended command preview for a workflow problem without launching the desktop window.",
    )
    parser.add_argument(
        "--preview-form",
        help="Print one workflow form model as JSON without launching the desktop window.",
    )
    parser.add_argument(
        "--preview-preset-form",
        help="Print one preset-bound workflow form model as JSON without launching the desktop window.",
    )
    parser.add_argument(
        "--preview-profile-form",
        type=Path,
        help="Print one profile-bound workflow form model as JSON without launching the desktop window.",
    )
    parser.add_argument(
        "--preview-profile-command",
        type=Path,
        help="Print the command preview for a workflow profile without launching the desktop window.",
    )
    return parser


def _launch_gui_shell() -> int:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QLabel,
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QMessageBox,
            QPlainTextEdit,
            QPushButton,
            QSplitter,
            QVBoxLayout,
            QWidget,
        )
    except Exception:
        print(
            "The GUI shell requires the optional GUI dependencies. "
            'Install them with: python -m pip install -e ".[gui]"',
            file=sys.stderr,
        )
        return 2

    model = build_gui_shell_model()

    class WorkflowShellWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Media Manager Shell")
            self.resize(1080, 680)

            container = QWidget(self)
            layout = QVBoxLayout(container)

            title = QLabel("Media Manager Workflow Shell")
            title.setStyleSheet("font-size: 22px; font-weight: 600;")
            subtitle = QLabel(
                "A lightweight new shell over the rebuilt CLI workflows. "
                "Review workflows, problems, forms, and example commands from one place."
            )
            subtitle.setWordWrap(True)

            splitter = QSplitter(Qt.Horizontal)

            self.workflow_list = QListWidget()
            self.problem_list = QListWidget()

            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            left_layout.addWidget(QLabel("Workflows"))
            left_layout.addWidget(self.workflow_list)
            left_layout.addWidget(QLabel("Problems"))
            left_layout.addWidget(self.problem_list)

            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            self.title_label = QLabel("Select a workflow or problem")
            self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
            self.summary_box = QPlainTextEdit()
            self.summary_box.setReadOnly(True)
            self.command_box = QPlainTextEdit()
            self.command_box.setReadOnly(True)
            copy_button = QPushButton("Copy command preview")
            copy_button.clicked.connect(self.copy_command_preview)
            right_layout.addWidget(self.title_label)
            right_layout.addWidget(QLabel("Summary"))
            right_layout.addWidget(self.summary_box)
            right_layout.addWidget(QLabel("Command preview"))
            right_layout.addWidget(self.command_box)
            right_layout.addWidget(copy_button)

            splitter.addWidget(left_panel)
            splitter.addWidget(right_panel)
            splitter.setStretchFactor(0, 1)
            splitter.setStretchFactor(1, 2)

            layout.addWidget(title)
            layout.addWidget(subtitle)
            layout.addWidget(splitter)
            self.setCentralWidget(container)

            for workflow in model.workflows:
                item = QListWidgetItem(f"{workflow.title} ({workflow.name})")
                item.setData(Qt.UserRole, ("workflow", workflow.name))
                self.workflow_list.addItem(item)

            for problem in model.problems:
                item = QListWidgetItem(f"{problem.title} ({problem.name})")
                item.setData(Qt.UserRole, ("problem", problem.name))
                self.problem_list.addItem(item)

            self.workflow_list.currentItemChanged.connect(self._on_workflow_changed)
            self.problem_list.currentItemChanged.connect(self._on_problem_changed)

        def _on_workflow_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
            if current is None:
                return
            payload = current.data(Qt.UserRole)
            if payload is None:
                return
            _, name = payload
            workflow = next(item for item in model.workflows if item.name == name)
            form_model = build_workflow_form_model(name)
            self.problem_list.blockSignals(True)
            self.problem_list.clearSelection()
            self.problem_list.blockSignals(False)
            self.title_label.setText(workflow.title)
            field_lines = [
                f"- {item.label} ({item.kind})"
                + (" [required]" if item.required else "")
                + (" [multiple]" if item.multiple else "")
                for item in form_model.fields
            ]
            self.summary_box.setPlainText(
                f"{workflow.summary}\n\nBest for: {workflow.best_for}\n\nForm fields:\n"
                + "\n".join(field_lines)
            )
            self.command_box.setPlainText(workflow.example_command)

        def _on_problem_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
            if current is None:
                return
            payload = current.data(Qt.UserRole)
            if payload is None:
                return
            _, name = payload
            problem = next(item for item in model.problems if item.name == name)
            self.workflow_list.blockSignals(True)
            self.workflow_list.clearSelection()
            self.workflow_list.blockSignals(False)
            self.title_label.setText(problem.title)
            self.summary_box.setPlainText(
                f"{problem.summary}\n\nRecommended workflow: {problem.recommended_workflow}\n\nNext step: {problem.next_step}"
            )
            self.command_box.setPlainText(problem.recommended_command)

        def copy_command_preview(self) -> None:
            command = self.command_box.toPlainText().strip()
            if not command:
                QMessageBox.information(self, "Nothing to copy", "Select a workflow or problem first.")
                return
            QApplication.clipboard().setText(command)
            QMessageBox.information(self, "Copied", "The command preview was copied to the clipboard.")

    app = QApplication.instance() or QApplication([])
    window = WorkflowShellWindow()
    window.show()
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.dump_model:
        print(json.dumps(build_gui_shell_model().to_dict(), indent=2, ensure_ascii=False))
        return 0

    if args.dump_forms:
        print(
            json.dumps(
                {"forms": [item.to_dict() for item in list_workflow_form_models()]},
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.dump_launchers:
        print(
            json.dumps(
                build_workflow_launcher_model(args.profiles_dir).to_dict(),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.preview_workflow:
        try:
            print(build_shell_command_preview_for_workflow(args.preview_workflow))
        except ValueError as exc:
            parser.error(str(exc))
        return 0

    if args.preview_problem:
        try:
            print(build_shell_command_preview_for_problem(args.preview_problem))
        except ValueError as exc:
            parser.error(str(exc))
        return 0

    if args.preview_form:
        try:
            print(json.dumps(build_workflow_form_model(args.preview_form).to_dict(), indent=2, ensure_ascii=False))
        except ValueError as exc:
            parser.error(str(exc))
        return 0

    if args.preview_preset_form:
        try:
            print(json.dumps(build_preset_bound_workflow_form_model(args.preview_preset_form).to_dict(), indent=2, ensure_ascii=False))
        except ValueError as exc:
            parser.error(str(exc))
        return 0

    if args.preview_profile_form:
        try:
            print(json.dumps(build_profile_bound_workflow_form_model(args.preview_profile_form).to_dict(), indent=2, ensure_ascii=False))
        except Exception as exc:
            parser.error(str(exc))
        return 0

    if args.preview_profile_command:
        try:
            bound = build_profile_bound_workflow_form_model(args.preview_profile_command)
        except Exception as exc:
            parser.error(str(exc))
        print(bound.command_preview or "")
        return 0

    return _launch_gui_shell()
