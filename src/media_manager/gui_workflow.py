from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .gui import ProblemCard
from .gui_review import APP_STYLESHEET, MediaManagerWindow as ReviewWindow
from .workflow_progress import (
    workflow_completed_steps,
    workflow_next_required_step,
    workflow_progress_percent,
    workflow_required_steps,
)

STRINGS = {
    "en": {
        "nav_subtitle": "Guided first. Manual when needed.",
        "nav_home": "Home",
        "nav_workflow": "Workflow",
        "nav_organize": "Organize",
        "nav_rename": "Rename",
        "nav_duplicates": "Duplicates",
        "language_tooltip": "Switch language",
        "home_title": "Answer a few quick questions",
        "home_subtitle": "This guided setup prepares the right workflow before you touch your files.",
        "home_step": "Question {current} of {total}",
        "home_dismiss": "Dismiss",
        "home_back": "Back",
        "home_next": "Next",
        "home_start": "Start now",
        "home_restart": "Start guided questionnaire",
        "home_info_title": "How it works",
        "home_info_body": "The questionnaire prepares the workflow, file-handling mode and duplicate preference. Then you add source folders and a target folder in the workflow page. Use the side navigation only when you want to work manually.",
        "wizard_problem_title": "What best describes your current situation?",
        "wizard_problem_subtitle": "Choose the option that matches your folders today.",
        "wizard_mode_title": "What should happen to the original files?",
        "wizard_mode_subtitle": "Copy is safer. Move is cleaner once you trust the result.",
        "wizard_mode_copy": "Copy files to the target and keep the originals",
        "wizard_mode_move": "Move files to the target",
        "wizard_duplicates_title": "When exact duplicates are found, which file should be kept by default?",
        "wizard_duplicates_subtitle": "You can still change every exact duplicate decision later in the review table.",
        "wizard_keep_first": "Keep the first stable match",
        "wizard_keep_newest": "Keep the newest file",
        "wizard_keep_oldest": "Keep the oldest file",
        "wizard_summary_title": "Ready to continue",
        "wizard_summary_subtitle": "Review your choices and continue to the guided workflow board.",
        "wizard_summary_text": "Workflow: {problem}\nFile handling: {mode}\nExact duplicates: {keep_rule}\nNext: add source folders and a target folder, then start the guided workflow.",
        "workflow_board_title": "Guided workflow board",
        "workflow_board_subtitle": "Set sources and target once. Then move through the recommended path with carried-over suggestions.",
        "workflow_hint": "Guided workflow: review exact duplicates, then organize into the target, then rename inside that target.",
        "workflow_progress_title": "Workflow progress",
        "workflow_progress_done": "Workflow complete. {done}/{total} required steps finished.",
        "workflow_progress_next": "{done}/{total} required steps finished. Next: {next_step}.",
        "step_duplicates": "1. Duplicates",
        "step_organize": "2. Organize",
        "step_rename": "3. Rename",
        "status_pending": "Pending",
        "status_ready": "Ready",
        "status_done": "Done",
        "status_skipped": "Skipped",
        "status_optional": "Optional",
        "status_not_required": "Not required",
        "step_setup": "Setup",
        "step_finished": "Finished",
        "next_duplicates": "duplicates",
        "next_organize": "organize",
        "next_rename": "rename",
        "group_guided_mode": "Guided mode",
        "group_workflow_setup": "Workflow setup",
        "group_recommended_path": "Recommended path",
        "group_review_apply": "Review and apply",
        "group_source_folders": "Source folders",
        "group_target_options": "Target and options",
        "group_rename_options": "Rename options",
        "group_run": "Run",
        "group_results": "Results",
        "group_current_situation": "Current situation",
        "workflow_apply_modules": "Apply to modules",
        "workflow_start_guided": "Start guided workflow",
        "workflow_browse_target": "Browse target",
        "button_add": "Add",
        "button_remove": "Remove",
        "button_clear": "Clear",
        "button_save_set": "Save set",
        "button_load": "Load",
        "button_delete": "Delete",
        "button_use_workflow": "Use workflow setup",
        "button_use_previous_target": "Use previous target",
        "button_browse": "Browse",
        "button_open_target": "Open target",
        "button_clear_results": "Clear results",
        "button_scan": "Scan",
        "button_keep_selected": "Keep selected",
        "button_keep_newest": "Keep newest",
        "button_keep_oldest": "Keep oldest",
        "button_reset_group": "Reset group",
        "button_open_selected_folder": "Open selected folder",
        "button_send_recycle": "Send marked files to Recycle Bin",
        "mode_copy_short": "Copy",
        "mode_move_short": "Move",
        "run_label": "Run",
        "prerun_label": "Pre-run",
        "summary_sources": "Sources",
        "summary_target": "Target",
        "summary_mode": "Mode",
        "summary_run": "Run",
        "summary_template": "Template",
        "summary_module": "Module",
        "summary_groups": "Exact groups",
        "summary_files_in_groups": "Files in groups",
        "summary_marked_remove": "Marked remove",
        "summary_current_step": "Current step",
        "summary_next_action": "Next action",
        "problem_full_cleanup_label": "My folders are messy and I want the cleanest full result",
        "problem_full_cleanup_desc": "Recommended path: Duplicates → Organize → Rename. Best choice for mixed sources and unclear folder quality.",
        "problem_ready_for_sorting_label": "Duplicates are already handled, now I need clean sorting",
        "problem_ready_for_sorting_desc": "Recommended path: Organize → Rename. Use this when duplicate cleanup is already done outside the app.",
        "problem_ready_for_rename_label": "The files are already in the right folder, I only need better names",
        "problem_ready_for_rename_desc": "Recommended path: Rename only. The previous target folder is used as the likely rename source.",
        "problem_exact_duplicates_only_label": "I only want to inspect exact duplicates right now",
        "problem_exact_duplicates_only_desc": "Recommended path: Duplicates only. Exact means 100% byte-identical, not visually similar.",
        "problem_select": "Choose",
        "problem_selected": "Selected",
        "action_preview_copy": "Preview copy",
        "action_preview_move": "Preview move",
        "action_copied": "Copied",
        "action_moved": "Moved",
        "action_preview_rename": "Preview rename",
        "action_renamed": "Renamed",
        "action_unchanged": "Unchanged",
        "action_error": "Error",
        "decision_keep": "Keep",
        "decision_remove": "Remove",
    },
    "de": {
        "nav_subtitle": "Zuerst geführt. Manuell nur wenn nötig.",
        "nav_home": "Start",
        "nav_workflow": "Ablauf",
        "nav_organize": "Sortieren",
        "nav_rename": "Umbenennen",
        "nav_duplicates": "Duplikate",
        "language_tooltip": "Sprache wechseln",
        "home_title": "Beantworte kurz ein paar Fragen",
        "home_subtitle": "Diese geführte Einrichtung bereitet den passenden Ablauf vor, bevor du an deine Dateien gehst.",
        "home_step": "Frage {current} von {total}",
        "home_dismiss": "Ausblenden",
        "home_back": "Zurück",
        "home_next": "Weiter",
        "home_start": "Jetzt starten",
        "home_restart": "Geführte Umfrage starten",
        "home_info_title": "So funktioniert es",
        "home_info_body": "Die Umfrage bereitet den Ablauf, den Datei-Modus und die Duplikat-Vorgabe vor. Danach wählst du im Workflow Quellenordner und Zielordner aus. Die Seitenleiste nutzt du nur, wenn du bewusst manuell arbeiten willst.",
        "wizard_problem_title": "Welche Situation passt gerade am besten?",
        "wizard_problem_subtitle": "Wähle die Option, die am besten zu deinen Ordnern passt.",
        "wizard_mode_title": "Was soll mit den Originaldateien passieren?",
        "wizard_mode_subtitle": "Kopieren ist sicherer. Verschieben ist sauberer, sobald du dem Ergebnis vertraust.",
        "wizard_mode_copy": "Dateien ins Ziel kopieren und Originale behalten",
        "wizard_mode_move": "Dateien ins Ziel verschieben",
        "wizard_duplicates_title": "Wenn exakte Duplikate gefunden werden, welche Datei soll standardmäßig behalten werden?",
        "wizard_duplicates_subtitle": "Jede Entscheidung kann später in der Review-Tabelle noch geändert werden.",
        "wizard_keep_first": "Ersten stabilen Treffer behalten",
        "wizard_keep_newest": "Neueste Datei behalten",
        "wizard_keep_oldest": "Älteste Datei behalten",
        "wizard_summary_title": "Bereit zum Weitergehen",
        "wizard_summary_subtitle": "Prüfe kurz deine Auswahl und gehe dann in den geführten Workflow.",
        "wizard_summary_text": "Ablauf: {problem}\nDatei-Behandlung: {mode}\nExakte Duplikate: {keep_rule}\nAls Nächstes: Quellenordner und Zielordner auswählen und dann den geführten Workflow starten.",
        "workflow_board_title": "Geführtes Workflow-Board",
        "workflow_board_subtitle": "Quellen und Ziel einmal festlegen. Danach Schritt für Schritt mit übernommenen Vorschlägen arbeiten.",
        "workflow_hint": "Geführter Ablauf: zuerst exakte Duplikate prüfen, dann ins Ziel sortieren, danach im Ziel umbenennen.",
        "workflow_progress_title": "Ablauf-Fortschritt",
        "workflow_progress_done": "Ablauf abgeschlossen. {done}/{total} nötige Schritte erledigt.",
        "workflow_progress_next": "{done}/{total} nötige Schritte erledigt. Nächster Schritt: {next_step}.",
        "step_duplicates": "1. Duplikate",
        "step_organize": "2. Sortieren",
        "step_rename": "3. Umbenennen",
        "status_pending": "Ausstehend",
        "status_ready": "Bereit",
        "status_done": "Fertig",
        "status_skipped": "Übersprungen",
        "status_optional": "Optional",
        "status_not_required": "Nicht nötig",
        "step_setup": "Einrichtung",
        "step_finished": "Fertig",
        "next_duplicates": "Duplikate",
        "next_organize": "Sortieren",
        "next_rename": "Umbenennen",
        "group_guided_mode": "Geführter Modus",
        "group_workflow_setup": "Workflow-Einrichtung",
        "group_recommended_path": "Empfohlener Ablauf",
        "group_review_apply": "Prüfen und anwenden",
        "group_source_folders": "Quellordner",
        "group_target_options": "Ziel und Optionen",
        "group_rename_options": "Umbenennen-Optionen",
        "group_run": "Ausführen",
        "group_results": "Ergebnisse",
        "group_current_situation": "Aktuelle Situation",
        "workflow_apply_modules": "An Module übergeben",
        "workflow_start_guided": "Geführten Workflow starten",
        "workflow_browse_target": "Ziel wählen",
        "button_add": "Hinzufügen",
        "button_remove": "Entfernen",
        "button_clear": "Leeren",
        "button_save_set": "Set speichern",
        "button_load": "Laden",
        "button_delete": "Löschen",
        "button_use_workflow": "Workflow übernehmen",
        "button_use_previous_target": "Vorheriges Ziel nutzen",
        "button_browse": "Wählen",
        "button_open_target": "Ziel öffnen",
        "button_clear_results": "Ergebnisse leeren",
        "button_scan": "Scannen",
        "button_keep_selected": "Auswahl behalten",
        "button_keep_newest": "Neueste behalten",
        "button_keep_oldest": "Älteste behalten",
        "button_reset_group": "Gruppe zurücksetzen",
        "button_open_selected_folder": "Gewählten Ordner öffnen",
        "button_send_recycle": "Markierte Dateien in den Papierkorb senden",
        "mode_copy_short": "Kopieren",
        "mode_move_short": "Verschieben",
        "run_label": "Ausführen",
        "prerun_label": "Vorlauf",
        "summary_sources": "Quellen",
        "summary_target": "Ziel",
        "summary_mode": "Modus",
        "summary_run": "Ausführung",
        "summary_template": "Vorlage",
        "summary_module": "Modul",
        "summary_groups": "Exakte Gruppen",
        "summary_files_in_groups": "Dateien in Gruppen",
        "summary_marked_remove": "Zum Entfernen markiert",
        "summary_current_step": "Aktueller Schritt",
        "summary_next_action": "Nächste Aktion",
        "problem_full_cleanup_label": "Meine Ordner sind unordentlich und ich will das sauberste Gesamtergebnis",
        "problem_full_cleanup_desc": "Empfohlener Pfad: Duplikate → Sortieren → Umbenennen. Beste Wahl bei gemischten Quellen und unklarer Ordnerqualität.",
        "problem_ready_for_sorting_label": "Duplikate sind schon erledigt, jetzt will ich sauber sortieren",
        "problem_ready_for_sorting_desc": "Empfohlener Pfad: Sortieren → Umbenennen. Sinnvoll, wenn Duplikate schon außerhalb der App bereinigt wurden.",
        "problem_ready_for_rename_label": "Die Dateien liegen schon richtig, ich brauche nur bessere Namen",
        "problem_ready_for_rename_desc": "Empfohlener Pfad: nur Umbenennen. Das vorherige Ziel wird dabei als wahrscheinliche Quelle übernommen.",
        "problem_exact_duplicates_only_label": "Ich will gerade nur exakte Duplikate prüfen",
        "problem_exact_duplicates_only_desc": "Empfohlener Pfad: nur Duplikate. Exakt heißt 100 % byte-identisch, nicht nur optisch ähnlich.",
        "problem_select": "Wählen",
        "problem_selected": "Gewählt",
        "action_preview_copy": "Kopier-Vorschau",
        "action_preview_move": "Verschiebe-Vorschau",
        "action_copied": "Kopiert",
        "action_moved": "Verschoben",
        "action_preview_rename": "Umbenenn-Vorschau",
        "action_renamed": "Umbenannt",
        "action_unchanged": "Unverändert",
        "action_error": "Fehler",
        "decision_keep": "Behalten",
        "decision_remove": "Entfernen",
    },
}

