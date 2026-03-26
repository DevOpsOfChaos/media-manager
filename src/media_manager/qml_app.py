from __future__ import annotations

import sys
import threading
from datetime import datetime
from importlib import resources
from pathlib import Path

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .duplicates import DuplicateScanConfig, scan_exact_duplicates

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
        "home_info_body": "The workflow helps you clean duplicates first, then organize the result, then rename the remaining media. Manual tools remain available in the side menu if you already know exactly what you want to do.",
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
        "stage_sources_subtitle": "Start with the folders you want to clean. The app can already begin scanning and counting media in the background.",
        "stage_sources_action": "Add source folder",
        "stage_sources_list_title": "Selected source folders",
        "stage_sources_empty": "No source folders selected yet.",
        "stage_target_title": "Select your target folder",
        "stage_target_subtitle": "Choose the place where the cleaned library should live. This target will later hold hidden workflow state as well.",
        "stage_target_action": "Select target folder",
        "stage_target_empty": "No target folder selected yet.",
        "stage_mode_title": "What should happen to the files?",
        "stage_mode_subtitle": "You can still change this later before real execution.",
        "mode_copy": "Copy",
        "mode_move": "Move",
        "mode_delete": "Delete",
        "stage_duplicates_title": "Duplicate review preview",
        "stage_duplicates_subtitle": "The scan already started in the background. The Start button mainly opens the visible review phase.",
        "stage_duplicates_action": "Start duplicate review",
        "stage_duplicates_hint": "This is a preview foundation. The final visual compare tool will be more powerful than this quick review screen.",
        "table_name": "Name",
        "table_size": "Size",
        "table_date": "Date",
        "table_matches": "Matches",
        "table_score": "Score",
        "table_action": "Action",
        "table_show": "Show",
        "stage_sorting_title": "Sorting setup preview",
        "stage_sorting_subtitle": "Later this page will let the user define folder structure blocks like year / month / day and optional trip support.",
        "stage_sorting_action": "Continue to rename",
        "stage_rename_title": "Rename setup preview",
        "stage_rename_subtitle": "Later this page will support readable templates, rename blocks, and preset patterns.",
        "stage_rename_action": "Continue to summary",
        "stage_done_title": "Congratulations",
        "stage_done_subtitle": "This preview foundation shows the future shell: guided flow, bottom status bar, staged review, and a modern entry point.",
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
        "tip_1": "Tip: exact duplicates are the safest cleanup wins.",
        "tip_2": "Photography fact: JPEG and RAW from the same shot should be treated as related but not identical files.",
        "tip_3": "Good cleanup workflows reduce chaos before folder sorting starts.",
        "tip_4": "History: early digital cameras often produced vendor-specific side files next to the image itself.",
        "manual_placeholder_title": "Manual tool page preview",
        "manual_placeholder_body": "This page will later reuse the same workflow logic, but without the guided entry path.",
        "manual_hint": "Use the guided workflow unless you already know exactly which tool you want.",
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
        "duplicate_detail_hint": "This is still a quick review popup, not the final advanced compare tool.",
        "duplicate_detail_selected": "Selected keep candidate",
        "duplicate_detail_keep_selected": "Keep selected",
        "duplicate_detail_keep_newest": "Keep newest",
        "duplicate_detail_keep_oldest": "Keep oldest",
        "duplicate_detail_close": "Close",
        "duplicate_detail_path": "Path",
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
        "home_info_body": "Der Workflow hilft zuerst beim Duplikat-Bereinigen, danach beim Sortieren und anschließend beim Umbenennen. Manuelle Werkzeuge bleiben in der Seitenleiste verfügbar, wenn du schon genau weißt, was du tun willst.",
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
        "stage_sources_subtitle": "Beginne mit den Ordnern, die du bereinigen willst. Die App kann dabei schon im Hintergrund scannen und zählen.",
        "stage_sources_action": "Quellordner hinzufügen",
        "stage_sources_list_title": "Gewählte Quellordner",
        "stage_sources_empty": "Noch keine Quellordner ausgewählt.",
        "stage_target_title": "Wähle deinen Zielordner aus",
        "stage_target_subtitle": "Wähle den Ort, an dem die bereinigte Bibliothek später liegen soll. Dort wird später auch der versteckte Workflow-Zustand abgelegt.",
        "stage_target_action": "Zielordner auswählen",
        "stage_target_empty": "Noch kein Zielordner ausgewählt.",
        "stage_mode_title": "Was soll mit den Dateien passieren?",
        "stage_mode_subtitle": "Das kann vor der echten Ausführung später noch geändert werden.",
        "mode_copy": "Kopieren",
        "mode_move": "Verschieben",
        "mode_delete": "Löschen",
        "stage_duplicates_title": "Duplikat-Prüfung Vorschau",
        "stage_duplicates_subtitle": "Der Scan läuft im Hintergrund bereits an. Der Start-Button öffnet hauptsächlich die sichtbare Review-Phase.",
        "stage_duplicates_action": "Duplikat-Prüfung starten",
        "stage_duplicates_hint": "Das ist nur das Grundgerüst. Das finale Vergleichstool wird deutlich stärker als diese schnelle Review-Ansicht.",
        "table_name": "Name",
        "table_size": "Größe",
        "table_date": "Datum",
        "table_matches": "Duplikate",
        "table_score": "Übereinstimmung",
        "table_action": "Aktion",
        "table_show": "Anzeigen",
        "stage_sorting_title": "Sortier-Setup Vorschau",
        "stage_sorting_subtitle": "Später kann der Nutzer hier Ordner-Ebenen wie Jahr / Monat / Tag und optional eine Trip-Unterstützung definieren.",
        "stage_sorting_action": "Weiter zu Umbenennen",
        "stage_rename_title": "Umbenennen-Setup Vorschau",
        "stage_rename_subtitle": "Später wird diese Seite lesbare Templates, Namensblöcke und Vorlagen unterstützen.",
        "stage_rename_action": "Weiter zur Zusammenfassung",
        "stage_done_title": "Glückwunsch",
        "stage_done_subtitle": "Dieses Grundgerüst zeigt die künftige Hülle: geführter Ablauf, untere Statusleiste, gestufte Review und ein moderner Einstiegspunkt.",
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
        "tip_1": "Tipp: exakte Duplikate sind die sichersten Gewinne bei der Bereinigung.",
        "tip_2": "Foto-Fakt: JPEG und RAW vom selben Foto sind zusammengehörig, aber nicht identisch.",
        "tip_3": "Gute Bereinigungs-Workflows reduzieren das Chaos, bevor die Sortierung beginnt.",
        "tip_4": "Geschichte: frühe Digitalkameras erzeugten oft herstellerspezifische Zusatzdateien neben dem Bild.",
        "manual_placeholder_title": "Vorschau für manuelle Werkzeugseite",
        "manual_placeholder_body": "Diese Seite wird später dieselbe Workflow-Logik nutzen, aber ohne geführten Einstiegspfad.",
        "manual_hint": "Nutze den geführten Workflow, außer du weißt schon ganz genau, welches Werkzeug du willst.",
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
        "duplicate_detail_hint": "Das ist noch ein schnelles Review-Popup und nicht das finale Vergleichstool.",
        "duplicate_detail_selected": "Gewählter Keep-Kandidat",
        "duplicate_detail_keep_selected": "Auswahl behalten",
        "duplicate_detail_keep_newest": "Neueste behalten",
        "duplicate_detail_keep_oldest": "Älteste behalten",
        "duplicate_detail_close": "Schließen",
        "duplicate_detail_path": "Pfad",
    },
}

