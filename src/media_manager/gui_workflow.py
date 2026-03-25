from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from .gui_review import APP_STYLESHEET, MediaManagerWindow as ReviewWindow
from .workflow_progress import (
    workflow_completed_steps,
    workflow_next_required_step,
    workflow_progress_percent,
    workflow_required_steps,
)


class WorkflowStepBadge(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        self.status_label = QLabel("Pending")
        self.status_label.setStyleSheet("color: #AFC1D9;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)

    def set_status(self, status: str, *, highlight: bool = False) -> None:
        self.status_label.setText(status)
        if highlight:
            self.setStyleSheet("border: 1px solid #2F6FED; border-radius: 22px;")
        else:
            self.setStyleSheet("")


class MediaManagerWindow(ReviewWindow):
    def __init__(self) -> None:
        super().__init__()
        self._install_workflow_stepper()
        self._refresh_workflow_stepper()

    def _install_workflow_stepper(self) -> None:
        workflow_page = self.stack.widget(1)
        outer_layout = workflow_page.layout()

        self.workflow_progress_card = QFrame()
        self.workflow_progress_card.setObjectName("Card")
        progress_layout = QVBoxLayout(self.workflow_progress_card)
        progress_layout.setContentsMargins(20, 18, 20, 18)
        progress_layout.setSpacing(10)

        title_label = QLabel("Workflow progress")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)

        self.workflow_progress_summary_label = QLabel("Choose a guided path to begin.")
        self.workflow_progress_summary_label.setStyleSheet("color: #AFC1D9;")
        self.workflow_progress_summary_label.setWordWrap(True)

        self.workflow_progress_bar = QProgressBar()
        self.workflow_progress_bar.setRange(0, 100)
        self.workflow_progress_bar.setValue(0)
        self.workflow_progress_bar.setTextVisible(False)
        self.workflow_progress_bar.setFixedHeight(12)
        self.workflow_progress_bar.setStyleSheet(
            "QProgressBar {"
            " background: #091321;"
            " border: 1px solid #31455F;"
            " border-radius: 6px;"
            "}"
            "QProgressBar::chunk {"
            " background: #2F6FED;"
            " border-radius: 6px;"
            "}"
        )

        badges_row = QHBoxLayout()
        badges_row.setSpacing(12)
        self.workflow_step_badges = {
            "duplicates": WorkflowStepBadge("1. Duplicates"),
            "organize": WorkflowStepBadge("2. Organize"),
            "rename": WorkflowStepBadge("3. Rename"),
        }
        for badge in self.workflow_step_badges.values():
            badges_row.addWidget(badge)

        progress_layout.addWidget(title_label)
        progress_layout.addWidget(self.workflow_progress_summary_label)
        progress_layout.addWidget(self.workflow_progress_bar)
        progress_layout.addLayout(badges_row)

        outer_layout.insertWidget(2, self.workflow_progress_card)

    def _refresh_workflow_summary_cards(self) -> None:
        super()._refresh_workflow_summary_cards()
        if hasattr(self, "workflow_progress_bar"):
            self._refresh_workflow_stepper()

    def _refresh_workflow_stepper(self) -> None:
        required_steps = workflow_required_steps(self.workflow_selected_problem)
        completed_steps = workflow_completed_steps(self.workflow_selected_problem, self.workflow_step_statuses)
        next_step = workflow_next_required_step(self.workflow_selected_problem, self.workflow_step_statuses)
        percent = workflow_progress_percent(self.workflow_selected_problem, self.workflow_step_statuses)

        self.workflow_progress_bar.setValue(percent)
        if next_step == "finished":
            self.workflow_progress_summary_label.setText(
                f"Workflow complete. {completed_steps}/{len(required_steps)} required steps finished."
            )
        else:
            self.workflow_progress_summary_label.setText(
                f"{completed_steps}/{len(required_steps)} required steps finished. Next: {next_step.title()}."
            )

        current_step_key = self.workflow_current_step.strip().lower()
        required_set = set(required_steps)
        for key, badge in self.workflow_step_badges.items():
            if key not in required_set:
                badge.set_status("Not required")
                continue
            status = self.workflow_step_statuses.get(key, "Pending")
            is_active = current_step_key.startswith(key) or (current_step_key == "setup" and next_step == key)
            if status.startswith("Done"):
                badge.set_status("Done", highlight=False)
            elif status == "Ready":
                badge.set_status("Ready", highlight=True)
            else:
                badge.set_status(status, highlight=is_active)


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = MediaManagerWindow()
    window.show()
    return app.exec()