PROBLEM_ORDER = ["full_cleanup", "ready_for_sorting", "ready_for_rename", "exact_duplicates_only"]
GROUPBOX_KEYS = {
    "Workflow setup": "group_workflow_setup",
    "Recommended path": "group_recommended_path",
    "Review and apply": "group_review_apply",
    "Source folders": "group_source_folders",
    "Target and options": "group_target_options",
    "Rename options": "group_rename_options",
    "Run": "group_run",
    "Results": "group_results",
    "Current situation": "group_current_situation",
    "Workflow-Einrichtung": "group_workflow_setup",
    "Empfohlener Ablauf": "group_recommended_path",
    "Prüfen und anwenden": "group_review_apply",
    "Quellordner": "group_source_folders",
    "Ziel und Optionen": "group_target_options",
    "Umbenennen-Optionen": "group_rename_options",
    "Ausführen": "group_run",
    "Ergebnisse": "group_results",
    "Aktuelle Situation": "group_current_situation",
}

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
        self.current_language = "en"
        self.home_wizard_dismissed = False
        self.home_wizard_step = 0
        self.home_selected_problem = "full_cleanup"
        self.duplicate_keep_strategy = "first"
        super().__init__()
        self._capture_page_header_labels()
        self._install_workflow_stepper()
        self._update_home_problem_cards()
        self._go_to_home_step(0)
        self._update_home_questionnaire_visibility()
        self._apply_language()
        self._refresh_workflow_stepper()

    def _t(self, key: str, **kwargs) -> str:
        text = STRINGS[self.current_language][key]
        return text.format(**kwargs) if kwargs else text
    def _problem_label(self, key: str) -> str:
        return self._t(f"problem_{key}_label")
    def _guided_problem_description(self, key: str) -> str:
        return self._t(f"problem_{key}_desc")
    def _localized_status(self, status: str) -> str:
        if status.startswith("Done"):
            return status.replace("Done", self._t("status_done"), 1)
        mapping = {"Pending": self._t("status_pending"), "Ready": self._t("status_ready"), "Skipped": self._t("status_skipped"), "Optional": self._t("status_optional"), "Not required": self._t("status_not_required")}
        return mapping.get(status, status)
    def _localized_step_name(self, step: str) -> str:
        mapping = {"Setup": self._t("step_setup"), "Duplicates": self._t("next_duplicates"), "Organize": self._t("next_organize"), "Rename": self._t("next_rename"), "Finished": self._t("step_finished")}
        return mapping.get(step, self._localized_status(step))
    def _duplicate_decision_label(self, is_keep: bool) -> str:
        return self._t("decision_keep") if is_keep else self._t("decision_remove")
    def _format_action(self, action: str) -> str:
        return self._t(f"action_{action.replace('-', '_')}")

    def _build_ui(self) -> None:
        container = QWidget(); root_layout = QHBoxLayout(container); root_layout.setContentsMargins(18,18,18,18); root_layout.setSpacing(16)
        nav = QFrame(); nav.setObjectName("Nav"); nav.setFixedWidth(230); nav_layout = QVBoxLayout(nav); nav_layout.setContentsMargins(18,18,18,18); nav_layout.setSpacing(10)
        self.nav_app_title_label = QLabel("Media Manager"); title_font = QFont(); title_font.setPointSize(18); title_font.setBold(True); self.nav_app_title_label.setFont(title_font)
        self.nav_app_subtitle_label = QLabel(); self.nav_app_subtitle_label.setStyleSheet("color: #93A8C6;")
        nav_layout.addWidget(self.nav_app_title_label); nav_layout.addWidget(self.nav_app_subtitle_label); nav_layout.addSpacing(12)
        nav_layout.addWidget(self.home_button); nav_layout.addWidget(self.workflow_button); nav_layout.addWidget(self.organize_button); nav_layout.addWidget(self.rename_button); nav_layout.addWidget(self.duplicates_button); nav_layout.addStretch(1)
        right_area = QWidget(); right_layout = QVBoxLayout(right_area); right_layout.setContentsMargins(0,0,0,0); right_layout.setSpacing(12)
        topbar = QFrame(); topbar.setObjectName("Card"); topbar_layout = QHBoxLayout(topbar); topbar_layout.setContentsMargins(14,12,14,12); topbar_layout.addStretch(1)
        self.language_toggle_button = QPushButton("🇺🇸"); self.language_toggle_button.setFixedWidth(58); self.language_toggle_button.setProperty("variant", "secondary"); self.language_toggle_button.clicked.connect(self._toggle_language); topbar_layout.addWidget(self.language_toggle_button)
        self.stack = QStackedWidget(); self.stack.addWidget(self._build_home_page()); self.stack.addWidget(self._build_workflow_page()); self.stack.addWidget(self._build_organize_page()); self.stack.addWidget(self._build_rename_page()); self.stack.addWidget(self._build_duplicates_page())
        right_layout.addWidget(topbar); right_layout.addWidget(self.stack, 1)
        root_layout.addWidget(nav); root_layout.addWidget(right_area, 1); self.setCentralWidget(container)

    def _build_home_page(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0,0,0,0); layout.setSpacing(16)
        self.home_questionnaire_card = QFrame(); self.home_questionnaire_card.setObjectName("HeroCard"); questionnaire_layout = QVBoxLayout(self.home_questionnaire_card); questionnaire_layout.setContentsMargins(28,28,28,28); questionnaire_layout.setSpacing(14)
        self.home_title_label = QLabel(); title_font = QFont(); title_font.setPointSize(24); title_font.setBold(True); self.home_title_label.setFont(title_font)
        self.home_subtitle_label = QLabel(); self.home_subtitle_label.setWordWrap(True); self.home_subtitle_label.setStyleSheet("color: #AFC1D9;")
        self.home_step_label = QLabel(); self.home_step_label.setStyleSheet("color: #93A8C6;")
        questionnaire_layout.addWidget(self.home_title_label); questionnaire_layout.addWidget(self.home_subtitle_label); questionnaire_layout.addWidget(self.home_step_label)
        self.home_questionnaire_stack = QStackedWidget(); self.home_questionnaire_stack.addWidget(self._build_wizard_problem_page()); self.home_questionnaire_stack.addWidget(self._build_wizard_mode_page()); self.home_questionnaire_stack.addWidget(self._build_wizard_duplicate_page()); self.home_questionnaire_stack.addWidget(self._build_wizard_summary_page()); questionnaire_layout.addWidget(self.home_questionnaire_stack, 1)
        footer_row = QHBoxLayout(); self.home_back_button = QPushButton(); self.home_back_button.setProperty("variant", "secondary"); self.home_back_button.clicked.connect(self._go_home_step_back); self.home_dismiss_button = QPushButton(); self.home_dismiss_button.setProperty("variant", "secondary"); self.home_dismiss_button.clicked.connect(self._dismiss_home_questionnaire); self.home_next_button = QPushButton(); self.home_next_button.clicked.connect(self._go_home_step_forward); footer_row.addWidget(self.home_back_button); footer_row.addWidget(self.home_dismiss_button); footer_row.addStretch(1); footer_row.addWidget(self.home_next_button); questionnaire_layout.addLayout(footer_row)
        self.home_info_card = QFrame(); self.home_info_card.setObjectName("Card"); info_layout = QVBoxLayout(self.home_info_card); info_layout.setContentsMargins(22,22,22,22); info_layout.setSpacing(10)
        self.home_info_title_label = QLabel(); info_title_font = QFont(); info_title_font.setPointSize(16); info_title_font.setBold(True); self.home_info_title_label.setFont(info_title_font)
        self.home_info_body_label = QLabel(); self.home_info_body_label.setWordWrap(True); self.home_info_body_label.setStyleSheet("color: #AFC1D9;")
        self.home_restart_questionnaire_button = QPushButton(); self.home_restart_questionnaire_button.clicked.connect(self._restart_home_questionnaire)
        info_layout.addWidget(self.home_info_title_label); info_layout.addWidget(self.home_info_body_label); info_layout.addWidget(self.home_restart_questionnaire_button); info_layout.addStretch(1)
        layout.addWidget(self.home_questionnaire_card, 8); layout.addWidget(self.home_info_card, 2); return page

    def _build_wizard_problem_page(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0,0,0,0); layout.setSpacing(12)
        self.wizard_problem_title_label = QLabel(); font = QFont(); font.setPointSize(19); font.setBold(True); self.wizard_problem_title_label.setFont(font)
        self.wizard_problem_subtitle_label = QLabel(); self.wizard_problem_subtitle_label.setWordWrap(True); self.wizard_problem_subtitle_label.setStyleSheet("color: #AFC1D9;")
        layout.addWidget(self.wizard_problem_title_label); layout.addWidget(self.wizard_problem_subtitle_label)
        grid = QGridLayout(); grid.setHorizontalSpacing(14); grid.setVerticalSpacing(14); self.home_problem_cards = {}
        for index, key in enumerate(PROBLEM_ORDER):
            card = ProblemCard("", "", "")
            card.button.clicked.connect(lambda _checked=False, selected_key=key: self._select_home_problem(selected_key))
            self.home_problem_cards[key] = card; grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid); layout.addStretch(1); return page

    def _build_wizard_mode_page(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0,0,0,0); layout.setSpacing(12)
        self.wizard_mode_title_label = QLabel(); font = QFont(); font.setPointSize(19); font.setBold(True); self.wizard_mode_title_label.setFont(font)
        self.wizard_mode_subtitle_label = QLabel(); self.wizard_mode_subtitle_label.setWordWrap(True); self.wizard_mode_subtitle_label.setStyleSheet("color: #AFC1D9;")
        self.home_mode_copy_radio = QRadioButton(); self.home_mode_move_radio = QRadioButton(); self.home_mode_copy_radio.setChecked(True)
        layout.addWidget(self.wizard_mode_title_label); layout.addWidget(self.wizard_mode_subtitle_label); layout.addWidget(self.home_mode_copy_radio); layout.addWidget(self.home_mode_move_radio); layout.addStretch(1); return page

    def _build_wizard_duplicate_page(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0,0,0,0); layout.setSpacing(12)
        self.wizard_duplicate_title_label = QLabel(); font = QFont(); font.setPointSize(19); font.setBold(True); self.wizard_duplicate_title_label.setFont(font)
        self.wizard_duplicate_subtitle_label = QLabel(); self.wizard_duplicate_subtitle_label.setWordWrap(True); self.wizard_duplicate_subtitle_label.setStyleSheet("color: #AFC1D9;")
        self.home_duplicate_rule_combo = QComboBox(); self.home_duplicate_rule_combo.setMinimumWidth(420)
        layout.addWidget(self.wizard_duplicate_title_label); layout.addWidget(self.wizard_duplicate_subtitle_label); layout.addWidget(self.home_duplicate_rule_combo); layout.addStretch(1); return page

    def _build_wizard_summary_page(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0,0,0,0); layout.setSpacing(12)
        self.wizard_summary_title_label = QLabel(); font = QFont(); font.setPointSize(19); font.setBold(True); self.wizard_summary_title_label.setFont(font)
        self.wizard_summary_subtitle_label = QLabel(); self.wizard_summary_subtitle_label.setWordWrap(True); self.wizard_summary_subtitle_label.setStyleSheet("color: #AFC1D9;")
        self.wizard_summary_text_label = QLabel(); self.wizard_summary_text_label.setWordWrap(True); self.wizard_summary_text_label.setStyleSheet("font-size: 14px; color: #E6EEF8;")
        layout.addWidget(self.wizard_summary_title_label); layout.addWidget(self.wizard_summary_subtitle_label); layout.addWidget(self.wizard_summary_text_label); layout.addStretch(1); return page

    def _populate_guided_problem_combo(self) -> None:
        current_key = getattr(self, "workflow_selected_problem", "full_cleanup")
        self.guided_problem_combo.blockSignals(True); self.guided_problem_combo.clear()
        for key in PROBLEM_ORDER: self.guided_problem_combo.addItem(self._problem_label(key), key)
        index = self.guided_problem_combo.findData(current_key); self.guided_problem_combo.setCurrentIndex(index if index >= 0 else 0); self.guided_problem_combo.blockSignals(False)

    def _capture_page_header_labels(self) -> None:
        self.workflow_page_title_label, self.workflow_page_subtitle_label = self._page_header_labels(1)
        self.organize_page_title_label, self.organize_page_subtitle_label = self._page_header_labels(2)
        self.rename_page_title_label, self.rename_page_subtitle_label = self._page_header_labels(3)
        self.duplicates_page_title_label, self.duplicates_page_subtitle_label = self._page_header_labels(4)

    def _page_header_labels(self, page_index: int) -> tuple[QLabel, QLabel]:
        page = self.stack.widget(page_index); header_frame = page.layout().itemAt(0).widget(); header_layout = header_frame.layout(); return header_layout.itemAt(0).widget(), header_layout.itemAt(1).widget()

    def _install_workflow_stepper(self) -> None:
        workflow_page = self.stack.widget(1); outer_layout = workflow_page.layout(); self.workflow_progress_card = QFrame(); self.workflow_progress_card.setObjectName("Card")
        progress_layout = QVBoxLayout(self.workflow_progress_card); progress_layout.setContentsMargins(20,18,20,18); progress_layout.setSpacing(10)
        self.workflow_progress_title_label = QLabel(); font = QFont(); font.setPointSize(16); font.setBold(True); self.workflow_progress_title_label.setFont(font)
        self.workflow_progress_summary_label = QLabel(); self.workflow_progress_summary_label.setStyleSheet("color: #AFC1D9;"); self.workflow_progress_summary_label.setWordWrap(True)
        self.workflow_progress_bar = QProgressBar(); self.workflow_progress_bar.setRange(0,100); self.workflow_progress_bar.setTextVisible(False); self.workflow_progress_bar.setFixedHeight(12); self.workflow_progress_bar.setStyleSheet("QProgressBar { background: #091321; border: 1px solid #31455F; border-radius: 6px; }QProgressBar::chunk { background: #2F6FED; border-radius: 6px; }")
        badges_row = QHBoxLayout(); badges_row.setSpacing(12); self.workflow_step_badges = {"duplicates": WorkflowStepBadge(""), "organize": WorkflowStepBadge(""), "rename": WorkflowStepBadge("")}
        for badge in self.workflow_step_badges.values(): badges_row.addWidget(badge)
        progress_layout.addWidget(self.workflow_progress_title_label); progress_layout.addWidget(self.workflow_progress_summary_label); progress_layout.addWidget(self.workflow_progress_bar); progress_layout.addLayout(badges_row); outer_layout.insertWidget(2, self.workflow_progress_card)

    def _load_settings(self) -> None:
        super()._load_settings(); self.current_language = str(self.app_settings.get("ui_language", "en")); self.current_language = self.current_language if self.current_language in STRINGS else "en"; self.home_wizard_dismissed = bool(self.app_settings.get("home_wizard_dismissed", False)); self.duplicate_keep_strategy = str(self.app_settings.get("duplicate_keep_strategy", "first")); self.duplicate_keep_strategy = self.duplicate_keep_strategy if self.duplicate_keep_strategy in {"first","newest","oldest"} else "first"; self.home_selected_problem = self.workflow_selected_problem; self.home_mode_move_radio.setChecked(self.move_radio.isChecked()); self.home_mode_copy_radio.setChecked(not self.move_radio.isChecked())

    def _save_settings(self) -> None:
        super()._save_settings(); updated = dict(self.app_settings); updated["ui_language"] = self.current_language; updated["home_wizard_dismissed"] = self.home_wizard_dismissed; updated["duplicate_keep_strategy"] = self.duplicate_keep_strategy; from .settings import save_app_settings; save_app_settings(updated); self.app_settings = updated

    def _toggle_language(self) -> None:
        self.current_language = "de" if self.current_language == "en" else "en"; self._apply_language(); self._save_settings()

    def _translate_group_boxes(self) -> None:
        for box in self.findChildren(QGroupBox):
            key = GROUPBOX_KEYS.get(box.title())
            if key: box.setTitle(self._t(key))

    def _translate_table_headers(self) -> None:
        self.results_table.setHorizontalHeaderLabels(["Status","File","Source","Target","Details"] if self.current_language == "en" else ["Status","Datei","Quelle","Ziel","Details"])
        self.rename_results_table.setHorizontalHeaderLabels(["Status","Current","New","Folder","Details"] if self.current_language == "en" else ["Status","Aktuell","Neu","Ordner","Details"])
        self.duplicates_results_table.setHorizontalHeaderLabels(["Group","Decision","File","Folder","Size","Notes"] if self.current_language == "en" else ["Gruppe","Entscheidung","Datei","Ordner","Größe","Hinweise"])

    def _populate_duplicate_rule_combo(self) -> None:
        current = self.duplicate_keep_strategy; self.home_duplicate_rule_combo.blockSignals(True); self.home_duplicate_rule_combo.clear(); self.home_duplicate_rule_combo.addItem(self._t("wizard_keep_first"), "first"); self.home_duplicate_rule_combo.addItem(self._t("wizard_keep_newest"), "newest"); self.home_duplicate_rule_combo.addItem(self._t("wizard_keep_oldest"), "oldest"); index = self.home_duplicate_rule_combo.findData(current); self.home_duplicate_rule_combo.setCurrentIndex(index if index >= 0 else 0); self.home_duplicate_rule_combo.blockSignals(False)

    def _update_home_problem_cards(self) -> None:
        for key, card in self.home_problem_cards.items():
            card.layout().itemAt(0).widget().setText(self._problem_label(key)); card.layout().itemAt(1).widget().setText(self._guided_problem_description(key)); selected = key == self.home_selected_problem; card.button.setText(self._t("problem_selected") if selected else self._t("problem_select")); card.button.setProperty("variant", None if selected else "secondary"); card.button.style().unpolish(card.button); card.button.style().polish(card.button)

    def _select_home_problem(self, key: str) -> None:
        self.home_selected_problem = key; self._update_home_problem_cards(); self.status_bar.showMessage(self._problem_label(key))

    def _go_to_home_step(self, step: int) -> None:
        self.home_wizard_step = max(0, min(step, self.home_questionnaire_stack.count() - 1)); self.home_questionnaire_stack.setCurrentIndex(self.home_wizard_step); self.home_step_label.setText(self._t("home_step", current=self.home_wizard_step + 1, total=self.home_questionnaire_stack.count())); self.home_back_button.setText(self._t("home_back")); self.home_dismiss_button.setText(self._t("home_dismiss")); self.home_back_button.setVisible(self.home_wizard_step > 0); self.home_next_button.setText(self._t("home_start") if self.home_wizard_step == self.home_questionnaire_stack.count() - 1 else self._t("home_next"));
        if self.home_wizard_step == self.home_questionnaire_stack.count() - 1: self._update_home_summary_text()

    def _go_home_step_back(self) -> None:
        self._go_to_home_step(self.home_wizard_step - 1)
    def _go_home_step_forward(self) -> None:
        self._go_to_home_step(self.home_wizard_step + 1) if self.home_wizard_step < self.home_questionnaire_stack.count() - 1 else self._start_from_home_questionnaire()
    def _update_home_summary_text(self) -> None:
        mode_key = "mode_move_short" if self.home_mode_move_radio.isChecked() else "mode_copy_short"; keep_rule_key = {"first": "wizard_keep_first", "newest": "wizard_keep_newest", "oldest": "wizard_keep_oldest"}[self.home_duplicate_rule_combo.currentData()]; self.wizard_summary_text_label.setText(self._t("wizard_summary_text", problem=self._problem_label(self.home_selected_problem), mode=self._t(mode_key), keep_rule=self._t(keep_rule_key)))
    def _dismiss_home_questionnaire(self) -> None:
        self.home_wizard_dismissed = True; self._update_home_questionnaire_visibility(); self._save_settings()
    def _restart_home_questionnaire(self) -> None:
        self.home_wizard_dismissed = False; self._update_home_questionnaire_visibility(); self._go_to_home_step(0); self._save_settings()
    def _update_home_questionnaire_visibility(self) -> None:
        self.home_questionnaire_card.setVisible(not self.home_wizard_dismissed); self.home_restart_questionnaire_button.setVisible(self.home_wizard_dismissed)
    def _start_from_home_questionnaire(self) -> None:
        self._set_guided_problem(self.home_selected_problem); self._prepare_guided_problem(self.home_selected_problem); self.duplicate_keep_strategy = str(self.home_duplicate_rule_combo.currentData()); self.move_radio.setChecked(self.home_mode_move_radio.isChecked()); self.copy_radio.setChecked(self.home_mode_copy_radio.isChecked()); self.home_wizard_dismissed = False; self._update_home_questionnaire_visibility(); self._save_settings(); self._set_current_page(1); self.status_bar.showMessage("Guided setup prepared. Add sources and a target to continue." if self.current_language == "en" else "Geführte Einrichtung vorbereitet. Wähle jetzt Quellen und Ziel aus.")

    def _workflow_next_action_label(self) -> str:
        if not self._workflow_source_dirs() or not self._workflow_target_text(): return "Complete setup" if self.current_language == "en" else "Einrichtung abschließen"
        if self.workflow_step_statuses["duplicates"] == "Pending": return self._t("next_duplicates")
        if self.workflow_step_statuses["organize"] == "Pending": return self._t("next_organize")
        if self.workflow_step_statuses["rename"] == "Pending": return self._t("next_rename")
        return "Review final result" if self.current_language == "en" else "Endergebnis prüfen"

    def _refresh_summary_cards(self) -> None:
        super()._refresh_summary_cards(); self._set_card_title(self.sources_card, self._t("summary_sources")); self._set_card_title(self.target_card, self._t("summary_target")); self._set_card_title(self.mode_card, self._t("summary_mode")); self._set_card_title(self.run_mode_card, self._t("summary_run")); count = self.source_list.count(); self.sources_card.set_value(f"{count} folders" if self.current_language == "en" else f"{count} Ordner"); self.mode_card.set_value(self._t("mode_move_short") if self.move_radio.isChecked() else self._t("mode_copy_short")); run_label = self._t("run_label") if self.apply_checkbox.isChecked() else self._t("prerun_label"); self.run_mode_card.set_value(run_label); self.run_button.setText(run_label)
    def _refresh_rename_summary_cards(self) -> None:
        super()._refresh_rename_summary_cards(); self._set_card_title(self.rename_sources_card, self._t("summary_sources")); self._set_card_title(self.rename_template_card, self._t("summary_template")); self._set_card_title(self.rename_run_mode_card, self._t("summary_run")); self._set_card_title(self.rename_status_card, self._t("summary_module")); count = self.rename_source_list.count(); self.rename_sources_card.set_value(f"{count} folders" if self.current_language == "en" else f"{count} Ordner"); run_label = self._t("run_label") if self.rename_apply_checkbox.isChecked() else self._t("prerun_label"); self.rename_run_mode_card.set_value(run_label); self.rename_run_button.setText(run_label); self.rename_status_card.set_value(self._t("nav_rename"))
    def _refresh_duplicates_summary_cards(self, groups: int | None = None, duplicate_files: int | None = None, extra_duplicates: int | None = None) -> None:
        super()._refresh_duplicates_summary_cards(groups, duplicate_files, extra_duplicates); self._set_card_title(self.duplicates_sources_card, self._t("summary_sources")); self._set_card_title(self.duplicates_groups_card, self._t("summary_groups")); self._set_card_title(self.duplicates_files_card, self._t("summary_files_in_groups")); self._set_card_title(self.duplicates_extra_card, self._t("summary_marked_remove")); count = self.duplicates_source_list.count(); self.duplicates_sources_card.set_value(f"{count} folders" if self.current_language == "en" else f"{count} Ordner")
    def _refresh_workflow_summary_cards(self) -> None:
        super()._refresh_workflow_summary_cards(); self._set_card_title(self.workflow_sources_card, self._t("summary_sources")); self._set_card_title(self.workflow_target_card, self._t("summary_target")); self._set_card_title(self.workflow_status_card, self._t("summary_current_step")); self._set_card_title(self.workflow_next_card, self._t("summary_next_action")); count = self.workflow_source_list.count(); self.workflow_sources_card.set_value(f"{count} folders" if self.current_language == "en" else f"{count} Ordner"); self.workflow_status_card.set_value(self._localized_step_name(self.workflow_current_step)); self.workflow_next_card.set_value(self._workflow_next_action_label()); self.workflow_duplicates_step_card.set_status(self._localized_status(self.workflow_step_statuses["duplicates"])); self.workflow_organize_step_card.set_status(self._localized_status(self.workflow_step_statuses["organize"])); self.workflow_rename_step_card.set_status(self._localized_status(self.workflow_step_statuses["rename"]));
        if hasattr(self, "workflow_progress_bar"): self._refresh_workflow_stepper()

    def _refresh_workflow_stepper(self) -> None:
        required_steps = workflow_required_steps(self.workflow_selected_problem); done = workflow_completed_steps(self.workflow_selected_problem, self.workflow_step_statuses); next_step = workflow_next_required_step(self.workflow_selected_problem, self.workflow_step_statuses); percent = workflow_progress_percent(self.workflow_selected_problem, self.workflow_step_statuses); self.workflow_progress_title_label.setText(self._t("workflow_progress_title")); self.workflow_step_badges["duplicates"].title_label.setText(self._t("step_duplicates")); self.workflow_step_badges["organize"].title_label.setText(self._t("step_organize")); self.workflow_step_badges["rename"].title_label.setText(self._t("step_rename")); self.workflow_progress_bar.setValue(percent)
        if next_step == "finished": self.workflow_progress_summary_label.setText(self._t("workflow_progress_done", done=done, total=len(required_steps)))
        else: self.workflow_progress_summary_label.setText(self._t("workflow_progress_next", done=done, total=len(required_steps), next_step=self._t({"duplicates": "next_duplicates", "organize": "next_organize", "rename": "next_rename"}[next_step])))
        current_key = self.workflow_current_step.strip().lower(); required_set = set(required_steps)
        for key, badge in self.workflow_step_badges.items():
            if key not in required_set: badge.set_status(self._t("status_not_required")); continue
            status = self.workflow_step_statuses.get(key, "Pending"); is_active = current_key.startswith(key) or (current_key == "setup" and next_step == key)
            if status.startswith("Done"): badge.set_status(self._localized_status(status), highlight=False)
            elif status == "Ready": badge.set_status(self._localized_status(status), highlight=True)
            else: badge.set_status(self._localized_status(status), highlight=is_active)

    def _apply_language(self) -> None:
        self.language_toggle_button.setText("🇺🇸" if self.current_language == "en" else "🇩🇪"); self.language_toggle_button.setToolTip(self._t("language_tooltip")); self.nav_app_subtitle_label.setText(self._t("nav_subtitle")); self.home_button.setText(self._t("nav_home")); self.workflow_button.setText(self._t("nav_workflow")); self.organize_button.setText(self._t("nav_organize")); self.rename_button.setText(self._t("nav_rename")); self.duplicates_button.setText(self._t("nav_duplicates"))
        self.home_title_label.setText(self._t("home_title")); self.home_subtitle_label.setText(self._t("home_subtitle")); self.home_info_title_label.setText(self._t("home_info_title")); self.home_info_body_label.setText(self._t("home_info_body")); self.home_restart_questionnaire_button.setText(self._t("home_restart")); self.wizard_problem_title_label.setText(self._t("wizard_problem_title")); self.wizard_problem_subtitle_label.setText(self._t("wizard_problem_subtitle")); self.wizard_mode_title_label.setText(self._t("wizard_mode_title")); self.wizard_mode_subtitle_label.setText(self._t("wizard_mode_subtitle")); self.home_mode_copy_radio.setText(self._t("wizard_mode_copy")); self.home_mode_move_radio.setText(self._t("wizard_mode_move")); self.wizard_duplicate_title_label.setText(self._t("wizard_duplicates_title")); self.wizard_duplicate_subtitle_label.setText(self._t("wizard_duplicates_subtitle")); self.wizard_summary_title_label.setText(self._t("wizard_summary_title")); self.wizard_summary_subtitle_label.setText(self._t("wizard_summary_subtitle"))
        self._populate_duplicate_rule_combo(); self._update_home_problem_cards(); self._go_to_home_step(self.home_wizard_step); self._update_home_summary_text(); self._populate_guided_problem_combo(); index = self.guided_problem_combo.findData(self.workflow_selected_problem); self.guided_problem_combo.setCurrentIndex(index if index >= 0 else 0); self.guided_problem_hint_label.setText(self._guided_problem_description(self._current_guided_problem_key())); self.workflow_mode_hint_label.setText(self._guided_problem_description(self.workflow_selected_problem)); self.workflow_hint_label.setText(self._t("workflow_hint")); self.workflow_page_title_label.setText(self._t("workflow_board_title")); self.workflow_page_subtitle_label.setText(self._t("workflow_board_subtitle")); self.organize_page_title_label.setText(self._t("nav_organize")); self.organize_page_subtitle_label.setText("Multiple sources. One target. Preview first." if self.current_language == "en" else "Mehrere Quellen. Ein Ziel. Erst Vorschau, dann ausführen."); self.rename_page_title_label.setText(self._t("nav_rename")); self.rename_page_subtitle_label.setText("Rename media in place. Preview first." if self.current_language == "en" else "Dateien direkt im Ordner umbenennen. Erst Vorschau."); self.duplicates_page_title_label.setText(self._t("nav_duplicates")); self.duplicates_page_subtitle_label.setText("Exact duplicate scan across multiple sources. 100% means byte-identical only." if self.current_language == "en" else "Exakte Duplikat-Prüfung über mehrere Quellen. 100 % heißt nur byte-identisch.")
        self.workflow_add_source_button.setText(self._t("button_add")); self.workflow_remove_source_button.setText(self._t("button_remove")); self.workflow_clear_sources_button.setText(self._t("button_clear")); self.workflow_target_browse_button.setText(self._t("workflow_browse_target")); self.workflow_apply_button.setText(self._t("workflow_apply_modules")); self.workflow_start_button.setText(self._t("workflow_start_guided"))
        for button in [self.add_source_button, self.rename_add_source_button, self.duplicates_add_source_button]: button.setText(self._t("button_add"))
        for button in [self.remove_source_button, self.rename_remove_source_button, self.duplicates_remove_source_button]: button.setText(self._t("button_remove"))
        for button in [self.clear_sources_button, self.rename_clear_sources_button, self.duplicates_clear_sources_button]: button.setText(self._t("button_clear"))
        self.save_import_set_button.setText(self._t("button_save_set")); self.load_import_set_button.setText(self._t("button_load")); self.delete_import_set_button.setText(self._t("button_delete")); self.organize_use_workflow_button.setText(self._t("button_use_workflow")); self.rename_use_target_button.setText(self._t("button_use_previous_target")); self.duplicates_use_workflow_button.setText(self._t("button_use_workflow")); self.target_browse_button.setText(self._t("button_browse")); self.exiftool_browse_button.setText(self._t("button_browse")); self.open_target_button.setText(self._t("button_open_target")); self.clear_results_button.setText(self._t("button_clear_results")); self.rename_clear_results_button.setText(self._t("button_clear_results")); self.duplicates_clear_results_button.setText(self._t("button_clear_results")); self.duplicates_run_button.setText(self._t("button_scan"))
        if hasattr(self, "duplicates_keep_selected_button"):
            self.duplicates_keep_selected_button.setText(self._t("button_keep_selected")); self.duplicates_keep_newest_button.setText(self._t("button_keep_newest")); self.duplicates_keep_oldest_button.setText(self._t("button_keep_oldest")); self.duplicates_reset_group_button.setText(self._t("button_reset_group")); self.duplicates_open_folder_button.setText(self._t("button_open_selected_folder")); self.duplicates_apply_review_button.setText(self._t("button_send_recycle"))
        self.target_input.setPlaceholderText("Target folder" if self.current_language == "en" else "Zielordner"); self.exiftool_input.setPlaceholderText("Auto-detect when empty" if self.current_language == "en" else "Automatisch finden, wenn leer"); self.workflow_target_input.setPlaceholderText("Final target folder" if self.current_language == "en" else "Endgültiger Zielordner"); self.organize_template_label.setText("Template" if self.current_language == "en" else "Vorlage"); self.rename_template_label.setText("Template" if self.current_language == "en" else "Vorlage"); self.rename_template_hint.setText("Template fields: {year} {month} {day} {hour} {minute} {second} {stem} {suffix} {index}" if self.current_language == "en" else "Vorlagenfelder: {year} {month} {day} {hour} {minute} {second} {stem} {suffix} {index}")
        self._translate_group_boxes(); self._translate_table_headers(); self._refresh_summary_cards(); self._refresh_rename_summary_cards(); self._refresh_duplicates_summary_cards(); self._refresh_workflow_summary_cards(); self._refresh_workflow_stepper()

def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = MediaManagerWindow()
    window.show()
    return app.exec()