STAGE_KEYS = ["sources", "target", "mode", "duplicates", "sorting", "rename", "done"]

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
    duplicateScanResultEvent = Signal(int, object, object, int, int, int, int, int)

    def __init__(self) -> None:
        super().__init__()
        self._language = "en"
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
        self._duplicate_detail_open = False
        self._duplicate_detail_group_index = -1
        self._duplicate_detail_selected_index = 0
        self._duplicate_scan_token = 0
        self._status_text = ""
        self._tips = ["tip_1", "tip_2", "tip_3", "tip_4"]

        self.duplicateScanProgressEvent.connect(self._on_duplicate_scan_progress)
        self.duplicateScanResultEvent.connect(self._on_duplicate_scan_result)

        self._tip_timer = QTimer(self)
        self._tip_timer.timeout.connect(self._advance_tip)
        self._tip_timer.start(3200)

        self._live_timer = QTimer(self)
        self._live_timer.timeout.connect(self._advance_live_scan)
        self._live_timer.start(250)

        self._duplicate_reveal_timer = QTimer(self)
        self._duplicate_reveal_timer.timeout.connect(self._advance_duplicate_preview)
        self._duplicate_reveal_timer.start(180)

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

    def _build_duplicate_rows_and_details(self, result) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
        rows: list[dict[str, str]] = []
        details: list[dict[str, object]] = []
        for index, group in enumerate(result.exact_groups):
            representative = group.files[0]
            matches = max(0, len(group.files) - 1)
            rows.append(
                {
                    "index": str(index),
                    "name": representative.name,
                    "size": self._format_size(group.file_size),
                    "date": self._format_date(representative),
                    "matches": str(matches),
                    "score": "100%",
                }
            )
            files = []
            newest_index = 0
            oldest_index = 0
            newest_ts = None
            oldest_ts = None
            for file_index, path in enumerate(group.files):
                try:
                    ts = path.stat().st_mtime
                except OSError:
                    ts = None
                if newest_ts is None or (ts is not None and ts > newest_ts):
                    newest_ts = ts
                    newest_index = file_index
                if oldest_ts is None or (ts is not None and ts < oldest_ts):
                    oldest_ts = ts
                    oldest_index = file_index
                files.append(
                    {
                        "name": path.name,
                        "path": str(path).replace("\\", "/"),
                        "size": self._format_size(group.file_size),
                        "date": self._format_date(path),
                        "keep": file_index == 0,
                    }
                )
            details.append(
                {
                    "title": representative.name,
                    "summary": f"{len(group.files)} file(s) | {self._format_size(group.file_size)} | exact match",
                    "files": files,
                    "newest_index": newest_index,
                    "oldest_index": oldest_index,
                }
            )
        return rows, details

    def _selected_detail(self) -> dict[str, object] | None:
        if self._duplicate_detail_group_index < 0:
            return None
        if self._duplicate_detail_group_index >= len(self._duplicate_group_details):
            return None
        return self._duplicate_group_details[self._duplicate_detail_group_index]

    def _reset_duplicate_state(self) -> None:
        self._duplicate_started = False
        self._duplicate_scan_ready = False
        self._duplicate_progress = 0
        self._duplicate_rows_visible = 0
        self._duplicate_all_rows = []
        self._duplicate_group_details = []
        self._duplicate_detail_open = False
        self._duplicate_detail_group_index = -1
        self._duplicate_detail_selected_index = 0
        self.duplicateRowsChanged.emit()
        self.duplicateDetailChanged.emit()
        self.workflowChanged.emit()

    def _start_background_duplicate_scan(self) -> None:
        self._duplicate_scan_token += 1
        current_token = self._duplicate_scan_token
        self._reset_duplicate_state()
        if not self._source_folders:
            return
        source_paths = [Path(folder) for folder in self._source_folders]

        def worker() -> None:
            def progress_callback(message: str) -> None:
                progress_value, status_text = self._progress_from_duplicate_message(message)
                self.duplicateScanProgressEvent.emit(current_token, progress_value, status_text)
            try:
                result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=source_paths), progress_callback=progress_callback)
            except Exception:
                self.duplicateScanResultEvent.emit(current_token, [], [], 0, 0, 0, 0, 1)
                return
            rows, details = self._build_duplicate_rows_and_details(result)
            self.duplicateScanResultEvent.emit(
                current_token,
                rows,
                details,
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

    @Property(bool, notify=duplicateDetailChanged)
    def duplicateDetailOpen(self) -> bool:
        return self._duplicate_detail_open

    @Property(str, notify=duplicateDetailChanged)
    def duplicateDetailTitle(self) -> str:
        detail = self._selected_detail()
        return str(detail.get("title", "")) if detail else ""

    @Property(str, notify=duplicateDetailChanged)
    def duplicateDetailSummary(self) -> str:
        detail = self._selected_detail()
        return str(detail.get("summary", "")) if detail else ""

    @Property("QVariantList", notify=duplicateDetailChanged)
    def duplicateDetailFiles(self) -> list[dict[str, object]]:
        detail = self._selected_detail()
        if not detail:
            return []
        files = []
        for index, item in enumerate(detail.get("files", [])):
            row = dict(item)
            row["selected"] = index == self._duplicate_detail_selected_index
            files.append(row)
        return files

    @Property(str, notify=duplicateDetailChanged)
    def duplicateDetailSelectedName(self) -> str:
        detail = self._selected_detail()
        if not detail:
            return ""
        files = detail.get("files", [])
        if not files or self._duplicate_detail_selected_index >= len(files):
            return ""
        return str(files[self._duplicate_detail_selected_index].get("name", ""))

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
        return True

    @Slot()
    def toggleLanguage(self) -> None:
        self._language = "de" if self._language == "en" else "en"
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
        self.workflowChanged.emit()

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
        self._start_background_duplicate_scan()

    @Slot()
    def clearSourceFolders(self) -> None:
        self._source_folders = []
        self._discovered_file_count = 0
        self._status_text = self._format_text("status_sources_updated")
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
        self._duplicate_detail_selected_index = 0
        self._duplicate_detail_open = True
        self.duplicateDetailChanged.emit()

    @Slot()
    def closeDuplicateGroup(self) -> None:
        self._duplicate_detail_open = False
        self.duplicateDetailChanged.emit()

    @Slot(int)
    def selectDuplicateCandidate(self, index: int) -> None:
        detail = self._selected_detail()
        if not detail:
            return
        files = detail.get("files", [])
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
        self.duplicateDetailChanged.emit()

    @Slot()
    def backToHome(self) -> None:
        self._current_page = "home"
        self.pageChanged.emit()

    @Slot(int, int, str)
    def _on_duplicate_scan_progress(self, token: int, progress: int, status_text: str) -> None:
        if token != self._duplicate_scan_token:
            return
        self._duplicate_progress = max(self._duplicate_progress, progress)
        if not self._duplicate_started:
            self._status_text = status_text
        self.workflowChanged.emit()
        self.duplicateRowsChanged.emit()

    @Slot(int, object, object, int, int, int, int, int)
    def _on_duplicate_scan_result(self, token: int, rows: object, details: object, scanned_files: int, exact_groups: int, duplicate_files: int, extra_duplicates: int, errors: int) -> None:
        if token != self._duplicate_scan_token:
            return
        self._duplicate_scan_ready = True
        self._duplicate_all_rows = list(rows)
        self._duplicate_group_details = list(details)
        self._duplicate_rows_visible = 0
        self._discovered_file_count = max(self._discovered_file_count, scanned_files)
        if exact_groups > 0:
            self._status_text = self._format_text("status_duplicates_finished", groups=exact_groups, files=duplicate_files, extra=extra_duplicates, errors=errors)
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
        if self._current_page != "workflow" or not self._source_folders or self._duplicate_scan_ready:
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
    app.setApplicationName("Media Manager QML")
    engine = QQmlApplicationEngine()
    state = QmlAppState()
    engine.rootContext().setContextProperty("appState", state)
    qml_file = resources.files("media_manager").joinpath("qml/Main.qml")
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        return 1
    return app.exec()
