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

from .duplicates import DuplicateScanConfig, scan_exact_duplicates
from .exiftool import resolve_exiftool_path
from .renamer import RenameConfig, rename_media
from .settings import (
    CUSTOM_TEMPLATE_LABEL,
    DEFAULT_RENAME_TEMPLATE,
    DEFAULT_TARGET_TEMPLATE,
    ORGANIZE_TEMPLATE_PRESETS,
    RENAME_TEMPLATE_PRESETS,
    get_import_set,
    list_import_sets,
    load_app_settings,
    remove_import_set,
    save_app_settings,
    template_preset_label,
    upsert_import_set,
)
from .sorter import SortConfig, organize_media

APP_STYLESHEET = """
QMainWindow {
    background: #07111F;
}
QWidget {
    color: #E6EEF8;
    font-size: 13px;
}
QFrame#Card {
    background: #0C1728;
    border: 1px solid #22324A;
    border-radius: 22px;
}
QFrame#HeroCard {
    background: #0B1628;
    border: 1px solid #2E4A70;
    border-radius: 24px;
}
QFrame#Nav {
    background: #091321;
    border: 1px solid #1B2A40;
    border-radius: 22px;
}
QGroupBox {
    border: 1px solid #22324A;
    border-radius: 18px;
    margin-top: 12px;
    padding-top: 16px;
    background: #0C1728;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #F8FBFF;
    font-weight: 700;
}
QLineEdit, QListWidget, QTableWidget, QComboBox {
    background: #091321;
    border: 1px solid #31455F;
    border-radius: 14px;
    padding: 9px;
    selection-background-color: #2F6FED;
    alternate-background-color: #0D1829;
}
QListWidget::item {
    padding: 10px;
    border-radius: 10px;
}
QListWidget::item:selected {
    background: #18345B;
}
QPushButton {
    background: #2F6FED;
    color: #F7FAFF;
    border: none;
    border-radius: 14px;
    padding: 10px 15px;
    font-weight: 700;
}
QPushButton:hover {
    background: #255FCE;
}
QPushButton:disabled {
    background: #2B3441;
    color: #8A97AA;
}
QPushButton[variant="secondary"] {
    background: #132033;
    color: #F7FAFF;
    border: 1px solid #31455F;
}
QPushButton[variant="secondary"]:hover {
    background: #18283E;
}
QPushButton[variant="ghost"] {
    background: transparent;
    color: #A9C3FF;
    border: 1px solid #31455F;
}
QPushButton[variant="ghost"]:hover {
    background: #102038;
}
QPushButton[nav="true"] {
    text-align: left;
    padding: 12px 14px;
}
QHeaderView::section {
    background: #0C1728;
    color: #F8FBFF;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #31455F;
}
QStatusBar {
    background: #07111F;
    border-top: 1px solid #111F33;
}
QCheckBox, QRadioButton {
    spacing: 8px;
}
"""

ACTION_LABELS = {
    "preview-copy": "Preview copy",
    "preview-move": "Preview move",
    "copied": "Copied",
    "moved": "Moved",
    "preview-rename": "Preview rename",
    "renamed": "Renamed",
    "unchanged": "Unchanged",
    "error": "Error",
}

GUIDED_PROBLEMS = [
    {
        "key": "full_cleanup",
        "label": "My folders are messy and I want the cleanest full result",
        "description": "Recommended path: Duplicates → Organize → Rename. Best choice for mixed sources and unclear folder quality.",
    },
    {
        "key": "ready_for_sorting",
        "label": "Duplicates are already handled, now I need clean sorting",
        "description": "Recommended path: Organize → Rename. Use this when duplicate cleanup is already done outside the app.",
    },
    {
        "key": "ready_for_rename",
        "label": "The files are already in the right folder, I only need better names",
        "description": "Recommended path: Rename only. The previous target folder is used as the likely rename source.",
    },
    {
        "key": "exact_duplicates_only",
        "label": "I only want to inspect exact duplicates right now",
        "description": "Recommended path: Duplicates only. Exact means 100% byte-identical, not visually similar.",
    },
]


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "-") -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #9DB1CE; font-size: 12px;")
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #93A8C6;")

        self.button = QPushButton(button_text)
        if not enabled:
            self.button.setEnabled(False)
            self.button.setProperty("variant", "secondary")
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch(1)
        layout.addWidget(self.button)


