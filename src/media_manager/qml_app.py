
from __future__ import annotations

import os
import sys
import threading
from datetime import datetime
from importlib import resources
from pathlib import Path

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
os.environ.setdefault("QT_QUICK_CONTROLS_FALLBACK_STYLE", "Basic")

from PySide6.QtCore import Property, QObject, QSettings, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .cleanup_plan import build_exact_cleanup_plan
from .duplicates import DuplicateScanConfig, scan_exact_duplicates
from .rename_plan import (
    RenameBlock,
    build_filename_preview,
    build_rename_preview,
    blocks_for_template,
    template_names,
)
from .sorter import iter_media_files
from .sorting_plan import DEFAULT_SORT_LEVELS, SortLevel, build_sort_preview

TRANSLATIONS = {
    "en": {
        "app_title": "Media Manager",
        "nav_subtitle": "Guided first. Manual when needed.",
        "nav_home": "Home",
        "nav_workflow": "Workflow",
        "nav_duplicates": "Duplicates",
        "nav_organize": "Organize",
        "nav_rename": "Rename",
        "home_title": "Media Manager",
        "home_subtitle": "Choose your problem to start a guided workflow.",
        "home_dismiss": "Dismiss",
        "home_restart": "Start guided questionnaire",
        "home_info_title": "How it works",
        "home_info_body": "Clean duplicates first, then organize, then rename. The guided path stays the recommended path.",
        "problem_full_cleanup_label": "My folders are messy and I want a full cleanup",
        "problem_full_cleanup_desc": "Duplicates, organize, and rename in one guided run.",
        "problem_ready_for_sorting_label": "Duplicates are already handled, now I need sorting",
        "problem_ready_for_sorting_desc": "Go directly toward folder structure and cleanup flow.",
        "problem_ready_for_rename_label": "The structure is fine, I mostly need better names",
        "problem_ready_for_rename_desc": "Start from a lighter workflow with naming as the main goal.",
        "problem_exact_duplicates_only_label": "I only want to inspect exact duplicates right now",
        "problem_exact_duplicates_only_desc": "Review only guaranteed byte-identical duplicates.",
        "workflow_title": "Guided workflow",
        "workflow_subtitle": "Everything important now happens here, step by step.",
        "stage_sources_title": "Select your source folders",
        "stage_sources_subtitle": "Start with the folders you want to clean.",
        "stage_sources_action": "Add source folder",
        "stage_sources_list_title": "Selected source folders",
        "stage_sources_empty": "No source folders selected yet.",
        "stage_target_title": "Select your target folder",
        "stage_target_subtitle": "Choose where the cleaned library should live.",
        "stage_target_action": "Select target folder",
        "stage_target_empty": "No target folder selected yet.",
        "stage_mode_title": "What should happen to the files?",
        "stage_mode_subtitle": "You can still change this later before real execution.",
        "mode_copy": "Copy",
        "mode_move": "Move",
        "mode_delete": "Delete",
        "stage_duplicates_title": "Duplicate review preview",
        "stage_duplicates_subtitle": "Start the visible review phase for exact duplicates.",
        "stage_duplicates_action": "Start duplicate review",
        "stage_duplicates_hint": "This is still a review popup, not the final comparison tool.",
        "stage_summary_title": "Cleanup summary",
        "stage_summary_subtitle": "Review what the workflow currently knows before later execution and sorting stages.",
        "stage_summary_action": "Continue to sorting",
        "summary_totals_title": "Current cleanup totals",
        "summary_resolved_title": "Decision progress",
        "summary_dry_run_title": "Dry-run foundation",
        "summary_dry_run_body": "This stage does not execute anything yet. It shows what the workflow currently plans based on exact duplicate review decisions.",
        "summary_groups": "Exact groups",
        "summary_duplicate_files": "Duplicate files",
        "summary_extra_duplicates": "Extra duplicates",
        "summary_resolved_groups": "Resolved groups",
        "summary_unresolved_groups": "Unresolved groups",
        "summary_mode": "Current mode",
        "summary_ready_body": "All exact duplicate groups currently have a keep decision. A later dry run can turn these decisions into a full cleanup preview.",
        "summary_unresolved_body": "Some exact duplicate groups still have no keep decision. Review them before trusting a later dry run.",
        "summary_decision_status": "{resolved} resolved / {unresolved} unresolved",
        "summary_plan_intro": "Planned interpretation so far",
        "summary_plan_line_1": "Resolved groups keep one selected survivor and mark the remaining exact matches as removable candidates.",
        "summary_plan_line_2": "Unresolved groups stay blocked from trustworthy dry-run planning until a keep candidate is chosen.",
        "summary_plan_line_3": "Later workflow stages will extend this into copy / move / delete previews and storage impact estimates.",
        "summary_planned_removals_title": "Planned remove candidates",
        "summary_planned_removals_empty": "No removable exact-match candidates are planned yet.",
        "summary_unresolved_list_title": "Open exact groups",
        "summary_unresolved_empty": "No open exact groups remain.",
        "summary_keep_survivor_label": "Keep",
        "summary_remove_candidate_label": "Remove",
        "summary_candidates_label": "Candidates",
        "summary_estimated_reclaimable_label": "Estimated reclaimable",
        "table_name": "Name",
        "table_size": "Size",
        "table_date": "Date",
        "table_matches": "Matches",
        "table_score": "Score",
        "table_action": "Action",
        "table_show": "Show",
        "stage_sorting_title": "Sorting builder",
        "stage_sorting_subtitle": "Choose how the cleaned library should be structured before the rename stage.",
        "stage_sorting_action": "Continue to rename",
        "sorting_config_title": "Sorting configuration",
        "sorting_config_body": "Set the folder structure for year, month, and day. This preview currently uses source file timestamps.",
        "sorting_level_year": "Year",
        "sorting_level_month": "Month",
        "sorting_level_day": "Day",
        "sorting_style_year_yyyy": "4-digit year",
        "sorting_style_year_yy": "2-digit year",
        "sorting_style_month_mm": "Month number",
        "sorting_style_month_name": "Month name",
        "sorting_style_month_yyyy-mm": "Year-Month",
        "sorting_style_day_dd": "Day number",
        "sorting_style_day_yyyy-mm-dd": "Full date",
        "sorting_cycle_action": "Change style",
        "sorting_reset_action": "Reset defaults",
        "sorting_preview_title": "Preview target structure",
        "sorting_preview_body": "A few real source files are mapped to their future relative target folders.",
        "sorting_preview_source": "Source",
        "sorting_preview_date": "Date",
        "sorting_preview_target": "Target folder",
        "sorting_preview_empty": "Add source folders with media files to see a sorting preview.",
        "sorting_template_title": "Live structure template",
        "sorting_template_body": "This updates immediately and shows how the folder structure will look later.",
        "sorting_template_live_source": "Template based on the first detected source file date.",
        "sorting_template_sample_source": "Template based on a sample date until real source dates are available.",
        "sorting_preview_count": "{count} preview item(s)",
        "stage_rename_title": "Rename setup preview",
        "stage_rename_subtitle": "Rename configuration comes after sorting.",
        "stage_rename_action": "Continue to summary",
        "rename_config_title": "Rename builder",
        "rename_config_body": "Start with two core blocks and add more when needed. Templates are only presets now. The real rename preview is always built from the active block list.",
        "rename_blocks_body": "Each block stands for one filename part. Click a block to change it. Add optional blocks only when they improve the result.",
        "rename_add_block_action": "Add block",
        "rename_remove_block_action": "Remove",
        "rename_block_press_to_change": "Press to change",
        "rename_block_optional": "Optional block",
        "rename_block_primary": "Core block",
        "rename_template_title": "Live filename template",
        "rename_template_selector": "Template",
        "rename_template_reset_action": "Reset template",
        "rename_template_live_source": "Preview based on the first detected source file.",
        "rename_template_sample_source": "Preview based on a sample filename until real source files are available.",
        "rename_preview_count": "{count} preview item(s)",
        "rename_blocks_title": "Active blocks",
        "rename_preview_title": "Rename preview",
        "rename_preview_body": "Real source files are mapped to their proposed names.",
        "rename_preview_empty": "Add source folders with media files to see rename previews.",
        "rename_template_custom": "Custom blocks",
        "rename_template_readable_datetime_original": "Readable date + time + original name",
        "rename_template_year_month_day_time_original": "Year + month + day + time + original name",
        "rename_template_date_original": "ISO date + original name",
        "rename_block_original_stem": "Original name",
        "rename_block_year": "Year",
        "rename_block_month_name": "Month name",
        "rename_block_day": "Day",
        "rename_block_date_iso": "ISO date",
        "rename_block_date_readable": "Readable date",
        "rename_block_time_hhmmss": "Time",
        "stage_done_title": "Congratulations",
        "stage_done_subtitle": "This is the preview shell for the future guided product.",
        "stage_done_action": "Finish preview",
        "button_back": "Back",
        "button_next": "Next",
        "button_home": "Back to home",
        "button_clear": "Clear",
        "button_remove": "Remove",
        "bottom_sources": "Sources",
        "bottom_target": "Target",
        "bottom_mode": "Mode",
        "bottom_step": "Step",
        "bottom_files": "Files found",
        "tip_1": "RAW files usually preserve much more editing latitude than JPEG exports.",
        "tip_2": "Exact duplicates are the safest cleanup target because the file content is byte-identical.",
        "tip_3": "Good folder structure saves more time later than aggressive early renaming.",
        "tip_4": "A consistent backup matters more than a perfect first cleanup pass.",
        "tip_5": "Blue hour usually gives softer contrast than harsh midday light.",
        "tip_6": "Long focal lengths amplify camera shake more than wide angles.",
        "tip_7": "Video and photo sidecar files often belong together and should not be split carelessly.",
        "tip_8": "A trustworthy dry run is more valuable than rushing into deletion.",
        "manual_placeholder_title": "Manual tool page preview",
        "manual_placeholder_body": "This page will later reuse the same workflow logic.",
        "manual_hint": "Use the guided workflow unless you know exactly what you want.",
        "language_tooltip": "Switch language",
        "status_sources_updated": "Source folders updated",
        "status_target_updated": "Target folder selected",
        "status_duplicates_preparing": "Preparing exact duplicate scan ...",
        "status_duplicates_stage_1": "Grouping media by file size ...",
        "status_duplicates_stage_2": "Comparing sample fingerprints ...",
        "status_duplicates_stage_3": "Computing full hashes ...",
        "status_duplicates_stage_4": "Confirming byte-identical groups ...",
        "status_duplicates_finished": "Exact groups: {groups} | duplicate files: {files} | extra duplicates: {extra} | errors: {errors}",
        "status_duplicates_none": "No exact duplicates found. Errors: {errors}",
        "status_duplicate_selection_saved": "Keep candidate set to {name}",
        "duplicate_detail_hint": "Quick review popup, not the final compare tool.",
        "duplicate_detail_selected": "Selected keep candidate",
        "duplicate_detail_keep_selected": "Keep selected",
        "duplicate_detail_keep_newest": "Keep newest",
        "duplicate_detail_keep_oldest": "Keep oldest",
        "duplicate_detail_close": "Close",
        "duplicate_detail_path": "Path",
        "duplicate_detail_summary": "{files} file(s) | {size} | exact match",
    },
    "de": {
        "app_title": "Media Manager",
        "nav_subtitle": "Zuerst geführt. Manuell nur wenn nötig.",
        "nav_home": "Start",
        "nav_workflow": "Workflow",
        "nav_duplicates": "Duplikate",
        "nav_organize": "Sortieren",
        "nav_rename": "Umbenennen",
        "home_title": "Media Manager",
        "home_subtitle": "Wähle dein Problem aus, um einen geführten Workflow zu starten.",
        "home_dismiss": "Ausblenden",
        "home_restart": "Geführte Umfrage starten",
        "home_info_title": "How it works",
        "home_info_body": "Erst Duplikate, dann sortieren, dann umbenennen. Der geführte Pfad bleibt der empfohlene Weg.",
        "problem_full_cleanup_label": "Meine Ordner sind unordentlich und ich will eine komplette Bereinigung",
        "problem_full_cleanup_desc": "Duplikate, Sortieren und Umbenennen in einem geführten Durchlauf.",
        "problem_ready_for_sorting_label": "Duplikate sind schon erledigt, jetzt brauche ich Sortierung",
        "problem_ready_for_sorting_desc": "Direkt in Richtung Ordnerstruktur und Bereinigung gehen.",
        "problem_ready_for_rename_label": "Die Struktur passt, ich brauche vor allem bessere Namen",
        "problem_ready_for_rename_desc": "Mit einem leichteren Workflow starten, bei dem Namen im Fokus stehen.",
        "problem_exact_duplicates_only_label": "Ich will gerade nur exakte Duplikate prüfen",
        "problem_exact_duplicates_only_desc": "Nur garantierte byte-identische Duplikate prüfen.",
        "workflow_title": "Geführter Workflow",
        "workflow_subtitle": "Ab hier findet alles Wichtige Schritt für Schritt statt.",
        "stage_sources_title": "Wähle deine Quellordner aus",
        "stage_sources_subtitle": "Beginne mit den Ordnern, die du bereinigen willst.",
        "stage_sources_action": "Quellordner hinzufügen",
        "stage_sources_list_title": "Gewählte Quellordner",
        "stage_sources_empty": "Noch keine Quellordner ausgewählt.",
        "stage_target_title": "Wähle deinen Zielordner aus",
        "stage_target_subtitle": "Wähle, wo die bereinigte Bibliothek liegen soll.",
        "stage_target_action": "Zielordner auswählen",
        "stage_target_empty": "Noch kein Zielordner ausgewählt.",
        "stage_mode_title": "Was soll mit den Dateien passieren?",
        "stage_mode_subtitle": "Das kannst du vor der echten Ausführung noch ändern.",
        "mode_copy": "Kopieren",
        "mode_move": "Verschieben",
        "mode_delete": "Löschen",
        "stage_duplicates_title": "Duplikat-Prüfung Vorschau",
        "stage_duplicates_subtitle": "Starte die sichtbare Review-Phase für exakte Duplikate.",
        "stage_duplicates_action": "Duplikat-Prüfung starten",
        "stage_duplicates_hint": "Das ist noch ein Review-Popup, nicht das finale Vergleichstool.",
        "stage_summary_title": "Bereinigungs-Zusammenfassung",
        "stage_summary_subtitle": "Prüfe den aktuellen Wissensstand des Workflows, bevor spätere Ausführung und Sortierung folgen.",
        "stage_summary_action": "Weiter zur Sortierung",
        "summary_totals_title": "Aktuelle Bereinigungs-Summen",
        "summary_resolved_title": "Entscheidungsstand",
        "summary_dry_run_title": "Dry-Run-Grundlage",
        "summary_dry_run_body": "Diese Stufe führt noch nichts aus. Sie zeigt, was der Workflow aktuell aus den exakten Duplikat-Entscheidungen ableitet.",
        "summary_groups": "Exakte Gruppen",
        "summary_duplicate_files": "Duplikat-Dateien",
        "summary_extra_duplicates": "Zusätzliche Duplikate",
        "summary_resolved_groups": "Gelöste Gruppen",
        "summary_unresolved_groups": "Offene Gruppen",
        "summary_mode": "Aktueller Modus",
        "summary_ready_body": "Alle exakten Duplikat-Gruppen haben aktuell eine Keep-Entscheidung. Ein späterer Dry Run kann diese Entscheidungen in eine vollständige Bereinigungsvorschau übersetzen.",
        "summary_unresolved_body": "Einige exakte Duplikat-Gruppen haben noch keine Keep-Entscheidung. Prüfe sie, bevor du einem späteren Dry Run vertraust.",
        "summary_decision_status": "{resolved} gelöst / {unresolved} offen",
        "summary_plan_intro": "Bisherige Plan-Interpretation",
        "summary_plan_line_1": "Gelöste Gruppen behalten einen ausgewählten Survivor und markieren die restlichen exakten Treffer als entfernbaren Kandidatenbestand.",
        "summary_plan_line_2": "Offene Gruppen bleiben für eine vertrauenswürdige Dry-Run-Planung blockiert, bis ein Keep-Kandidat gewählt wurde.",
        "summary_plan_line_3": "Spätere Workflow-Stufen erweitern das zu Copy / Move / Delete-Vorschauen und Speicher-Einschätzungen.",
        "summary_planned_removals_title": "Geplante Entfern-Kandidaten",
        "summary_planned_removals_empty": "Aktuell sind noch keine entfernbaren exakten Treffer geplant.",
        "summary_unresolved_list_title": "Offene exakte Gruppen",
        "summary_unresolved_empty": "Es sind keine offenen exakten Gruppen mehr übrig.",
        "summary_keep_survivor_label": "Behalten",
        "summary_remove_candidate_label": "Entfernen",
        "summary_candidates_label": "Kandidaten",
        "summary_estimated_reclaimable_label": "Geschätzt freisetzbar",
        "table_name": "Name",
        "table_size": "Größe",
        "table_date": "Datum",
        "table_matches": "Duplikate",
        "table_score": "Übereinstimmung",
        "table_action": "Aktion",
        "table_show": "Anzeigen",
        "stage_sorting_title": "Sorting-Builder",
        "stage_sorting_subtitle": "Lege die Zielstruktur fest, bevor der Umbenennen-Schritt folgt.",
        "stage_sorting_action": "Weiter zu Umbenennen",
        "sorting_config_title": "Sortier-Konfiguration",
        "sorting_config_body": "Lege fest, wie Jahr, Monat und Tag in der Zielstruktur erscheinen sollen. Diese Vorschau nutzt aktuell die Zeitstempel der Quelldateien.",
        "sorting_level_year": "Jahr",
        "sorting_level_month": "Monat",
        "sorting_level_day": "Tag",
        "sorting_style_year_yyyy": "4-stelliges Jahr",
        "sorting_style_year_yy": "2-stelliges Jahr",
        "sorting_style_month_mm": "Monatszahl",
        "sorting_style_month_name": "Monatsname",
        "sorting_style_month_yyyy-mm": "Jahr-Monat",
        "sorting_style_day_dd": "Tageszahl",
        "sorting_style_day_yyyy-mm-dd": "Vollständiges Datum",
        "sorting_cycle_action": "Stil wechseln",
        "sorting_reset_action": "Standard zurücksetzen",
        "sorting_preview_title": "Vorschau Zielstruktur",
        "sorting_preview_body": "Einige echte Quelldateien werden auf ihre zukünftigen relativen Zielordner abgebildet.",
        "sorting_preview_source": "Quelle",
        "sorting_preview_date": "Datum",
        "sorting_preview_target": "Zielordner",
        "sorting_preview_empty": "Füge Quellordner mit Mediendateien hinzu, um eine Sortier-Vorschau zu sehen.",
        "sorting_template_title": "Live-Strukturvorlage",
        "sorting_template_body": "Diese Vorlage aktualisiert sich sofort und zeigt, wie die Ordnerstruktur später aussehen wird.",
        "sorting_template_live_source": "Vorlage basierend auf dem Datum der ersten gefundenen Quelldatei.",
        "sorting_template_sample_source": "Vorlage basierend auf einem Beispieldatum, bis echte Quelldaten verfügbar sind.",
        "sorting_preview_count": "{count} Vorschau-Einträge",
        "stage_rename_title": "Umbenennen-Setup Vorschau",
        "stage_rename_subtitle": "Die Umbenennungs-Konfiguration kommt nach dem Sortieren.",
        "stage_rename_action": "Weiter zur Zusammenfassung",
        "rename_config_title": "Umbenennen-Builder",
        "rename_config_body": "Starte mit zwei Kernblöcken und füge weitere nur bei Bedarf hinzu. Vorlagen sind jetzt nur noch Presets. Die echte Vorschau wird immer aus der aktiven Blockliste gebaut.",
        "rename_blocks_body": "Jeder Block steht für einen Teil des Dateinamens. Klicke auf einen Block, um ihn zu ändern. Zusätzliche Blöcke nur dann hinzufügen, wenn sie wirklich helfen.",
        "rename_add_block_action": "Block hinzufügen",
        "rename_remove_block_action": "Entfernen",
        "rename_block_press_to_change": "Klicken zum Ändern",
        "rename_block_optional": "Optionaler Block",
        "rename_block_primary": "Kernblock",
        "rename_template_title": "Live-Dateinamen-Vorlage",
        "rename_template_selector": "Vorlage",
        "rename_template_reset_action": "Vorlage zurücksetzen",
        "rename_template_live_source": "Vorschau basierend auf der ersten gefundenen Quelldatei.",
        "rename_template_sample_source": "Vorschau basierend auf einem Beispiel-Dateinamen, bis echte Quelldateien verfügbar sind.",
        "rename_preview_count": "{count} Vorschau-Einträge",
        "rename_blocks_title": "Aktive Blöcke",
        "rename_preview_title": "Umbenennen-Vorschau",
        "rename_preview_body": "Echte Quelldateien werden auf ihre vorgeschlagenen Namen abgebildet.",
        "rename_preview_empty": "Füge Quellordner mit Mediendateien hinzu, um Umbenennen-Vorschauen zu sehen.",
        "rename_template_custom": "Eigene Blöcke",
        "rename_template_readable_datetime_original": "Lesbares Datum + Uhrzeit + Originalname",
        "rename_template_year_month_day_time_original": "Jahr + Monat + Tag + Uhrzeit + Originalname",
        "rename_template_date_original": "ISO-Datum + Originalname",
        "rename_block_original_stem": "Originalname",
        "rename_block_year": "Jahr",
        "rename_block_month_name": "Monatsname",
        "rename_block_day": "Tag",
        "rename_block_date_iso": "ISO-Datum",
        "rename_block_date_readable": "Lesbares Datum",
        "rename_block_time_hhmmss": "Uhrzeit",
        "stage_done_title": "Glückwunsch",
        "stage_done_subtitle": "Das ist die Vorschau-Hülle für das spätere geführte Produkt.",
        "stage_done_action": "Vorschau beenden",
        "button_back": "Zurück",
        "button_next": "Weiter",
        "button_home": "Zurück zur Startseite",
        "button_clear": "Leeren",
        "button_remove": "Entfernen",
        "bottom_sources": "Quellen",
        "bottom_target": "Ziel",
        "bottom_mode": "Modus",
        "bottom_step": "Schritt",
        "bottom_files": "Dateien gefunden",
        "tip_1": "RAW-Dateien bieten meist deutlich mehr Spielraum für Bearbeitung als JPEG-Exporte.",
        "tip_2": "Exakte Duplikate sind das sicherste Ziel für eine erste Bereinigung, weil der Inhalt byte-identisch ist.",
        "tip_3": "Eine gute Ordnerstruktur spart später oft mehr Zeit als aggressives frühes Umbenennen.",
        "tip_4": "Ein verlässliches Backup ist wichtiger als ein perfekter erster Bereinigungsdurchlauf.",
        "tip_5": "Die blaue Stunde liefert oft weichere Kontraste als hartes Mittagslicht.",
        "tip_6": "Lange Brennweiten verstärken Verwacklungen stärker als Weitwinkel.",
        "tip_7": "Video-, Foto- und Sidecar-Dateien gehören oft zusammen und sollten nicht leichtfertig getrennt werden.",
        "tip_8": "Ein vertrauenswürdiger Dry Run ist wertvoller als ein vorschnelles Löschen.",
        "manual_placeholder_title": "Vorschau für manuelle Werkzeugseite",
        "manual_placeholder_body": "Diese Seite wird später dieselbe Workflow-Logik nutzen.",
        "manual_hint": "Nutze den geführten Workflow, außer du weißt schon genau, was du willst.",
        "language_tooltip": "Sprache wechseln",
        "status_sources_updated": "Quellordner aktualisiert",
        "status_target_updated": "Zielordner ausgewählt",
        "status_duplicates_preparing": "Exakte Duplikat-Prüfung wird vorbereitet ...",
        "status_duplicates_stage_1": "Medien nach Dateigröße gruppieren ...",
        "status_duplicates_stage_2": "Sample-Fingerprints vergleichen ...",
        "status_duplicates_stage_3": "Volle Hashes berechnen ...",
        "status_duplicates_stage_4": "Byte-identische Gruppen bestätigen ...",
        "status_duplicates_finished": "Exakte Gruppen: {groups} | Duplikat-Dateien: {files} | zusätzliche Duplikate: {extra} | Fehler: {errors}",
        "status_duplicates_none": "Keine exakten Duplikate gefunden. Fehler: {errors}",
        "status_duplicate_selection_saved": "Keep-Kandidat gesetzt auf {name}",
        "duplicate_detail_hint": "Schnelles Review-Popup, nicht das finale Vergleichstool.",
        "duplicate_detail_selected": "Gewählter Keep-Kandidat",
        "duplicate_detail_keep_selected": "Auswahl behalten",
        "duplicate_detail_keep_newest": "Neueste behalten",
        "duplicate_detail_keep_oldest": "Älteste behalten",
        "duplicate_detail_close": "Schließen",
        "duplicate_detail_path": "Pfad",
        "duplicate_detail_summary": "{files} Datei(en) | {size} | exakte Übereinstimmung",
    },
}

STAGE_KEYS = ["sources", "target", "mode", "duplicates", "summary", "sorting", "rename", "done"]
YEAR_STYLE_OPTIONS = ["yyyy", "yy"]
MONTH_STYLE_OPTIONS = ["mm", "name", "yyyy-mm"]
DAY_STYLE_OPTIONS = ["dd", "yyyy-mm-dd"]
DEFAULT_RENAME_TEMPLATE = "readable_datetime_original"
DEFAULT_RENAME_BLOCKS = [
    RenameBlock(kind="date_readable", position="prefix"),
    RenameBlock(kind="original_stem", position="suffix"),
]
RENAME_BLOCK_KIND_OPTIONS = [
    "date_readable",
    "date_iso",
    "time_hhmmss",
    "year",
    "month_name",
    "day",
    "original_stem",
]


class QmlAppState(QObject):
    languageChanged = Signal()
    pageChanged = Signal()
    wizardVisibleChanged = Signal()
    selectedProblemChanged = Signal()
    workflowChanged = Signal()
    liveStatsChanged = Signal()
    tipChanged = Signal()
    duplicateRowsChanged = Signal()
    duplicateDetailChanged = Signal()
    flagPathChanged = Signal()
    duplicateScanProgressEvent = Signal(int, int, str)
    duplicateScanResultEvent = Signal(int, object, object, object, int, int, int, int, int)

    def __init__(self) -> None:
        super().__init__()
        self._settings = QSettings("DevOpsOfChaos", "MediaManager")
        saved_language = str(self._settings.value("ui/language", "en"))
        if saved_language not in ("en", "de"):
            saved_language = "en"

        self._language = saved_language
        self._current_page = "home"
        self._wizard_visible = True
        self._selected_problem = "full_cleanup"
        self._workflow_stage_index = 0
        self._source_folders: list[str] = []
        self._target_path = ""
        self._operation_mode = "copy"
        self._discovered_file_count = 0
        self._tip_index = 0

        self._duplicate_started = False
        self._duplicate_scan_ready = False
        self._duplicate_progress = 0
        self._duplicate_rows_visible = 0
        self._duplicate_all_rows: list[dict[str, str]] = []
        self._duplicate_group_details: list[dict[str, object]] = []
        self._exact_duplicate_groups = []
        self._duplicate_decisions: dict[str, str] = {}
        self._duplicate_detail_group_index = -1
        self._duplicate_detail_selected_index = 0
        self._duplicate_scan_token = 0
        self._status_text = ""
        self._tips = ["tip_1", "tip_2", "tip_3", "tip_4", "tip_5", "tip_6", "tip_7", "tip_8"]

        self._summary_exact_group_count = 0
        self._summary_exact_duplicate_files = 0
        self._summary_extra_duplicates = 0
        self._summary_resolved_duplicate_groups = 0
        self._summary_unresolved_duplicate_groups = 0
        self._summary_planned_removals_preview: list[dict[str, str]] = []
        self._summary_unresolved_groups_preview: list[dict[str, str]] = []
        self._summary_planned_removal_count = 0
        self._summary_estimated_reclaimable_bytes = 0

        self._sorting_levels = [SortLevel(level.kind, level.style) for level in DEFAULT_SORT_LEVELS]
        self._sorting_preview_rows: list[dict[str, str]] = []
        self._sorting_template_path = ""
        self._sorting_template_hint = ""

        self._rename_template_keys = ["custom", *template_names()]
        self._rename_template_key = "custom"
        self._rename_blocks = [RenameBlock(block.kind, block.position) for block in DEFAULT_RENAME_BLOCKS]
        self._rename_preview_rows: list[dict[str, str]] = []
        self._rename_live_template_name = ""
        self._rename_live_template_hint = ""

        self.duplicateScanProgressEvent.connect(self._on_duplicate_scan_progress)
        self.duplicateScanResultEvent.connect(self._on_duplicate_scan_result)

        self._tip_timer = QTimer(self)
        self._tip_timer.timeout.connect(self._advance_tip)
        self._tip_timer.start(45000)

        self._live_timer = QTimer(self)
        self._live_timer.timeout.connect(self._advance_live_scan)
        self._live_timer.start(250)

        self._duplicate_reveal_timer = QTimer(self)
        self._duplicate_reveal_timer.timeout.connect(self._advance_duplicate_preview)
        self._duplicate_reveal_timer.start(180)

        self._rebuild_previews()

    def _format_text(self, key: str, **kwargs) -> str:
        text = TRANSLATIONS[self._language].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _flag_path(self, language: str) -> str:
        asset_path = resources.files("media_manager").joinpath(f"qml/assets/{language}_flag.svg")
        return QUrl.fromLocalFile(str(asset_path)).toString()

    def _normalize_folder_input(self, folder_value: str) -> str:
        if not folder_value:
            return ""
        local_file = QUrl(folder_value).toLocalFile()
        normalized = local_file or folder_value.replace("file:///", "")
        return str(Path(normalized)).replace("\\", "/")

    def _format_size(self, size_bytes: int) -> str:
        value = float(size_bytes)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                if unit == "B":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{int(size_bytes)} B"

    def _format_date(self, path: Path) -> str:
        try:
            return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
        except OSError:
            return "-"

    def _format_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M")

    def _progress_from_duplicate_message(self, message: str) -> tuple[int, str]:
        if message.startswith("Scanning source folders") or message.startswith("Found "):
            return 8, self._format_text("status_duplicates_preparing")
        if message.startswith("Stage 1/4"):
            return 26, self._format_text("status_duplicates_stage_1")
        if message.startswith("Stage 2/4"):
            return 52, self._format_text("status_duplicates_stage_2")
        if message.startswith("Stage 3/4"):
            return 76, self._format_text("status_duplicates_stage_3")
        if message.startswith("Stage 4/4"):
            return 92, self._format_text("status_duplicates_stage_4")
        return self._duplicate_progress, self._status_text

    def _selected_detail(self) -> dict[str, object] | None:
        if self._duplicate_detail_group_index < 0:
            return None
        if self._duplicate_detail_group_index >= len(self._duplicate_group_details):
            return None
        return self._duplicate_group_details[self._duplicate_detail_group_index]

    def _selected_index_for_detail(self, detail: dict[str, object]) -> int:
        files = detail.get("files", [])
        if not isinstance(files, list) or not files:
            return 0

        decision_path = self._duplicate_decisions.get(str(detail.get("group_id", "")), "")
        if decision_path:
            for index, item in enumerate(files):
                if str(item.get("path", "")) == decision_path:
                    return index
        return 0

    def _sorting_level(self, kind: str) -> SortLevel:
        for level in self._sorting_levels:
            if level.kind == kind:
                return level
        raise ValueError(f"Missing sorting level for kind {kind}")

    def _sorting_style_options(self, kind: str) -> list[str]:
        if kind == "year":
            return YEAR_STYLE_OPTIONS
        if kind == "month":
            return MONTH_STYLE_OPTIONS
        if kind == "day":
            return DAY_STYLE_OPTIONS
        raise ValueError(f"Unsupported sorting kind {kind}")

    def _sorting_style_label(self, kind: str, style: str) -> str:
        return self.text(f"sorting_style_{kind}_{style}")

    def _collect_media_preview_inputs(self, max_items: int = 8) -> list[tuple[Path, datetime]]:
        if not self._source_folders:
            return []

        items: list[tuple[Path, datetime]] = []
        source_paths = [Path(folder) for folder in self._source_folders]
        try:
            for path in iter_media_files(source_paths):
                try:
                    captured_at = datetime.fromtimestamp(path.stat().st_mtime)
                except OSError:
                    continue
                items.append((path, captured_at))
                if len(items) >= max_items:
                    break
        except Exception:
            return []
        return items

    def _rebuild_previews(self) -> None:
        self._rebuild_sorting_preview()
        self._rebuild_rename_preview()

    def _rebuild_sorting_preview(self) -> None:
        inputs = self._collect_media_preview_inputs()
        template_reference = inputs[0][1] if inputs else datetime.now()

        try:
            template_path = build_sort_preview(
                [(Path("template.jpg"), template_reference)],
                self._sorting_levels,
                language=self._language,
            )[0].relative_directory
            self._sorting_template_path = str(template_path).replace("\\", " / ")
        except Exception:
            self._sorting_template_path = ""
        self._sorting_template_hint = (
            self.text("sorting_template_live_source")
            if inputs
            else self.text("sorting_template_sample_source")
        )

        if not inputs:
            self._sorting_preview_rows = []
            self.workflowChanged.emit()
            return

        try:
            preview = build_sort_preview(inputs, self._sorting_levels, language=self._language)
        except Exception:
            self._sorting_preview_rows = []
            self.workflowChanged.emit()
            return

        self._sorting_preview_rows = [
            {
                "source_name": item.source_path.name,
                "source_path": str(item.source_path).replace("\\", "/"),
                "captured_at": self._format_datetime(item.captured_at),
                "relative_directory": str(item.relative_directory).replace("\\", "/"),
            }
            for item in preview
        ]
        self.workflowChanged.emit()

    def _rename_block_kind_label(self, kind: str) -> str:
        return self.text(f"rename_block_{kind}")

    def _rename_block_index(self, kind: str) -> int:
        if kind in RENAME_BLOCK_KIND_OPTIONS:
            return RENAME_BLOCK_KIND_OPTIONS.index(kind)
        return 0

    def _rename_blocks_match_template(self, template_key: str) -> bool:
        if template_key == "custom":
            return False
        try:
            template_blocks = blocks_for_template(template_key)
        except Exception:
            return False
        if len(template_blocks) != len(self._rename_blocks):
            return False
        return all(
            left.kind == right.kind and left.position == right.position
            for left, right in zip(self._rename_blocks, template_blocks)
        )

    def _sync_rename_template_key(self) -> None:
        for template_key in self._rename_template_keys:
            if self._rename_blocks_match_template(template_key):
                self._rename_template_key = template_key
                return
        self._rename_template_key = "custom"

    def _rebuild_rename_preview(self) -> None:
        self._sync_rename_template_key()
        inputs = self._collect_media_preview_inputs()
        sample_path = inputs[0][0] if inputs else Path("IMG_1234.JPG")
        sample_dt = inputs[0][1] if inputs else datetime.now()

        if self._rename_blocks:
            try:
                self._rename_live_template_name = build_filename_preview(
                    sample_path,
                    sample_dt,
                    self._rename_blocks,
                    language=self._language,
                )
            except Exception:
                self._rename_live_template_name = sample_path.name
        else:
            self._rename_live_template_name = sample_path.name

        self._rename_live_template_hint = (
            self.text("rename_template_live_source")
            if inputs
            else self.text("rename_template_sample_source")
        )

        if not inputs or not self._rename_blocks:
            self._rename_preview_rows = []
            self.workflowChanged.emit()
            return

        try:
            preview = build_rename_preview(
                inputs,
                self._rename_blocks,
                language=self._language,
            )
        except Exception:
            self._rename_preview_rows = []
            self.workflowChanged.emit()
            return

        self._rename_preview_rows = [
            {
                "source_name": item.source_path.name,
                "source_path": str(item.source_path).replace("\\", "/"),
                "proposed_name": item.proposed_name,
            }
            for item in preview
        ]
        self.workflowChanged.emit()

    def _cycle_sorting_style(self, kind: str) -> None:
        level = self._sorting_level(kind)
        options = self._sorting_style_options(kind)
        current_index = options.index(level.style)
        level.style = options[(current_index + 1) % len(options)]
        self._rebuild_sorting_preview()

    def _build_duplicate_rows_and_details(self, result) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
        rows: list[dict[str, str]] = []
        details: list[dict[str, object]] = []

        for index, group in enumerate(result.exact_groups):
            representative = group.files[0]
            group_id = f"{group.file_size}:{group.full_digest}"
            row = {
                "index": str(index),
                "group_id": group_id,
                "name": representative.name,
                "size": self._format_size(group.file_size),
                "date": self._format_date(representative),
                "matches": str(max(0, len(group.files) - 1)),
                "score": "100%",
            }
            rows.append(row)

            files: list[dict[str, str]] = []
            newest_index = 0
            oldest_index = 0
            newest_ts = None
            oldest_ts = None

            for file_index, path in enumerate(group.files):
                try:
                    modified_ts = path.stat().st_mtime
                except OSError:
                    modified_ts = None

                if newest_ts is None or (modified_ts is not None and modified_ts > newest_ts):
                    newest_ts = modified_ts
                    newest_index = file_index
                if oldest_ts is None or (modified_ts is not None and modified_ts < oldest_ts):
                    oldest_ts = modified_ts
                    oldest_index = file_index

                files.append(
                    {
                        "name": path.name,
                        "path": str(path).replace("\\", "/"),
                        "size": self._format_size(group.file_size),
                        "date": self._format_date(path),
                    }
                )

            details.append(
                {
                    "group_id": group_id,
                    "title": representative.name,
                    "file_count": len(group.files),
                    "size_label": self._format_size(group.file_size),
                    "files": files,
                    "newest_index": newest_index,
                    "oldest_index": oldest_index,
                }
            )

        return rows, details

    def _recompute_summary_state(self) -> None:
        plan = build_exact_cleanup_plan(
            self._exact_duplicate_groups,
            self._duplicate_decisions,
            self._operation_mode,
        )

        self._summary_exact_group_count = plan.total_groups
        self._summary_exact_duplicate_files = plan.duplicate_files
        self._summary_extra_duplicates = plan.extra_duplicates
        self._summary_resolved_duplicate_groups = plan.resolved_groups
        self._summary_unresolved_duplicate_groups = plan.unresolved_groups
        self._summary_planned_removal_count = len(plan.planned_removals)
        self._summary_estimated_reclaimable_bytes = plan.estimated_reclaimable_bytes

        self._summary_planned_removals_preview = [
            {
                "group_id": item.group_id,
                "keep_name": item.keep_path.name,
                "keep_path": str(item.keep_path).replace("\\", "/"),
                "remove_name": item.remove_path.name,
                "remove_path": str(item.remove_path).replace("\\", "/"),
                "size": self._format_size(item.file_size),
                "mode": self.text(f"mode_{item.operation_mode}"),
            }
            for item in plan.planned_removals[:8]
        ]

        self._summary_unresolved_groups_preview = []
        for item in plan.unresolved[:6]:
            names = [path.name for path in item.candidate_paths]
            preview_names = ", ".join(names[:3])
            if len(names) > 3:
                preview_names += ", ..."
            self._summary_unresolved_groups_preview.append(
                {
                    "group_id": item.group_id,
                    "candidate_count": str(len(item.candidate_paths)),
                    "size": self._format_size(item.file_size),
                    "preview_names": preview_names,
                }
            )

        self.workflowChanged.emit()
        self.liveStatsChanged.emit()

    def _reset_duplicate_state(self) -> None:
        self._duplicate_started = False
        self._duplicate_scan_ready = False
        self._duplicate_progress = 0
        self._duplicate_rows_visible = 0
        self._duplicate_all_rows = []
        self._duplicate_group_details = []
        self._exact_duplicate_groups = []
        self._duplicate_decisions = {}
        self._duplicate_detail_group_index = -1
        self._duplicate_detail_selected_index = 0
        self._summary_exact_group_count = 0
        self._summary_exact_duplicate_files = 0
        self._summary_extra_duplicates = 0
        self._summary_resolved_duplicate_groups = 0
        self._summary_unresolved_duplicate_groups = 0
        self._summary_planned_removals_preview = []
        self._summary_unresolved_groups_preview = []
        self._summary_planned_removal_count = 0
        self._summary_estimated_reclaimable_bytes = 0
        self.duplicateRowsChanged.emit()
        self.duplicateDetailChanged.emit()
        self.workflowChanged.emit()

    def _start_background_duplicate_scan(self) -> None:
        self._duplicate_scan_token += 1
        current_token = self._duplicate_scan_token
        self._reset_duplicate_state()

        if not self._source_folders:
            self._rebuild_previews()
            return

        source_paths = [Path(folder) for folder in self._source_folders]

        def worker() -> None:
            def progress_callback(message: str) -> None:
                progress_value, status_text = self._progress_from_duplicate_message(message)
                self.duplicateScanProgressEvent.emit(current_token, progress_value, status_text)

            try:
                result = scan_exact_duplicates(
                    DuplicateScanConfig(source_dirs=source_paths),
                    progress_callback=progress_callback,
                )
            except Exception:
                self.duplicateScanResultEvent.emit(current_token, [], [], [], 0, 0, 0, 0, 1)
                return

            rows, details = self._build_duplicate_rows_and_details(result)
            self.duplicateScanResultEvent.emit(
                current_token,
                rows,
                details,
                list(result.exact_groups),
                result.scanned_files,
                len(result.exact_groups),
                result.exact_duplicate_files,
                result.exact_duplicates,
                result.errors,
            )

        threading.Thread(target=worker, daemon=True).start()

    def _start_duplicate_reveal_if_ready(self) -> None:
        if not self._duplicate_started or not self._duplicate_scan_ready:
            return
        if not self._duplicate_all_rows:
            self._duplicate_progress = 100
            self.workflowChanged.emit()
            self.duplicateRowsChanged.emit()
            return
        self.workflowChanged.emit()
        self.duplicateRowsChanged.emit()

    @Slot(str, result=str)
    def text(self, key: str) -> str:
        return TRANSLATIONS[self._language].get(key, key)

    @Slot(str, result=str)
    def problemLabel(self, key: str) -> str:
        return self.text(f"problem_{key}_label")

    @Slot(str, result=str)
    def problemDescription(self, key: str) -> str:
        return self.text(f"problem_{key}_desc")

    @Property(str, notify=languageChanged)
    def language(self) -> str:
        return self._language

    @Property(str, notify=flagPathChanged)
    def flagPath(self) -> str:
        return self._flag_path(self._language)

    @Property(str, notify=pageChanged)
    def currentPage(self) -> str:
        return self._current_page

    @Property(bool, notify=wizardVisibleChanged)
    def wizardVisible(self) -> bool:
        return self._wizard_visible

    @Property(str, notify=selectedProblemChanged)
    def selectedProblem(self) -> str:
        return self._selected_problem

    @Property(int, notify=liveStatsChanged)
    def sourceCount(self) -> int:
        return len(self._source_folders)

    @Property("QVariantList", notify=liveStatsChanged)
    def sourceFolders(self) -> list[str]:
        return list(self._source_folders)

    @Property(str, notify=liveStatsChanged)
    def targetPath(self) -> str:
        return self._target_path

    @Property(str, notify=liveStatsChanged)
    def targetLabel(self) -> str:
        if not self._target_path:
            return "-"
        return Path(self._target_path).name or self._target_path

    @Property(str, notify=workflowChanged)
    def operationMode(self) -> str:
        return self._operation_mode

    @Property(int, notify=workflowChanged)
    def workflowStageIndex(self) -> int:
        return self._workflow_stage_index

    @Property(int, notify=workflowChanged)
    def workflowTotalSteps(self) -> int:
        return len(STAGE_KEYS)

    @Property(str, notify=workflowChanged)
    def workflowStageKey(self) -> str:
        return STAGE_KEYS[self._workflow_stage_index]

    @Property(str, notify=workflowChanged)
    def workflowStageTitle(self) -> str:
        return self.text(f"stage_{self.workflowStageKey}_title")

    @Property(str, notify=workflowChanged)
    def workflowStageSubtitle(self) -> str:
        return self.text(f"stage_{self.workflowStageKey}_subtitle")

    @Property(int, notify=liveStatsChanged)
    def discoveredFileCount(self) -> int:
        return self._discovered_file_count

    @Property(str, notify=tipChanged)
    def currentTip(self) -> str:
        return self.text(self._tips[self._tip_index])

    @Property(str, notify=workflowChanged)
    def statusText(self) -> str:
        return self._status_text

    @Property(int, notify=duplicateRowsChanged)
    def duplicateProgress(self) -> int:
        return self._duplicate_progress

    @Property("QVariantList", notify=duplicateRowsChanged)
    def duplicateRows(self) -> list[dict[str, str]]:
        if not self._duplicate_started:
            return []
        return self._duplicate_all_rows[: self._duplicate_rows_visible]

    @Property(int, notify=workflowChanged)
    def summaryExactGroupCount(self) -> int:
        return self._summary_exact_group_count

    @Property(int, notify=workflowChanged)
    def summaryExactDuplicateFiles(self) -> int:
        return self._summary_exact_duplicate_files

    @Property(int, notify=workflowChanged)
    def summaryExtraDuplicates(self) -> int:
        return self._summary_extra_duplicates

    @Property(int, notify=workflowChanged)
    def summaryResolvedDuplicateGroups(self) -> int:
        return self._summary_resolved_duplicate_groups

    @Property(int, notify=workflowChanged)
    def summaryUnresolvedDuplicateGroups(self) -> int:
        return self._summary_unresolved_duplicate_groups

    @Property(str, notify=workflowChanged)
    def summaryOperationModeLabel(self) -> str:
        return self.text(f"mode_{self._operation_mode}")

    @Property(bool, notify=workflowChanged)
    def summaryReadyForDryRun(self) -> bool:
        if self._summary_exact_group_count == 0:
            return self._duplicate_scan_ready
        return self._summary_unresolved_duplicate_groups == 0

    @Property(str, notify=workflowChanged)
    def summaryDecisionStatus(self) -> str:
        return self._format_text(
            "summary_decision_status",
            resolved=self._summary_resolved_duplicate_groups,
            unresolved=self._summary_unresolved_duplicate_groups,
        )

    @Property(int, notify=workflowChanged)
    def summaryPlannedRemovalCount(self) -> int:
        return self._summary_planned_removal_count

    @Property(str, notify=workflowChanged)
    def summaryEstimatedReclaimableSizeLabel(self) -> str:
        return self._format_size(self._summary_estimated_reclaimable_bytes)

    @Property("QVariantList", notify=workflowChanged)
    def summaryPlannedRemovalsPreview(self) -> list[dict[str, str]]:
        return list(self._summary_planned_removals_preview)

    @Property("QVariantList", notify=workflowChanged)
    def summaryUnresolvedGroupsPreview(self) -> list[dict[str, str]]:
        return list(self._summary_unresolved_groups_preview)

    @Property(str, notify=workflowChanged)
    def sortingYearStyleLabel(self) -> str:
        level = self._sorting_level("year")
        return self._sorting_style_label("year", level.style)

    @Property(str, notify=workflowChanged)
    def sortingMonthStyleLabel(self) -> str:
        level = self._sorting_level("month")
        return self._sorting_style_label("month", level.style)

    @Property(str, notify=workflowChanged)
    def sortingDayStyleLabel(self) -> str:
        level = self._sorting_level("day")
        return self._sorting_style_label("day", level.style)

    @Property(str, notify=workflowChanged)
    def sortingTemplatePathLabel(self) -> str:
        return self._sorting_template_path

    @Property(str, notify=workflowChanged)
    def sortingTemplateHintLabel(self) -> str:
        return self._sorting_template_hint

    @Property(str, notify=workflowChanged)
    def sortingPreviewCountLabel(self) -> str:
        return self._format_text("sorting_preview_count", count=len(self._sorting_preview_rows))

    @Property("QVariantList", notify=workflowChanged)
    def sortingPreviewRows(self) -> list[dict[str, str]]:
        return list(self._sorting_preview_rows)

    @Property(bool, notify=workflowChanged)
    def sortingPreviewReady(self) -> bool:
        return len(self._sorting_preview_rows) > 0

    @Property(str, notify=workflowChanged)
    def renameLiveTemplateName(self) -> str:
        return self._rename_live_template_name

    @Property(str, notify=workflowChanged)
    def renameLiveTemplateHint(self) -> str:
        return self._rename_live_template_hint

    @Property("QVariantList", notify=workflowChanged)
    def renameTemplateOptions(self) -> list[dict[str, str]]:
        return [{"key": key, "label": self.text(f"rename_template_{key}")} for key in self._rename_template_keys]

    @Property(int, notify=workflowChanged)
    def renameSelectedTemplateIndex(self) -> int:
        if self._rename_template_key in self._rename_template_keys:
            return self._rename_template_keys.index(self._rename_template_key)
        return 0

    @Property(str, notify=workflowChanged)
    def renamePreviewCountLabel(self) -> str:
        return self._format_text("rename_preview_count", count=len(self._rename_preview_rows))

    @Property("QVariantList", notify=workflowChanged)
    def renameBlockLabels(self) -> list[str]:
        return [self.text(f"rename_block_{block.kind}") for block in self._rename_blocks]

    @Property("QVariantList", notify=workflowChanged)
    def renameBlocks(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for index, block in enumerate(self._rename_blocks):
            rows.append(
                {
                    "index": index,
                    "kind": block.kind,
                    "label": self._rename_block_kind_label(block.kind),
                    "removable": index >= 2,
                    "slot_label": self.text("rename_block_primary") if index < 2 else self.text("rename_block_optional"),
                    "hint": self.text("rename_block_press_to_change"),
                }
            )
        return rows

    @Property("QVariantList", notify=workflowChanged)
    def renamePreviewRows(self) -> list[dict[str, str]]:
        return list(self._rename_preview_rows)

    @Property(str, notify=duplicateDetailChanged)
    def duplicateDetailTitle(self) -> str:
        detail = self._selected_detail()
        return str(detail.get("title", "")) if detail else ""

    @Property(str, notify=duplicateDetailChanged)
    def duplicateDetailSummary(self) -> str:
        detail = self._selected_detail()
        if not detail:
            return ""
        return self._format_text(
            "duplicate_detail_summary",
            files=int(detail.get("file_count", 0)),
            size=str(detail.get("size_label", "-")),
        )

    @Property("QVariantList", notify=duplicateDetailChanged)
    def duplicateDetailFiles(self) -> list[dict[str, object]]:
        detail = self._selected_detail()
        if not detail:
            return []

        items = detail.get("files", [])
        if not isinstance(items, list):
            return []

        rows: list[dict[str, object]] = []
        for index, item in enumerate(items):
            row = dict(item)
            row["selected"] = index == self._duplicate_detail_selected_index
            rows.append(row)
        return rows

    @Property(bool, notify=workflowChanged)
    def canAdvanceWorkflow(self) -> bool:
        key = self.workflowStageKey
        if key == "sources":
            return len(self._source_folders) > 0
        if key == "target":
            return bool(self._target_path)
        if key == "mode":
            return True
        if key == "duplicates":
            return self._duplicate_started and self._duplicate_progress >= 100
        if key == "summary":
            return self.summaryReadyForDryRun
        if key == "sorting":
            return self.sortingPreviewReady or len(self._source_folders) > 0
        return True

    @Slot()
    def toggleLanguage(self) -> None:
        self._language = "de" if self._language == "en" else "en"
        self._settings.setValue("ui/language", self._language)
        self._settings.sync()
        self._rebuild_previews()
        self.languageChanged.emit()
        self.flagPathChanged.emit()
        self.tipChanged.emit()
        self.workflowChanged.emit()
        self.pageChanged.emit()
        self.selectedProblemChanged.emit()
        self.liveStatsChanged.emit()
        self.duplicateDetailChanged.emit()

    @Slot(str)
    def setPage(self, page: str) -> None:
        if page == self._current_page:
            return
        self._current_page = page
        self.pageChanged.emit()

    @Slot()
    def dismissWizard(self) -> None:
        self._wizard_visible = False
        self.wizardVisibleChanged.emit()

    @Slot()
    def restartWizard(self) -> None:
        self._wizard_visible = True
        self.wizardVisibleChanged.emit()

    @Slot(str)
    def selectProblemAndStart(self, key: str) -> None:
        self._selected_problem = key
        self._workflow_stage_index = 0
        self._status_text = self.problemLabel(key)
        self._current_page = "workflow"
        self.selectedProblemChanged.emit()
        self.workflowChanged.emit()
        self.pageChanged.emit()

    @Slot(str)
    def setOperationMode(self, mode: str) -> None:
        self._operation_mode = mode
        self._status_text = self.text(f"mode_{mode}")
        self._recompute_summary_state()
        self.workflowChanged.emit()

    @Slot()
    def cycleSortingYearStyle(self) -> None:
        self._cycle_sorting_style("year")

    @Slot()
    def cycleSortingMonthStyle(self) -> None:
        self._cycle_sorting_style("month")

    @Slot()
    def cycleSortingDayStyle(self) -> None:
        self._cycle_sorting_style("day")

    @Slot()
    def resetSortingDefaults(self) -> None:
        self._sorting_levels = [SortLevel(level.kind, level.style) for level in DEFAULT_SORT_LEVELS]
        self._rebuild_sorting_preview()

    @Slot(int, result=str)
    def renameTemplateKeyAt(self, index: int) -> str:
        if index < 0 or index >= len(self._rename_template_keys):
            return ""
        return self._rename_template_keys[index]

    @Slot(str)
    def setRenameTemplate(self, template_key: str) -> None:
        if template_key not in self._rename_template_keys or template_key == "custom":
            return
        self._rename_template_key = template_key
        self._rename_blocks = blocks_for_template(template_key)
        self._rebuild_rename_preview()

    @Slot()
    def resetRenameTemplate(self) -> None:
        self._rename_template_key = "custom"
        self._rename_blocks = [RenameBlock(block.kind, block.position) for block in DEFAULT_RENAME_BLOCKS]
        self._rebuild_rename_preview()

    @Slot(str)
    def addSourceFolder(self, folder_value: str) -> None:
        folder = self._normalize_folder_input(folder_value)
        if not folder:
            return
        if folder not in self._source_folders:
            self._source_folders.append(folder)
        self._discovered_file_count = 0
        self._status_text = self._format_text("status_sources_updated")
        self.liveStatsChanged.emit()
        self.workflowChanged.emit()
        self._rebuild_previews()
        self._start_background_duplicate_scan()

    @Slot(int)
    def removeSourceFolder(self, index: int) -> None:
        if index < 0 or index >= len(self._source_folders):
            return
        del self._source_folders[index]
        self._discovered_file_count = 0
        self._status_text = self._format_text("status_sources_updated")
        self.liveStatsChanged.emit()
        self.workflowChanged.emit()
        self._rebuild_previews()
        self._start_background_duplicate_scan()

    @Slot()
    def clearSourceFolders(self) -> None:
        self._source_folders = []
        self._discovered_file_count = 0
        self._status_text = self._format_text("status_sources_updated")
        self._rebuild_previews()
        self._start_background_duplicate_scan()
        self.liveStatsChanged.emit()
        self.workflowChanged.emit()

    @Slot(str)
    def setTargetFolder(self, folder_value: str) -> None:
        folder = self._normalize_folder_input(folder_value)
        if not folder:
            return
        self._target_path = folder
        self._status_text = self._format_text("status_target_updated")
        self.liveStatsChanged.emit()
        self.workflowChanged.emit()

    @Slot()
    def clearTargetFolder(self) -> None:
        self._target_path = ""
        self._status_text = self._format_text("stage_target_empty")
        self.liveStatsChanged.emit()
        self.workflowChanged.emit()

    @Slot()
    def workflowNext(self) -> None:
        if not self.canAdvanceWorkflow:
            return
        if self._workflow_stage_index < len(STAGE_KEYS) - 1:
            self._workflow_stage_index += 1
            self._status_text = self.workflowStageTitle
            self.workflowChanged.emit()

    @Slot()
    def workflowBack(self) -> None:
        if self._workflow_stage_index > 0:
            self._workflow_stage_index -= 1
            self._status_text = self.workflowStageTitle
            self.workflowChanged.emit()
        else:
            self._current_page = "home"
            self.pageChanged.emit()

    @Slot()
    def startDuplicatePreview(self) -> None:
        self._duplicate_started = True
        if self._duplicate_scan_ready:
            self._start_duplicate_reveal_if_ready()
        else:
            self._status_text = self._format_text("status_duplicates_preparing")
        self.workflowChanged.emit()
        self.duplicateRowsChanged.emit()

    @Slot(int)
    def openDuplicateGroup(self, index: int) -> None:
        if index < 0 or index >= len(self._duplicate_group_details):
            return
        self._duplicate_detail_group_index = index
        detail = self._duplicate_group_details[index]
        self._duplicate_detail_selected_index = self._selected_index_for_detail(detail)
        self.duplicateDetailChanged.emit()

    @Slot()
    def closeDuplicateGroup(self) -> None:
        self._duplicate_detail_group_index = -1
        self._duplicate_detail_selected_index = 0
        self.duplicateDetailChanged.emit()

    @Slot(int)
    def selectDuplicateCandidate(self, index: int) -> None:
        detail = self._selected_detail()
        if not detail:
            return

        files = detail.get("files", [])
        if not isinstance(files, list):
            return
        if index < 0 or index >= len(files):
            return

        self._duplicate_detail_selected_index = index
        self.duplicateDetailChanged.emit()

    @Slot()
    def chooseDuplicateKeepNewest(self) -> None:
        detail = self._selected_detail()
        if not detail:
            return
        self._duplicate_detail_selected_index = int(detail.get("newest_index", 0))
        self.duplicateDetailChanged.emit()

    @Slot()
    def chooseDuplicateKeepOldest(self) -> None:
        detail = self._selected_detail()
        if not detail:
            return
        self._duplicate_detail_selected_index = int(detail.get("oldest_index", 0))
        self.duplicateDetailChanged.emit()

    @Slot()
    def keepSelectedDuplicateCandidate(self) -> None:
        detail = self._selected_detail()
        if not detail:
            return

        files = detail.get("files", [])
        if not isinstance(files, list) or not files:
            return
        if self._duplicate_detail_selected_index < 0 or self._duplicate_detail_selected_index >= len(files):
            return

        selected = files[self._duplicate_detail_selected_index]
        selected_path = str(selected.get("path", ""))
        if not selected_path:
            return

        self._duplicate_decisions[str(detail.get("group_id", ""))] = selected_path
        self._status_text = self._format_text(
            "status_duplicate_selection_saved",
            name=str(selected.get("name", "")),
        )
        self._recompute_summary_state()
        self.workflowChanged.emit()
        self.duplicateDetailChanged.emit()

    @Slot(int)
    def cycleRenameBlock(self, index: int) -> None:
        if index < 0 or index >= len(self._rename_blocks):
            return
        current_kind = self._rename_blocks[index].kind
        current_index = self._rename_block_index(current_kind)
        next_kind = RENAME_BLOCK_KIND_OPTIONS[(current_index + 1) % len(RENAME_BLOCK_KIND_OPTIONS)]
        self._rename_blocks[index] = RenameBlock(kind=next_kind, position=self._rename_blocks[index].position)
        self._rebuild_rename_preview()

    @Slot()
    def addRenameBlock(self) -> None:
        self._rename_blocks.append(RenameBlock(kind="time_hhmmss", position="prefix"))
        self._rebuild_rename_preview()

    @Slot(int)
    def removeRenameBlock(self, index: int) -> None:
        if index < 2 or index >= len(self._rename_blocks):
            return
        del self._rename_blocks[index]
        self._rebuild_rename_preview()

    @Slot()
    def backToHome(self) -> None:
        self._current_page = "home"
        self.pageChanged.emit()

    @Slot(int, int, str)
    def _on_duplicate_scan_progress(self, token: int, progress: int, status_text: str) -> None:
        if token != self._duplicate_scan_token:
            return
        self._duplicate_progress = max(self._duplicate_progress, progress)
        self._status_text = status_text
        self.workflowChanged.emit()
        self.duplicateRowsChanged.emit()

    @Slot(int, object, object, object, int, int, int, int, int)
    def _on_duplicate_scan_result(
        self,
        token: int,
        rows: object,
        details: object,
        exact_groups_payload: object,
        scanned_files: int,
        exact_groups: int,
        duplicate_files: int,
        extra_duplicates: int,
        errors: int,
    ) -> None:
        if token != self._duplicate_scan_token:
            return
        self._duplicate_scan_ready = True
        self._duplicate_all_rows = list(rows)
        self._duplicate_group_details = list(details)
        self._exact_duplicate_groups = list(exact_groups_payload)
        self._duplicate_rows_visible = 0
        self._discovered_file_count = max(self._discovered_file_count, scanned_files)
        self._recompute_summary_state()
        self._rebuild_previews()
        if exact_groups > 0:
            self._status_text = self._format_text(
                "status_duplicates_finished",
                groups=exact_groups,
                files=duplicate_files,
                extra=extra_duplicates,
                errors=errors,
            )
            self._duplicate_progress = max(self._duplicate_progress, 96)
        else:
            self._status_text = self._format_text("status_duplicates_none", errors=errors)
            self._duplicate_progress = max(self._duplicate_progress, 96)
        self.liveStatsChanged.emit()
        self.workflowChanged.emit()
        self.duplicateRowsChanged.emit()
        self.duplicateDetailChanged.emit()
        self._start_duplicate_reveal_if_ready()

    def _advance_tip(self) -> None:
        self._tip_index = (self._tip_index + 1) % len(self._tips)
        self.tipChanged.emit()

    def _advance_live_scan(self) -> None:
        if self._current_page != "workflow":
            return
        if not self._source_folders:
            return
        if self._duplicate_scan_ready:
            return
        max_files = 18000 * max(1, len(self._source_folders))
        step = 90 + (35 * len(self._source_folders))
        if self._discovered_file_count < max_files:
            self._discovered_file_count = min(max_files, self._discovered_file_count + step)
            self.liveStatsChanged.emit()

    def _advance_duplicate_preview(self) -> None:
        if not self._duplicate_started or not self._duplicate_scan_ready:
            return
        did_change = False
        if self._duplicate_rows_visible < len(self._duplicate_all_rows):
            self._duplicate_rows_visible += 1
            did_change = True
        if self._duplicate_progress < 100:
            self._duplicate_progress = min(100, self._duplicate_progress + 5)
            did_change = True
        if did_change:
            self.workflowChanged.emit()
            self.duplicateRowsChanged.emit()


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("DevOpsOfChaos")
    app.setApplicationName("Media Manager QML")

    engine = QQmlApplicationEngine()
    state = QmlAppState()
    engine.rootContext().setContextProperty("appState", state)

    qml_file = resources.files("media_manager").joinpath("qml/Main.qml")
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        return 1
    return app.exec()