class WorkflowStepCard(QFrame):
    def __init__(self, title: str, description: str, button_text: str) -> None:
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)

        self.status_label = QLabel("Pending")
        self.status_label.setStyleSheet("color: #A9C3FF;")

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #93A8C6;")

        self.button = QPushButton(button_text)
        self.button.setProperty("variant", "secondary")

        layout.addWidget(title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(description_label)
        layout.addStretch(1)
        layout.addWidget(self.button)

    def set_status(self, value: str) -> None:
        self.status_label.setText(value)


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


def format_file_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KiB"
    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MiB"
    return f"{size / (1024 * 1024 * 1024):.2f} GiB"


class MediaManagerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Media Manager")
        self.resize(1640, 1020)
        self.setMinimumSize(1440, 920)
        self.app_settings: dict[str, object] = {}
        self.workflow_current_step = "Setup"
        self.workflow_selected_problem = "full_cleanup"
        self.workflow_step_statuses = {
            "duplicates": "Pending",
            "organize": "Pending",
            "rename": "Pending",
        }

        self.guided_problem_combo = QComboBox()
        self.guided_problem_combo.setMinimumWidth(520)
        self.guided_problem_hint_label = QLabel()
        self.guided_problem_hint_label.setWordWrap(True)
        self.guided_problem_hint_label.setStyleSheet("color: #AFC1D9;")
        self.guided_start_button = QPushButton("Start guided path")
        self.guided_workflow_board_button = QPushButton("Open workflow board")
        self.guided_workflow_board_button.setProperty("variant", "secondary")

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target folder")
        self.exiftool_input = QLineEdit()
        self.exiftool_input.setPlaceholderText("Auto-detect when empty")
        self.template_preset_combo = QComboBox()
        self.template_preset_combo.setMinimumWidth(240)
        self.organize_template_label = QLabel("Template")
        self.template_input = QLineEdit(DEFAULT_TARGET_TEMPLATE)
        self.apply_checkbox = QCheckBox("Apply")
        self.import_set_combo = QComboBox()
        self.import_set_combo.setMinimumWidth(260)
        self.source_list = QListWidget()
        self.source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.source_list.setAlternatingRowColors(True)
        self.source_details_label = QLabel("No source folder selected.")
        self.source_details_label.setWordWrap(True)
        self.source_details_label.setStyleSheet("color: #93A8C6;")
        self.organize_workflow_hint_label = QLabel("No workflow setup connected yet.")
        self.organize_workflow_hint_label.setWordWrap(True)
        self.organize_workflow_hint_label.setStyleSheet("color: #93A8C6;")
        self.copy_radio = QRadioButton("Copy")
        self.move_radio = QRadioButton("Move")
        self.copy_radio.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.copy_radio)
        self.mode_group.addButton(self.move_radio)
        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels(["Status", "File", "Source", "Target", "Details"])
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setAlternatingRowColors(True)

        self.rename_source_list = QListWidget()
        self.rename_source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.rename_source_list.setAlternatingRowColors(True)
        self.rename_source_details_label = QLabel("No source folder selected.")
        self.rename_source_details_label.setWordWrap(True)
        self.rename_source_details_label.setStyleSheet("color: #93A8C6;")
        self.rename_target_hint_label = QLabel("No suggested source from the previous target yet.")
        self.rename_target_hint_label.setWordWrap(True)
        self.rename_target_hint_label.setStyleSheet("color: #93A8C6;")
        self.rename_template_preset_combo = QComboBox()
        self.rename_template_preset_combo.setMinimumWidth(240)
        self.rename_template_label = QLabel("Template")
        self.rename_template_input = QLineEdit(DEFAULT_RENAME_TEMPLATE)
        self.rename_apply_checkbox = QCheckBox("Apply")
        self.rename_template_hint = QLabel("Template fields: {year} {month} {day} {hour} {minute} {second} {stem} {suffix} {index}")
        self.rename_template_hint.setWordWrap(True)
        self.rename_template_hint.setStyleSheet("color: #93A8C6;")
        self.rename_results_table = QTableWidget(0, 5)
        self.rename_results_table.setHorizontalHeaderLabels(["Status", "Current", "New", "Folder", "Details"])
        self.rename_results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.rename_results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rename_results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.rename_results_table.verticalHeader().setVisible(False)
        self.rename_results_table.setAlternatingRowColors(True)

        self.duplicates_source_list = QListWidget()
        self.duplicates_source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.duplicates_source_list.setAlternatingRowColors(True)
        self.duplicates_source_details_label = QLabel("No source folder selected.")
        self.duplicates_source_details_label.setWordWrap(True)
        self.duplicates_source_details_label.setStyleSheet("color: #93A8C6;")
        self.duplicates_workflow_hint_label = QLabel("No workflow source set linked yet.")
        self.duplicates_workflow_hint_label.setWordWrap(True)
        self.duplicates_workflow_hint_label.setStyleSheet("color: #93A8C6;")
        self.duplicates_results_table = QTableWidget(0, 5)
        self.duplicates_results_table.setHorizontalHeaderLabels(["Group", "File", "Folder", "Size", "Notes"])
        self.duplicates_results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.duplicates_results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.duplicates_results_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.duplicates_results_table.verticalHeader().setVisible(False)
        self.duplicates_results_table.setAlternatingRowColors(True)

        self.workflow_source_list = QListWidget()
        self.workflow_source_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.workflow_source_list.setAlternatingRowColors(True)
        self.workflow_source_details_label = QLabel("No source folder selected.")
        self.workflow_source_details_label.setWordWrap(True)
        self.workflow_source_details_label.setStyleSheet("color: #93A8C6;")
        self.workflow_target_input = QLineEdit()
        self.workflow_target_input.setPlaceholderText("Final target folder")
        self.workflow_mode_hint_label = QLabel()
        self.workflow_mode_hint_label.setWordWrap(True)
        self.workflow_mode_hint_label.setStyleSheet("color: #AFC1D9;")
        self.workflow_hint_label = QLabel("Guided workflow: review exact duplicates, then organize into the target, then rename inside that target.")
        self.workflow_hint_label.setWordWrap(True)
        self.workflow_hint_label.setStyleSheet("color: #93A8C6;")
        self.workflow_duplicates_step_card = WorkflowStepCard("Step 1 — Duplicates", "Review exact byte-identical duplicates first. This reduces clutter before the real processing starts.", "Open duplicates")
        self.workflow_organize_step_card = WorkflowStepCard("Step 2 — Organize", "Sort the remaining material into the chosen target folder.", "Open organize")
        self.workflow_rename_step_card = WorkflowStepCard("Step 3 — Rename", "Rename the organized files inside the target folder with readable templates.", "Open rename")

        self.sources_card = StatCard("Sources", "0")
        self.target_card = StatCard("Target", "Not set")
        self.mode_card = StatCard("Mode", "Copy")
        self.run_mode_card = StatCard("Run", "Pre-run")
        self.rename_sources_card = StatCard("Sources", "0")
        self.rename_template_card = StatCard("Template", DEFAULT_RENAME_TEMPLATE)
        self.rename_run_mode_card = StatCard("Run", "Pre-run")
        self.rename_status_card = StatCard("Module", "Rename")
        self.duplicates_sources_card = StatCard("Sources", "0")
        self.duplicates_groups_card = StatCard("Exact groups", "-")
        self.duplicates_files_card = StatCard("Duplicate files", "-")
        self.duplicates_extra_card = StatCard("Extra duplicates", "-")
        self.workflow_sources_card = StatCard("Sources", "0")
        self.workflow_target_card = StatCard("Target", "Not set")
        self.workflow_status_card = StatCard("Current step", "Setup")
        self.workflow_next_card = StatCard("Next action", "Choose a path")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.stack = QStackedWidget()
        self.home_button = QPushButton("Home")
        self.home_button.setProperty("nav", "true")
        self.home_button.setProperty("variant", "secondary")
        self.workflow_button = QPushButton("Workflow")
        self.workflow_button.setProperty("nav", "true")
        self.workflow_button.setProperty("variant", "secondary")
        self.organize_button = QPushButton("Organize")
        self.organize_button.setProperty("nav", "true")
        self.organize_button.setProperty("variant", "secondary")
        self.rename_button = QPushButton("Rename")
        self.rename_button.setProperty("nav", "true")
        self.rename_button.setProperty("variant", "secondary")
        self.duplicates_button = QPushButton("Duplicates")
        self.duplicates_button.setProperty("nav", "true")
        self.duplicates_button.setProperty("variant", "secondary")

        self._build_ui()
        self._populate_template_preset_combos()
        self._populate_guided_problem_combo()
        self._apply_readability_styles()
        self._wire_signals()
        self._load_settings()
        self._refresh_summary_cards()
        self._refresh_rename_summary_cards()
        self._refresh_duplicates_summary_cards()
        self._refresh_workflow_summary_cards()
        for list_widget in [self.source_list, self.rename_source_list, self.duplicates_source_list, self.workflow_source_list]:
            self._refresh_source_list_height(list_widget)
        self._update_guided_problem_hint()
        self._update_cross_module_suggestions()
        self._resize_result_columns(self.results_table)
        self._resize_result_columns(self.rename_results_table)
        self._resize_result_columns(self.duplicates_results_table)
        self._set_current_page(0)

    def _build_ui(self) -> None:
        container = QWidget()
        root_layout = QHBoxLayout(container)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(16)

        nav = QFrame()
        nav.setObjectName("Nav")
        nav.setFixedWidth(230)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(18, 18, 18, 18)
        nav_layout.setSpacing(10)

        app_title = QLabel("Media Manager")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        app_title.setFont(title_font)

        app_subtitle = QLabel("Guided first. Manual when needed.")
        app_subtitle.setStyleSheet("color: #93A8C6;")

        nav_layout.addWidget(app_title)
        nav_layout.addWidget(app_subtitle)
        nav_layout.addSpacing(12)
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.workflow_button)
        nav_layout.addWidget(self.organize_button)
        nav_layout.addWidget(self.rename_button)
        nav_layout.addWidget(self.duplicates_button)
        nav_layout.addStretch(1)

        self.stack.addWidget(self._build_home_page())
        self.stack.addWidget(self._build_workflow_page())
        self.stack.addWidget(self._build_organize_page())
        self.stack.addWidget(self._build_rename_page())
        self.stack.addWidget(self._build_duplicates_page())

        root_layout.addWidget(nav)
        root_layout.addWidget(self.stack, 1)
        self.setCentralWidget(container)

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(8)

        title = QLabel("Start from the problem, not from the tool")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Choose your current situation and the app will point you to the right next step. Manual workspaces are still available below.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #AFC1D9;")
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)

        layout.addWidget(hero)

        guided_group = QGroupBox("Guided mode")
        guided_layout = QVBoxLayout(guided_group)
        guided_layout.setSpacing(12)
        guided_layout.addWidget(self.guided_problem_combo)
        guided_layout.addWidget(self.guided_problem_hint_label)

        guided_actions = QHBoxLayout()
        guided_actions.addWidget(self.guided_start_button)
        guided_actions.addWidget(self.guided_workflow_board_button)
        guided_actions.addStretch(1)
        guided_layout.addLayout(guided_actions)

        manual_group = QGroupBox("Manual mode")
        manual_layout = QVBoxLayout(manual_group)
        manual_layout.setSpacing(12)

        manual_hint = QLabel("Use this when you already know exactly which workspace you want. Same functionality, less hand-holding.")
        manual_hint.setWordWrap(True)
        manual_hint.setStyleSheet("color: #93A8C6;")
        manual_layout.addWidget(manual_hint)

        manual_grid = QGridLayout()
        manual_grid.setHorizontalSpacing(14)
        manual_grid.setVerticalSpacing(14)
        organize_card = ModuleCard("Organize", "Sort media from one or more source folders into one target folder.", "Open")
        organize_card.button.clicked.connect(lambda: self._set_current_page(2))
        rename_card = ModuleCard("Rename", "Rename media in place from one or more source folders using a template.", "Open")
        rename_card.button.clicked.connect(lambda: self._set_current_page(3))
        duplicates_card = ModuleCard("Duplicates", "Scan exact duplicate media across one or more source folders.", "Open")
        duplicates_card.button.clicked.connect(lambda: self._set_current_page(4))
        workflow_card = ModuleCard("Workflow board", "Open the central guided board with setup, current step and progress tracking.", "Open")
        workflow_card.button.clicked.connect(lambda: self._set_current_page(1))
        manual_grid.addWidget(workflow_card, 0, 0)
        manual_grid.addWidget(organize_card, 0, 1)
        manual_grid.addWidget(duplicates_card, 1, 0)
        manual_grid.addWidget(rename_card, 1, 1)
        manual_layout.addLayout(manual_grid)

        layout.addWidget(guided_group)
        layout.addWidget(manual_group)
        layout.addStretch(1)
        return page

    def _build_workflow_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 22, 22, 22)
        header_layout.setSpacing(8)

        title = QLabel("Guided workflow board")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Set sources and target once. Then move through the recommended path with carried-over suggestions.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #AFC1D9;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(self.workflow_mode_hint_label)

        outer_layout.addWidget(header)
        outer_layout.addLayout(self._build_workflow_summary_row())

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(14)
        controls_layout.addWidget(self._build_workflow_setup_group())
        controls_layout.addStretch(1)

        steps_group = QGroupBox("Recommended path")
        steps_layout = QVBoxLayout(steps_group)
        steps_layout.setSpacing(12)
        steps_layout.addWidget(self.workflow_hint_label)
        steps_layout.addWidget(self.workflow_duplicates_step_card)
        steps_layout.addWidget(self.workflow_organize_step_card)
        steps_layout.addWidget(self.workflow_rename_step_card)

        content_layout.addWidget(controls_panel, 4)
        content_layout.addWidget(steps_group, 7)
        outer_layout.addLayout(content_layout)
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
        subtitle.setStyleSheet("color: #93A8C6;")
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
        results_layout.addWidget(self.results_table)

        content_layout.addWidget(controls_panel, 4)
        content_layout.addWidget(results_group, 7)
        outer_layout.addLayout(content_layout)
        return page

    def _build_rename_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(6)

        title = QLabel("Rename")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Rename media in place. Preview first.")
        subtitle.setStyleSheet("color: #93A8C6;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        outer_layout.addWidget(header)
        outer_layout.addLayout(self._build_rename_summary_row())

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(14)
        controls_layout.addWidget(self._build_rename_sources_group())
        controls_layout.addWidget(self._build_rename_options_group())
        controls_layout.addWidget(self._build_rename_run_group())
        controls_layout.addStretch(1)

        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setSpacing(10)
        results_layout.addWidget(self.rename_results_table)

        content_layout.addWidget(controls_panel, 4)
        content_layout.addWidget(results_group, 7)
        outer_layout.addLayout(content_layout)
        return page

    def _build_duplicates_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(6)

        title = QLabel("Duplicates")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Exact duplicate scan across multiple sources. 100% means byte-identical only.")
        subtitle.setStyleSheet("color: #93A8C6;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        outer_layout.addWidget(header)
        outer_layout.addLayout(self._build_duplicates_summary_row())

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(14)
        controls_layout.addWidget(self._build_duplicates_sources_group())
        controls_layout.addWidget(self._build_duplicates_run_group())
        controls_layout.addStretch(1)

        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setSpacing(10)
        results_layout.addWidget(self.duplicates_results_table)

        content_layout.addWidget(controls_panel, 4)
        content_layout.addWidget(results_group, 7)
        outer_layout.addLayout(content_layout)
        return page

    def _build_workflow_summary_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self.workflow_sources_card)
        row.addWidget(self.workflow_target_card)
        row.addWidget(self.workflow_status_card)
        row.addWidget(self.workflow_next_card)
        return row

    def _build_summary_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self.sources_card)
        row.addWidget(self.target_card)
        row.addWidget(self.mode_card)
        row.addWidget(self.run_mode_card)
        return row

    def _build_rename_summary_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self.rename_sources_card)
        row.addWidget(self.rename_template_card)
        row.addWidget(self.rename_run_mode_card)
        row.addWidget(self.rename_status_card)
        return row

    def _build_duplicates_summary_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self.duplicates_sources_card)
        row.addWidget(self.duplicates_groups_card)
        row.addWidget(self.duplicates_files_card)
        row.addWidget(self.duplicates_extra_card)
        return row

    def _build_workflow_setup_group(self) -> QGroupBox:
        group = QGroupBox("Workflow setup")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.addWidget(self.workflow_source_list)
        layout.addWidget(self.workflow_source_details_label)

        buttons_row = QHBoxLayout()
        self.workflow_add_source_button = QPushButton("Add")
        self.workflow_remove_source_button = QPushButton("Remove")
        self.workflow_clear_sources_button = QPushButton("Clear")
        self.workflow_remove_source_button.setProperty("variant", "secondary")
        self.workflow_clear_sources_button.setProperty("variant", "secondary")
        self.workflow_add_source_button.clicked.connect(self._workflow_add_source_folder)
        self.workflow_remove_source_button.clicked.connect(self._workflow_remove_selected_sources)
        self.workflow_clear_sources_button.clicked.connect(self._workflow_clear_sources)
        buttons_row.addWidget(self.workflow_add_source_button)
        buttons_row.addWidget(self.workflow_remove_source_button)
        buttons_row.addWidget(self.workflow_clear_sources_button)
        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)

        target_row = QHBoxLayout()
        self.workflow_target_browse_button = QPushButton("Browse target")
        self.workflow_target_browse_button.clicked.connect(self._choose_workflow_target_folder)
        target_row.addWidget(self.workflow_target_input, 1)
        target_row.addWidget(self.workflow_target_browse_button)
        layout.addLayout(target_row)

        actions_row = QHBoxLayout()
        self.workflow_apply_button = QPushButton("Apply to modules")
        self.workflow_start_button = QPushButton("Start guided workflow")
        self.workflow_apply_button.setProperty("variant", "secondary")
        self.workflow_apply_button.clicked.connect(self._apply_workflow_setup_to_modules)
        self.workflow_start_button.clicked.connect(self._start_guided_workflow)
        actions_row.addWidget(self.workflow_apply_button)
        actions_row.addWidget(self.workflow_start_button)
        actions_row.addStretch(1)
        layout.addLayout(actions_row)
        return group

    def _build_sources_group(self) -> QGroupBox:
        group = QGroupBox("Source folders")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        workflow_row = QHBoxLayout()
        self.organize_use_workflow_button = QPushButton("Use workflow setup")
        self.organize_use_workflow_button.setProperty("variant", "secondary")
        self.organize_use_workflow_button.clicked.connect(self._apply_workflow_setup_to_modules)
        workflow_row.addWidget(self.organize_use_workflow_button)
        workflow_row.addWidget(self.organize_workflow_hint_label, 1)
        layout.addLayout(workflow_row)

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

    def _build_rename_sources_group(self) -> QGroupBox:
        group = QGroupBox("Source folders")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        workflow_row = QHBoxLayout()
        self.rename_use_target_button = QPushButton("Use previous target")
        self.rename_use_target_button.setProperty("variant", "secondary")
        self.rename_use_target_button.clicked.connect(self._use_current_target_for_rename)
        workflow_row.addWidget(self.rename_use_target_button)
        workflow_row.addWidget(self.rename_target_hint_label, 1)
        layout.addLayout(workflow_row)

        layout.addWidget(self.rename_source_list)
        layout.addWidget(self.rename_source_details_label)

        buttons_row = QHBoxLayout()
        self.rename_add_source_button = QPushButton("Add")
        self.rename_remove_source_button = QPushButton("Remove")
        self.rename_clear_sources_button = QPushButton("Clear")
        self.rename_remove_source_button.setProperty("variant", "secondary")
        self.rename_clear_sources_button.setProperty("variant", "secondary")
        self.rename_add_source_button.clicked.connect(self._rename_add_source_folder)
        self.rename_remove_source_button.clicked.connect(self._rename_remove_selected_sources)
        self.rename_clear_sources_button.clicked.connect(self._rename_clear_sources)
        buttons_row.addWidget(self.rename_add_source_button)
        buttons_row.addWidget(self.rename_remove_source_button)
        buttons_row.addWidget(self.rename_clear_sources_button)
        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)
        return group

    def _build_duplicates_sources_group(self) -> QGroupBox:
        group = QGroupBox("Source folders")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        workflow_row = QHBoxLayout()
        self.duplicates_use_workflow_button = QPushButton("Use workflow setup")
        self.duplicates_use_workflow_button.setProperty("variant", "secondary")
        self.duplicates_use_workflow_button.clicked.connect(self._apply_workflow_setup_to_duplicates)
        workflow_row.addWidget(self.duplicates_use_workflow_button)
        workflow_row.addWidget(self.duplicates_workflow_hint_label, 1)
        layout.addLayout(workflow_row)

        layout.addWidget(self.duplicates_source_list)
        layout.addWidget(self.duplicates_source_details_label)

        buttons_row = QHBoxLayout()
        self.duplicates_add_source_button = QPushButton("Add")
        self.duplicates_remove_source_button = QPushButton("Remove")
        self.duplicates_clear_sources_button = QPushButton("Clear")
        self.duplicates_remove_source_button.setProperty("variant", "secondary")
        self.duplicates_clear_sources_button.setProperty("variant", "secondary")
        self.duplicates_add_source_button.clicked.connect(self._duplicates_add_source_folder)
        self.duplicates_remove_source_button.clicked.connect(self._duplicates_remove_selected_sources)
        self.duplicates_clear_sources_button.clicked.connect(self._duplicates_clear_sources)
        buttons_row.addWidget(self.duplicates_add_source_button)
        buttons_row.addWidget(self.duplicates_remove_source_button)
        buttons_row.addWidget(self.duplicates_clear_sources_button)
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
        layout.addWidget(QLabel("Template preset"), 2, 0)
        layout.addWidget(self.template_preset_combo, 2, 1, 1, 2)
        layout.addWidget(self.organize_template_label, 3, 0)
        layout.addWidget(self.template_input, 3, 1, 1, 2)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode"))
        mode_row.addWidget(self.copy_radio)
        mode_row.addWidget(self.move_radio)
        mode_row.addSpacing(16)
        mode_row.addWidget(self.apply_checkbox)
        mode_row.addStretch(1)
        layout.addLayout(mode_row, 4, 0, 1, 3)
        layout.addWidget(self.open_target_button, 5, 2)
        return group

    def _build_rename_options_group(self) -> QGroupBox:
        group = QGroupBox("Rename options")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)
        layout.setColumnStretch(1, 1)
        layout.addWidget(QLabel("Template preset"), 0, 0)
        layout.addWidget(self.rename_template_preset_combo, 0, 1)
        layout.addWidget(self.rename_template_label, 1, 0)
        layout.addWidget(self.rename_template_input, 1, 1)
        layout.addWidget(self.rename_apply_checkbox, 2, 1)
        layout.addWidget(self.rename_template_hint, 3, 0, 1, 2)
        return group

    def _build_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)
        row = QHBoxLayout()
        self.run_button = QPushButton("Pre-run")
        self.clear_results_button = QPushButton("Clear results")
        self.clear_results_button.setProperty("variant", "secondary")
        self.run_button.clicked.connect(self._run)
        self.clear_results_button.clicked.connect(self._clear_results)
        row.addWidget(self.run_button)
        row.addWidget(self.clear_results_button)
        row.addStretch(1)
        layout.addLayout(row)
        return group

    def _build_rename_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)
        row = QHBoxLayout()
        self.rename_run_button = QPushButton("Pre-run")
        self.rename_clear_results_button = QPushButton("Clear results")
        self.rename_clear_results_button.setProperty("variant", "secondary")
        self.rename_run_button.clicked.connect(self._run_rename)
        self.rename_clear_results_button.clicked.connect(self._rename_clear_results)
        row.addWidget(self.rename_run_button)
        row.addWidget(self.rename_clear_results_button)
        row.addStretch(1)
        layout.addLayout(row)
        return group

    def _build_duplicates_run_group(self) -> QGroupBox:
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)
        row = QHBoxLayout()
        self.duplicates_run_button = QPushButton("Scan")
        self.duplicates_clear_results_button = QPushButton("Clear results")
        self.duplicates_clear_results_button.setProperty("variant", "secondary")
        self.duplicates_run_button.clicked.connect(self._run_duplicates)
        self.duplicates_clear_results_button.clicked.connect(self._duplicates_clear_results)
        row.addWidget(self.duplicates_run_button)
        row.addWidget(self.duplicates_clear_results_button)
        row.addStretch(1)
        layout.addLayout(row)
        return group

    def _populate_template_preset_combos(self) -> None:
        self._fill_template_combo(self.template_preset_combo, ORGANIZE_TEMPLATE_PRESETS)
        self._fill_template_combo(self.rename_template_preset_combo, RENAME_TEMPLATE_PRESETS)

    def _populate_guided_problem_combo(self) -> None:
        self.guided_problem_combo.clear()
        for item in GUIDED_PROBLEMS:
            self.guided_problem_combo.addItem(item["label"], item["key"])

    def _fill_template_combo(self, combo: QComboBox, presets: list[dict[str, str]]) -> None:
        combo.clear()
        for preset in presets:
            combo.addItem(preset["label"], preset["template"])
        combo.addItem(CUSTOM_TEMPLATE_LABEL, None)

    def _apply_readability_styles(self) -> None:
        table_font = QFont()
        table_font.setPointSize(14)
        list_font = QFont()
        list_font.setPointSize(14)
        for table in [self.results_table, self.rename_results_table, self.duplicates_results_table]:
            table.setFont(table_font)
            table.horizontalHeader().setFont(table_font)
            table.horizontalHeader().setStretchLastSection(True)
            table.verticalHeader().setDefaultSectionSize(36)
        for list_widget in [self.source_list, self.rename_source_list, self.duplicates_source_list, self.workflow_source_list]:
            list_widget.setFont(list_font)
            list_widget.setSpacing(5)

    def _wire_signals(self) -> None:
        self.home_button.clicked.connect(lambda: self._set_current_page(0))
        self.workflow_button.clicked.connect(lambda: self._set_current_page(1))
        self.organize_button.clicked.connect(lambda: self._set_current_page(2))
        self.rename_button.clicked.connect(lambda: self._set_current_page(3))
        self.duplicates_button.clicked.connect(lambda: self._set_current_page(4))
        self.guided_problem_combo.currentIndexChanged.connect(self._update_guided_problem_hint)
        self.guided_start_button.clicked.connect(self._start_from_home_problem)
        self.guided_workflow_board_button.clicked.connect(lambda: self._set_current_page(1))
        self.target_input.textChanged.connect(self._on_target_changed)
        self.workflow_target_input.textChanged.connect(self._on_workflow_target_changed)
        self.template_input.textChanged.connect(self._on_organize_template_changed)
        self.template_preset_combo.currentIndexChanged.connect(self._on_organize_template_preset_changed)
        self.apply_checkbox.stateChanged.connect(self._refresh_summary_cards)
        self.copy_radio.toggled.connect(self._refresh_summary_cards)
        self.move_radio.toggled.connect(self._refresh_summary_cards)
        self.source_list.itemSelectionChanged.connect(self._refresh_source_details)
        self.rename_source_list.itemSelectionChanged.connect(self._refresh_rename_source_details)
        self.duplicates_source_list.itemSelectionChanged.connect(self._refresh_duplicates_source_details)
        self.workflow_source_list.itemSelectionChanged.connect(self._refresh_workflow_source_details)
        self.rename_template_input.textChanged.connect(self._on_rename_template_changed)
        self.rename_template_preset_combo.currentIndexChanged.connect(self._on_rename_template_preset_changed)
        self.rename_apply_checkbox.stateChanged.connect(self._refresh_rename_summary_cards)
        self.workflow_duplicates_step_card.button.clicked.connect(self._open_duplicates_from_workflow)
        self.workflow_organize_step_card.button.clicked.connect(self._open_organize_from_workflow)
        self.workflow_rename_step_card.button.clicked.connect(self._open_rename_from_workflow)

    def _set_current_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        button_states = {
            self.home_button: index == 0,
            self.workflow_button: index == 1,
            self.organize_button: index == 2,
            self.rename_button: index == 3,
            self.duplicates_button: index == 4,
        }
        for button, active in button_states.items():
            button.setProperty("variant", None if active else "secondary")
            button.style().unpolish(button)
            button.style().polish(button)

    def _current_guided_problem_key(self) -> str:
        data = self.guided_problem_combo.currentData()
        return str(data) if data else "full_cleanup"

    def _guided_problem_description(self, key: str) -> str:
        for item in GUIDED_PROBLEMS:
            if item["key"] == key:
                return item["description"]
        return GUIDED_PROBLEMS[0]["description"]

    def _update_guided_problem_hint(self) -> None:
        key = self._current_guided_problem_key()
        self.guided_problem_hint_label.setText(self._guided_problem_description(key))

    def _reset_workflow_state(self) -> None:
        self.workflow_step_statuses = {
            "duplicates": "Pending",
            "organize": "Pending",
            "rename": "Pending",
        }
        self.workflow_current_step = "Setup"

    def _prepare_guided_problem(self, problem_key: str) -> None:
        self.workflow_selected_problem = problem_key
        self._reset_workflow_state()
        if problem_key == "ready_for_sorting":
            self.workflow_step_statuses["duplicates"] = "Skipped"
        elif problem_key == "ready_for_rename":
            self.workflow_step_statuses["duplicates"] = "Skipped"
            self.workflow_step_statuses["organize"] = "Skipped"
        elif problem_key == "exact_duplicates_only":
            self.workflow_step_statuses["organize"] = "Optional"
            self.workflow_step_statuses["rename"] = "Optional"
        self.workflow_mode_hint_label.setText(self._guided_problem_description(problem_key))
        self._refresh_workflow_summary_cards()

    def _start_from_home_problem(self) -> None:
        problem_key = self._current_guided_problem_key()
        self._prepare_guided_problem(problem_key)

        if problem_key == "ready_for_rename":
            suggestion = self._current_rename_suggestion()
            if suggestion:
                self._use_current_target_for_rename()
                self.workflow_current_step = "Rename"
                self._refresh_workflow_summary_cards()
                self._set_current_page(3)
                self.status_bar.showMessage("Guided path opened at rename")
                return

        if problem_key == "exact_duplicates_only":
            if self._workflow_source_dirs():
                self._apply_workflow_setup_to_duplicates()
                self.workflow_current_step = "Duplicates"
                self._refresh_workflow_summary_cards()
                self._set_current_page(4)
                self.status_bar.showMessage("Guided path opened at exact duplicates")
                return

        if problem_key == "ready_for_sorting" and self._workflow_source_dirs() and self._workflow_target_text():
            self._apply_workflow_setup_to_modules()
            self.workflow_current_step = "Organize"
            self._refresh_workflow_summary_cards()
            self._set_current_page(2)
            self.status_bar.showMessage("Guided path opened at organize")
            return

        if problem_key == "full_cleanup" and self._workflow_source_dirs() and self._workflow_target_text():
            self._apply_workflow_setup_to_modules()
            self.workflow_current_step = "Duplicates"
            self._refresh_workflow_summary_cards()
            self._set_current_page(4)
            self.status_bar.showMessage("Guided path opened at duplicates")
            return

        self._set_current_page(1)
        self.status_bar.showMessage("Complete the workflow setup to continue")

    def _path_from_item(self, item: QListWidgetItem) -> Path:
        return Path(item.data(Qt.ItemDataRole.UserRole))

    def _add_path_item(self, list_widget: QListWidget, path: Path) -> None:
        normalized = str(path)
        existing = {self._path_from_item(list_widget.item(index)) for index in range(list_widget.count())}
        if path in existing:
            return
        item = QListWidgetItem(compact_path_label(path))
        item.setData(Qt.ItemDataRole.UserRole, normalized)
        item.setToolTip(normalized)
        list_widget.addItem(item)
        self._refresh_source_list_height(list_widget)

    def _populate_path_list(self, list_widget: QListWidget, source_dirs: list[str]) -> None:
        list_widget.clear()
        for raw_path in source_dirs:
            self._add_path_item(list_widget, Path(raw_path))
        self._refresh_source_list_height(list_widget)

    def _refresh_source_list_height(self, list_widget: QListWidget) -> None:
        row_height = list_widget.sizeHintForRow(0)
        if row_height <= 0:
            row_height = 40
        visible_rows = max(3, list_widget.count())
        frame = list_widget.frameWidth() * 2
        spacing = max(0, list_widget.spacing()) * max(0, visible_rows - 1)
        list_widget.setMinimumHeight((row_height * visible_rows) + frame + spacing + 10)

    def _refresh_source_details(self) -> None:
        self._refresh_list_details(self.source_list, self.source_details_label)

    def _refresh_rename_source_details(self) -> None:
        self._refresh_list_details(self.rename_source_list, self.rename_source_details_label)

    def _refresh_duplicates_source_details(self) -> None:
        self._refresh_list_details(self.duplicates_source_list, self.duplicates_source_details_label)

    def _refresh_workflow_source_details(self) -> None:
        self._refresh_list_details(self.workflow_source_list, self.workflow_source_details_label)

    def _refresh_list_details(self, list_widget: QListWidget, label: QLabel) -> None:
        selected_items = list_widget.selectedItems()
        if not selected_items:
            label.setText("No source folder selected.")
            return
        if len(selected_items) == 1:
            label.setText(str(self._path_from_item(selected_items[0])))
            return
        label.setText(f"{len(selected_items)} source folders selected.")

    def _sync_template_preset_combo(self, combo: QComboBox, template: str, presets: list[dict[str, str]]) -> None:
        label = template_preset_label(template, presets)
        index = combo.findText(label)
        if index >= 0 and combo.currentIndex() != index:
            combo.blockSignals(True)
            combo.setCurrentIndex(index)
            combo.blockSignals(False)

    def _is_custom_selected(self, combo: QComboBox) -> bool:
        return combo.currentText() == CUSTOM_TEMPLATE_LABEL

    def _update_organize_template_visibility(self) -> None:
        visible = self._is_custom_selected(self.template_preset_combo)
        self.organize_template_label.setVisible(visible)
        self.template_input.setVisible(visible)

    def _update_rename_template_visibility(self) -> None:
        visible = self._is_custom_selected(self.rename_template_preset_combo)
        self.rename_template_label.setVisible(visible)
        self.rename_template_input.setVisible(visible)
        self.rename_template_hint.setVisible(visible)

    def _on_organize_template_changed(self) -> None:
        self._sync_template_preset_combo(self.template_preset_combo, self.template_input.text(), ORGANIZE_TEMPLATE_PRESETS)
        self._update_organize_template_visibility()

    def _on_rename_template_changed(self) -> None:
        self._refresh_rename_summary_cards()
        self._sync_template_preset_combo(self.rename_template_preset_combo, self.rename_template_input.text(), RENAME_TEMPLATE_PRESETS)
        self._update_rename_template_visibility()

    def _on_organize_template_preset_changed(self, index: int) -> None:
        template = self.template_preset_combo.itemData(index)
        if isinstance(template, str):
            self.template_input.setText(template)
        self._update_organize_template_visibility()

    def _on_rename_template_preset_changed(self, index: int) -> None:
        template = self.rename_template_preset_combo.itemData(index)
        if isinstance(template, str):
            self.rename_template_input.setText(template)
        self._update_rename_template_visibility()

    def _on_target_changed(self) -> None:
        self._refresh_summary_cards()
        self._update_cross_module_suggestions()

    def _on_workflow_target_changed(self) -> None:
        self._refresh_workflow_summary_cards()
        self._update_cross_module_suggestions()

    def _workflow_source_dirs(self) -> list[str]:
        return [str(path) for path in self._collect_paths(self.workflow_source_list)]

    def _workflow_target_text(self) -> str:
        return self.workflow_target_input.text().strip()

    def _current_rename_suggestion(self) -> str:
        organize_target = self.target_input.text().strip()
        if organize_target:
            return organize_target
        return self._workflow_target_text()

    def _workflow_next_action_label(self) -> str:
        if not self._workflow_source_dirs() or not self._workflow_target_text():
            return "Complete setup"
        if self.workflow_step_statuses["duplicates"] == "Pending":
            return "Review duplicates"
        if self.workflow_step_statuses["organize"] == "Pending":
            return "Run organize"
        if self.workflow_step_statuses["rename"] == "Pending":
            return "Run rename"
        return "Review final result"

    def _refresh_summary_cards(self) -> None:
        source_count = self.source_list.count()
        self.sources_card.set_value(f"{source_count} folder" if source_count == 1 else f"{source_count} folders")
        target_text = self.target_input.text().strip()
        self.target_card.set_value((Path(target_text).name or target_text) if target_text else "Not set")
        self.mode_card.set_value("Move" if self.move_radio.isChecked() else "Copy")
        run_label = "Run" if self.apply_checkbox.isChecked() else "Pre-run"
        self.run_mode_card.set_value(run_label)
        self.run_button.setText(run_label)

    def _refresh_rename_summary_cards(self) -> None:
        source_count = self.rename_source_list.count()
        self.rename_sources_card.set_value(f"{source_count} folder" if source_count == 1 else f"{source_count} folders")
        template_text = self.rename_template_input.text().strip() or DEFAULT_RENAME_TEMPLATE
        self.rename_template_card.set_value(template_text if len(template_text) <= 30 else template_text[:27] + "...")
        run_label = "Run" if self.rename_apply_checkbox.isChecked() else "Pre-run"
        self.rename_run_mode_card.set_value(run_label)
        self.rename_run_button.setText(run_label)

    def _refresh_duplicates_summary_cards(self, groups: int | None = None, duplicate_files: int | None = None, extra_duplicates: int | None = None) -> None:
        source_count = self.duplicates_source_list.count()
        self.duplicates_sources_card.set_value(f"{source_count} folder" if source_count == 1 else f"{source_count} folders")
        if groups is not None:
            self.duplicates_groups_card.set_value(str(groups))
        if duplicate_files is not None:
            self.duplicates_files_card.set_value(str(duplicate_files))
        if extra_duplicates is not None:
            self.duplicates_extra_card.set_value(str(extra_duplicates))

    def _refresh_workflow_summary_cards(self) -> None:
        source_count = self.workflow_source_list.count()
        self.workflow_sources_card.set_value(f"{source_count} folder" if source_count == 1 else f"{source_count} folders")
        target_text = self._workflow_target_text()
        self.workflow_target_card.set_value((Path(target_text).name or target_text) if target_text else "Not set")
        self.workflow_status_card.set_value(self.workflow_current_step)
        self.workflow_next_card.set_value(self._workflow_next_action_label())
        self.workflow_duplicates_step_card.set_status(self.workflow_step_statuses["duplicates"])
        self.workflow_organize_step_card.set_status(self.workflow_step_statuses["organize"])
        self.workflow_rename_step_card.set_status(self.workflow_step_statuses["rename"])
        self.workflow_mode_hint_label.setText(self._guided_problem_description(self.workflow_selected_problem))

    def _set_workflow_step_status(self, step: str, value: str) -> None:
        self.workflow_step_statuses[step] = value
        self._refresh_workflow_summary_cards()

    def _update_cross_module_suggestions(self) -> None:
        workflow_sources = self._workflow_source_dirs()
        workflow_target = self._workflow_target_text()
        workflow_target_label = (Path(workflow_target).name or workflow_target) if workflow_target else "not set"
        self.organize_workflow_hint_label.setText(
            f"Workflow suggestion: {len(workflow_sources)} source(s), target {workflow_target_label}."
            if workflow_sources or workflow_target
            else "No workflow setup connected yet."
        )
        self.duplicates_workflow_hint_label.setText(
            f"Workflow sources ready: {len(workflow_sources)} folder(s)."
            if workflow_sources
            else "No workflow source set linked yet."
        )
        rename_target = self._current_rename_suggestion()
        if rename_target:
            self.rename_target_hint_label.setText(f"Suggested source: {rename_target}")
            self.rename_use_target_button.setEnabled(True)
        else:
            self.rename_target_hint_label.setText("No suggested source from the previous target yet.")
            self.rename_use_target_button.setEnabled(False)

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
        rename_template_text = str(self.app_settings.get("rename_template", DEFAULT_RENAME_TEMPLATE)).strip() or DEFAULT_RENAME_TEMPLATE
        workflow_target_text = str(self.app_settings.get("workflow_target_dir", "")).strip()
        workflow_sources_raw = self.app_settings.get("workflow_source_dirs", [])
        saved_problem = str(self.app_settings.get("guided_problem", "full_cleanup")).strip() or "full_cleanup"

        if target_text:
            self.target_input.setText(target_text)
        self.template_input.setText(template_text)
        self.rename_template_input.setText(rename_template_text)
        if workflow_target_text:
            self.workflow_target_input.setText(workflow_target_text)
        if isinstance(workflow_sources_raw, list):
            self._populate_path_list(self.workflow_source_list, [str(value) for value in workflow_sources_raw])
        problem_index = self.guided_problem_combo.findData(saved_problem)
        if problem_index >= 0:
            self.guided_problem_combo.setCurrentIndex(problem_index)
            self.workflow_selected_problem = saved_problem
        if exiftool_text and Path(exiftool_text).is_file():
            self.exiftool_input.setText(exiftool_text)
        else:
            auto_path = resolve_exiftool_path()
            if auto_path is not None:
                self.exiftool_input.setText(str(auto_path))
        self._refresh_import_set_combo()
        self._sync_template_preset_combo(self.template_preset_combo, self.template_input.text(), ORGANIZE_TEMPLATE_PRESETS)
        self._sync_template_preset_combo(self.rename_template_preset_combo, self.rename_template_input.text(), RENAME_TEMPLATE_PRESETS)
        self._update_organize_template_visibility()
        self._update_rename_template_visibility()

    def _save_settings(self) -> None:
        updated = dict(self.app_settings)
        updated["target_dir"] = self.target_input.text().strip()
        updated["exiftool_path"] = self.exiftool_input.text().strip()
        updated["target_template"] = self.template_input.text().strip() or DEFAULT_TARGET_TEMPLATE
        updated["rename_template"] = self.rename_template_input.text().strip() or DEFAULT_RENAME_TEMPLATE
        updated["workflow_target_dir"] = self._workflow_target_text()
        updated["workflow_source_dirs"] = self._workflow_source_dirs()
        updated["guided_problem"] = self._current_guided_problem_key()
        save_app_settings(updated)
        self.app_settings = updated

    def closeEvent(self, event) -> None:  # pragma: no cover - GUI runtime
        self._save_settings()
        super().closeEvent(event)

    def _set_run_state(self, running: bool) -> None:
        enabled = not running
        for widget in [
            self.guided_problem_combo,
            self.guided_start_button,
            self.guided_workflow_board_button,
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
            self.template_preset_combo,
            self.template_input,
            self.apply_checkbox,
            self.copy_radio,
            self.move_radio,
            self.source_list,
            self.target_browse_button,
            self.exiftool_browse_button,
            self.open_target_button,
            self.rename_run_button,
            self.rename_clear_results_button,
            self.rename_add_source_button,
            self.rename_remove_source_button,
            self.rename_clear_sources_button,
            self.rename_source_list,
            self.rename_template_preset_combo,
            self.rename_template_input,
            self.rename_apply_checkbox,
            self.duplicates_run_button,
            self.duplicates_clear_results_button,
            self.duplicates_add_source_button,
            self.duplicates_remove_source_button,
            self.duplicates_clear_sources_button,
            self.duplicates_source_list,
            self.workflow_add_source_button,
            self.workflow_remove_source_button,
            self.workflow_clear_sources_button,
            self.workflow_target_input,
            self.workflow_target_browse_button,
            self.workflow_apply_button,
            self.workflow_start_button,
            self.home_button,
            self.workflow_button,
            self.organize_button,
            self.rename_button,
            self.duplicates_button,
            self.organize_use_workflow_button,
            self.rename_use_target_button,
            self.duplicates_use_workflow_button,
        ]:
            widget.setEnabled(enabled)
        QApplication.processEvents()

    def _handle_progress(self, message: str) -> None:
        self.status_bar.showMessage(message)
        QApplication.processEvents()

    def _resize_result_columns(self, table: QTableWidget) -> None:
        for column in range(table.columnCount()):
            table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

    def _make_result_item(self, display_value: str, tooltip_value: str, *, center: bool = False) -> QTableWidgetItem:
        item = QTableWidgetItem(display_value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setToolTip(tooltip_value)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _format_action(self, action: str) -> str:
        return ACTION_LABELS.get(action, action.replace("-", " ").title())

    def _save_import_set(self) -> None:
        source_dirs = [str(path) for path in self._collect_paths(self.source_list)]
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
        self._populate_path_list(self.source_list, item["source_dirs"])
        self.target_input.setText(item["target_dir"])
        self.template_input.setText(item["target_template"])
        self._refresh_summary_cards()
        self._refresh_source_details()
        self._update_cross_module_suggestions()
        self.status_bar.showMessage(f"Loaded import set: {item['name']}")

    def _delete_import_set(self) -> None:
        selected_name = self.import_set_combo.currentData()
        if not selected_name:
            return
        reply = QMessageBox.question(self, "Delete import set", f"Delete '{selected_name}'?")
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
        self._add_path_item(self.source_list, Path(selected))
        self.status_bar.showMessage(f"Added source folder: {selected}")
        self._refresh_summary_cards()

    def _remove_selected_sources(self) -> None:
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))
        self._refresh_source_list_height(self.source_list)
        self.status_bar.showMessage("Selected source folders removed")
        self._refresh_summary_cards()
        self._refresh_source_details()

    def _clear_sources(self) -> None:
        self.source_list.clear()
        self._refresh_source_list_height(self.source_list)
        self.status_bar.showMessage("Source folder list cleared")
        self._refresh_summary_cards()
        self._refresh_source_details()

    def _rename_add_source_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not selected:
            return
        self._add_path_item(self.rename_source_list, Path(selected))
        self.status_bar.showMessage(f"Added source folder: {selected}")
        self._refresh_rename_summary_cards()

    def _rename_remove_selected_sources(self) -> None:
        for item in self.rename_source_list.selectedItems():
            self.rename_source_list.takeItem(self.rename_source_list.row(item))
        self._refresh_source_list_height(self.rename_source_list)
        self.status_bar.showMessage("Selected source folders removed")
        self._refresh_rename_summary_cards()
        self._refresh_rename_source_details()

    def _rename_clear_sources(self) -> None:
        self.rename_source_list.clear()
        self._refresh_source_list_height(self.rename_source_list)
        self.status_bar.showMessage("Source folder list cleared")
        self._refresh_rename_summary_cards()
        self._refresh_rename_source_details()

    def _duplicates_add_source_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not selected:
            return
        self._add_path_item(self.duplicates_source_list, Path(selected))
        self.status_bar.showMessage(f"Added source folder: {selected}")
        self._refresh_duplicates_summary_cards()

    def _duplicates_remove_selected_sources(self) -> None:
        for item in self.duplicates_source_list.selectedItems():
            self.duplicates_source_list.takeItem(self.duplicates_source_list.row(item))
        self._refresh_source_list_height(self.duplicates_source_list)
        self.status_bar.showMessage("Selected source folders removed")
        self._refresh_duplicates_summary_cards()
        self._refresh_duplicates_source_details()

    def _duplicates_clear_sources(self) -> None:
        self.duplicates_source_list.clear()
        self._refresh_source_list_height(self.duplicates_source_list)
        self.status_bar.showMessage("Source folder list cleared")
        self._refresh_duplicates_summary_cards()
        self._refresh_duplicates_source_details()

    def _workflow_add_source_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not selected:
            return
        self._add_path_item(self.workflow_source_list, Path(selected))
        self.status_bar.showMessage(f"Added source folder: {selected}")
        self._refresh_workflow_summary_cards()
        self._update_cross_module_suggestions()

    def _workflow_remove_selected_sources(self) -> None:
        for item in self.workflow_source_list.selectedItems():
            self.workflow_source_list.takeItem(self.workflow_source_list.row(item))
        self._refresh_source_list_height(self.workflow_source_list)
        self.status_bar.showMessage("Selected source folders removed")
        self._refresh_workflow_summary_cards()
        self._refresh_workflow_source_details()
        self._update_cross_module_suggestions()

    def _workflow_clear_sources(self) -> None:
        self.workflow_source_list.clear()
        self._refresh_source_list_height(self.workflow_source_list)
        self.status_bar.showMessage("Source folder list cleared")
        self._refresh_workflow_summary_cards()
        self._refresh_workflow_source_details()
        self._update_cross_module_suggestions()

    def _choose_target_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select target folder")
        if selected:
            self.target_input.setText(str(Path(selected)))

    def _choose_workflow_target_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select final target folder")
        if selected:
            self.workflow_target_input.setText(str(Path(selected)))
            self.status_bar.showMessage(f"Workflow target set: {selected}")

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

    def _validate_workflow_setup(self) -> tuple[list[Path], str] | None:
        source_dirs = self._collect_paths(self.workflow_source_list)
        target_text = self._workflow_target_text()
        if not source_dirs:
            QMessageBox.information(self, "Workflow", "Add at least one source folder first.")
            return None
        invalid_sources = [path for path in source_dirs if not path.is_dir()]
        if invalid_sources:
            QMessageBox.information(self, "Workflow", "The following workflow source folders are invalid:\n- " + "\n- ".join(str(path) for path in invalid_sources))
            return None
        if not target_text:
            QMessageBox.information(self, "Workflow", "Select a target folder first.")
            return None
        return source_dirs, target_text

    def _apply_workflow_setup_to_modules(self) -> None:
        validated = self._validate_workflow_setup()
        if validated is None:
            return
        source_dirs, target_text = validated
        source_strings = [str(path) for path in source_dirs]
        self._populate_path_list(self.source_list, source_strings)
        self._populate_path_list(self.duplicates_source_list, source_strings)
        self.target_input.setText(target_text)
        self._refresh_summary_cards()
        self._refresh_duplicates_summary_cards()
        self._update_cross_module_suggestions()
        self._save_settings()
        self.status_bar.showMessage("Workflow setup applied to organize and duplicates")

    def _apply_workflow_setup_to_duplicates(self) -> None:
        source_strings = self._workflow_source_dirs()
        if not source_strings:
            QMessageBox.information(self, "Duplicates", "No workflow source folders are available yet.")
            return
        self._populate_path_list(self.duplicates_source_list, source_strings)
        self._refresh_duplicates_summary_cards()
        self._refresh_duplicates_source_details()
        self.status_bar.showMessage("Workflow source folders applied to duplicates")

    def _use_current_target_for_rename(self) -> None:
        suggestion = self._current_rename_suggestion()
        if not suggestion:
            QMessageBox.information(self, "Rename", "No previous target is available yet.")
            return
        self._populate_path_list(self.rename_source_list, [suggestion])
        self._refresh_rename_summary_cards()
        self._refresh_rename_source_details()
        self.status_bar.showMessage("Previous target applied as rename source")

    def _start_guided_workflow(self) -> None:
        validated = self._validate_workflow_setup()
        if validated is None:
            return
        self._apply_workflow_setup_to_modules()
        problem_key = self.workflow_selected_problem
        if problem_key == "ready_for_rename":
            self.workflow_current_step = "Rename"
            self._use_current_target_for_rename()
            self._set_current_page(3)
            self.status_bar.showMessage("Guided workflow started — continue with rename")
            return
        if problem_key == "ready_for_sorting":
            self.workflow_current_step = "Organize"
            self._refresh_workflow_summary_cards()
            self._set_current_page(2)
            self.status_bar.showMessage("Guided workflow started — continue with organize")
            return
        self.workflow_current_step = "Duplicates"
        self._set_workflow_step_status("duplicates", "Ready")
        self._refresh_workflow_summary_cards()
        self._set_current_page(4)
        self.status_bar.showMessage("Guided workflow started — continue with duplicates")

    def _open_duplicates_from_workflow(self) -> None:
        self._apply_workflow_setup_to_duplicates()
        self.workflow_current_step = "Duplicates"
        self._refresh_workflow_summary_cards()
        self._set_current_page(4)

    def _open_organize_from_workflow(self) -> None:
        self._apply_workflow_setup_to_modules()
        self.workflow_current_step = "Organize"
        self._refresh_workflow_summary_cards()
        self._set_current_page(2)

    def _open_rename_from_workflow(self) -> None:
        self._use_current_target_for_rename()
        self.workflow_current_step = "Rename"
        self._refresh_workflow_summary_cards()
        self._set_current_page(3)

    def _clear_results(self) -> None:
        self.results_table.setRowCount(0)
        self._resize_result_columns(self.results_table)
        self.status_bar.showMessage("Results cleared")

    def _rename_clear_results(self) -> None:
        self.rename_results_table.setRowCount(0)
        self._resize_result_columns(self.rename_results_table)
        self.status_bar.showMessage("Results cleared")

    def _duplicates_clear_results(self) -> None:
        self.duplicates_results_table.setRowCount(0)
        self._resize_result_columns(self.duplicates_results_table)
        self._refresh_duplicates_summary_cards(groups=0, duplicate_files=0, extra_duplicates=0)
        self.status_bar.showMessage("Results cleared")

    def _collect_paths(self, list_widget: QListWidget) -> list[Path]:
        return [self._path_from_item(list_widget.item(index)) for index in range(list_widget.count())]

    def _run(self) -> None:
        source_dirs = self._collect_paths(self.source_list)
        target_text = self.target_input.text().strip()
        exiftool_text = self.exiftool_input.text().strip()
        is_prerun = not self.apply_checkbox.isChecked()

        if not source_dirs:
            QMessageBox.critical(self, "Error", "Please add at least one source folder.")
            return
        invalid_sources = [path for path in source_dirs if not path.is_dir()]
        if invalid_sources:
            QMessageBox.critical(self, "Error", "The following source folders are invalid:\n- " + "\n- ".join(str(path) for path in invalid_sources))
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
            dry_run=is_prerun,
            mode="move" if self.move_radio.isChecked() else "copy",
            exiftool_path=exiftool_path,
        )

        self._save_settings()
        self.results_table.setRowCount(0)
        self._resize_result_columns(self.results_table)
        self.status_bar.showMessage("Preparing organizer run ...")
        self._set_run_state(True)
        try:
            results = organize_media(config, progress_callback=self._handle_progress)
        except Exception as exc:  # pragma: no cover - GUI fallback
            QMessageBox.critical(self, "Error", str(exc))
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
                (self._format_action(entry.action), entry.action, True),
                (entry.source.name, str(entry.source), False),
                (entry.source.parent.name or str(entry.source.parent), str(entry.source.parent), False),
                (target_value, target_tooltip, False),
                (entry.reason or "-", entry.reason or "-", False),
            ]
            for column_index, (display_value, tooltip_value, center) in enumerate(values):
                self.results_table.setItem(row_index, column_index, self._make_result_item(display_value, tooltip_value, center=center))
        self._resize_result_columns(self.results_table)
        self.workflow_target_input.setText(target_text)
        self._set_workflow_step_status("organize", f"Done ({results.organized})")
        self.workflow_current_step = "Rename"
        self._refresh_workflow_summary_cards()
        self._use_current_target_for_rename()

        if is_prerun:
            self.apply_checkbox.setChecked(True)
            self.status_bar.showMessage(
                f"Pre-run finished | Processed: {results.processed} | Planned: {results.organized} | Errors: {results.errors} | Apply enabled"
            )
        else:
            self.status_bar.showMessage(
                f"Run finished | Processed: {results.processed} | Executed: {results.organized} | Skipped: {results.skipped} | Errors: {results.errors}"
            )

    def _run_rename(self) -> None:
        source_dirs = self._collect_paths(self.rename_source_list)
        exiftool_text = self.exiftool_input.text().strip()
        is_prerun = not self.rename_apply_checkbox.isChecked()

        if not source_dirs:
            QMessageBox.critical(self, "Error", "Please add at least one source folder.")
            return
        invalid_sources = [path for path in source_dirs if not path.is_dir()]
        if invalid_sources:
            QMessageBox.critical(self, "Error", "The following source folders are invalid:\n- " + "\n- ".join(str(path) for path in invalid_sources))
            return

        config = RenameConfig(
            source_dirs=source_dirs,
            template=self.rename_template_input.text().strip() or DEFAULT_RENAME_TEMPLATE,
            dry_run=is_prerun,
            exiftool_path=Path(exiftool_text) if exiftool_text else None,
        )

        self._save_settings()
        self.rename_results_table.setRowCount(0)
        self._resize_result_columns(self.rename_results_table)
        self.status_bar.showMessage("Preparing rename run ...")
        self._set_run_state(True)
        try:
            results = rename_media(config, progress_callback=self._handle_progress)
        except Exception as exc:  # pragma: no cover - GUI fallback
            QMessageBox.critical(self, "Error", str(exc))
            self.status_bar.showMessage("An error occurred")
            return
        finally:
            self._set_run_state(False)

        self.rename_results_table.setRowCount(len(results.entries))
        for row_index, entry in enumerate(results.entries):
            target_name = entry.target.name if entry.target is not None else "-"
            folder_value = entry.source.parent.name or str(entry.source.parent)
            values = [
                (self._format_action(entry.action), entry.action, True),
                (entry.source.name, str(entry.source), False),
                (target_name, str(entry.target) if entry.target is not None else "-", False),
                (folder_value, str(entry.source.parent), False),
                (entry.reason or "-", entry.reason or "-", False),
            ]
            for column_index, (display_value, tooltip_value, center) in enumerate(values):
                self.rename_results_table.setItem(row_index, column_index, self._make_result_item(display_value, tooltip_value, center=center))
        self._resize_result_columns(self.rename_results_table)
        self._set_workflow_step_status("rename", f"Done ({results.renamed})")
        self.workflow_current_step = "Finished"
        self._refresh_workflow_summary_cards()

        if is_prerun:
            self.rename_apply_checkbox.setChecked(True)
            self.status_bar.showMessage(
                f"Pre-run finished | Processed: {results.processed} | Planned: {results.renamed} | Errors: {results.errors} | Apply enabled"
            )
        else:
            self.status_bar.showMessage(
                f"Run finished | Processed: {results.processed} | Executed: {results.renamed} | Skipped: {results.skipped} | Errors: {results.errors}"
            )

    def _run_duplicates(self) -> None:
        source_dirs = self._collect_paths(self.duplicates_source_list)
        if not source_dirs:
            QMessageBox.critical(self, "Error", "Please add at least one source folder.")
            return
        invalid_sources = [path for path in source_dirs if not path.is_dir()]
        if invalid_sources:
            QMessageBox.critical(self, "Error", "The following source folders are invalid:\n- " + "\n- ".join(str(path) for path in invalid_sources))
            return

        config = DuplicateScanConfig(source_dirs=source_dirs)
        self.duplicates_results_table.setRowCount(0)
        self._resize_result_columns(self.duplicates_results_table)
        self._refresh_duplicates_summary_cards(groups=0, duplicate_files=0, extra_duplicates=0)
        self.status_bar.showMessage("Preparing duplicate scan ...")
        self._set_run_state(True)
        try:
            result = scan_exact_duplicates(config, progress_callback=self._handle_progress)
        except Exception as exc:  # pragma: no cover - GUI fallback
            QMessageBox.critical(self, "Error", str(exc))
            self.status_bar.showMessage("An error occurred")
            return
        finally:
            self._set_run_state(False)

        row_count = sum(len(group.files) for group in result.exact_groups)
        self.duplicates_results_table.setRowCount(row_count)
        row_index = 0
        for group_index, group in enumerate(result.exact_groups, start=1):
            note = f"{len(group.files)} files | same name: {'yes' if group.same_name else 'no'} | same suffix: {'yes' if group.same_suffix else 'no'}"
            size_label = format_file_size(group.file_size)
            for path in group.files:
                values = [
                    (str(group_index), str(group_index), True),
                    (path.name, str(path), False),
                    (path.parent.name or str(path.parent), str(path.parent), False),
                    (size_label, str(group.file_size), True),
                    (note, note, False),
                ]
                for column_index, (display_value, tooltip_value, center) in enumerate(values):
                    self.duplicates_results_table.setItem(row_index, column_index, self._make_result_item(display_value, tooltip_value, center=center))
                row_index += 1

        self._resize_result_columns(self.duplicates_results_table)
        self._refresh_duplicates_summary_cards(
            groups=len(result.exact_groups),
            duplicate_files=result.exact_duplicate_files,
            extra_duplicates=result.exact_duplicates,
        )
        self._set_workflow_step_status("duplicates", f"Done ({len(result.exact_groups)} groups)")
        self.workflow_current_step = "Organize"
        self._refresh_workflow_summary_cards()
        self.status_bar.showMessage(
            f"Duplicate scan finished | Scanned: {result.scanned_files} | Exact groups: {len(result.exact_groups)} | Duplicate files: {result.exact_duplicate_files} | Extra duplicates: {result.exact_duplicates} | Errors: {result.errors}"
        )


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = MediaManagerWindow()
    window.show()
    return app.exec()
