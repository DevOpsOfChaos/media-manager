from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_review_workbench_confirmation_dialog import (
    REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND,
    build_review_workbench_confirmation_dialog_model,
    write_review_workbench_confirmation_dialog_model,
)
from media_manager.core.gui_review_workbench_service import build_gui_review_workbench_service_bundle
from media_manager.core.gui_page_models import build_page_model
from media_manager.gui_review_workbench_qt import build_review_workbench_page_widget


class _Signal:
    def __init__(self) -> None:
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)


class _Widget:
    def __init__(self, *args):
        self.args = args
        self.properties = {}
        self.children = []
        self.triggered = _Signal()
        self.textChanged = _Signal()
        self.currentTextChanged = _Signal()
        self.itemSelectionChanged = _Signal()
        self.cellDoubleClicked = _Signal()
        self.clicked = _Signal()
        self._current_row = 0

    def setObjectName(self, name):
        self.object_name = name

    def setProperty(self, key, value):
        self.properties[key] = value

    def setEnabled(self, value):
        self.enabled = bool(value)

    def setWordWrap(self, value):
        self.properties["word_wrap"] = bool(value)

    def setPlaceholderText(self, value):
        self.properties["placeholder"] = value

    def setText(self, value):
        self.text = value

    def setPlainText(self, value):
        self.text = value

    def setReadOnly(self, value):
        self.properties["read_only"] = bool(value)

    def addItems(self, values):
        self.items = list(values)

    def setColumnCount(self, value):
        self.properties["column_count"] = value

    def setRowCount(self, value):
        self.properties["row_count"] = value

    def setHorizontalHeaderLabels(self, values):
        self.properties["headers"] = list(values)

    def setItem(self, row, column, item):
        self.children.append((row, column, item))

    def setAlternatingRowColors(self, value):
        self.properties["alternating"] = bool(value)

    def setContentsMargins(self, *args):
        self.properties["contents_margins"] = args

    def setSpacing(self, value):
        self.properties["spacing"] = value

    def addAction(self, label):
        action = _Widget(label)
        self.children.append(("action", action))
        return action

    def addWidget(self, widget, *args):
        self.children.append(("widget", widget, args))

    def addLayout(self, layout):
        self.children.append(("layout", layout))

    def addStretch(self, value=1):
        self.children.append(("stretch", value))

    def currentRow(self):
        return self._current_row


class _Layout(_Widget):
    pass


class _QtWidgets:
    QWidget = _Widget
    QLabel = _Widget
    QToolBar = _Widget
    QLineEdit = _Widget
    QComboBox = _Widget
    QTableWidget = _Widget
    QTableWidgetItem = _Widget
    QTextEdit = _Widget
    QPushButton = _Widget
    QSplitter = _Widget
    QVBoxLayout = _Layout
    QHBoxLayout = _Layout


def _reviewed_plan() -> dict[str, object]:
    return {
        "status": "reviewed",
        "safe_to_preview_apply": True,
        "reviewed_decision_count": 2,
        "command_preview": [["media-manager", "duplicates", "--import-decisions", "decisions.json", "--show-plan"]],
    }


def test_confirmation_dialog_blocks_without_apply_preview_ready() -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1}, selected_lane_id="duplicates")
    dialog = service["confirmation_dialog"]

    assert dialog["kind"] == REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND
    assert dialog["readiness"]["ready"] is False
    assert dialog["summary"]["status"] == "blocked"
    assert dialog["summary"]["apply_enabled"] is False
    assert dialog["capabilities"]["executes_commands"] is False
    assert any(item["id"] == "typed-confirmation-required" for item in dialog["checklist"])


def test_confirmation_dialog_renders_ready_preview_without_enabling_apply() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )
    dialog = service["confirmation_dialog"]

    assert dialog["readiness"]["ready"] is True
    assert dialog["summary"]["status"] == "confirmation_ready"
    assert dialog["summary"]["candidate_command_count"] == 1
    assert dialog["summary"]["reviewed_decision_count"] == 2
    assert dialog["summary"]["apply_enabled"] is False
    assert dialog["confirmation"]["phrase"] == "APPLY REVIEWED DECISIONS"
    assert dialog["confirmation"]["typed_confirmation_satisfied"] is False
    assert dialog["command_plan_preview"]["commands"][0]["executes_commands"] is False
    assert service["capabilities"]["review_workbench_confirmation_dialog_available"] is True


def test_confirmation_dialog_writer_creates_split_artifacts(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )

    result = write_review_workbench_confirmation_dialog_model(tmp_path, service["apply_preview"])

    assert result["written_file_count"] == 3
    assert (tmp_path / "review_workbench_confirmation_dialog_model.json").exists()
    assert (tmp_path / "review_workbench_confirmation_checklist.json").exists()
    loaded = json.loads((tmp_path / "review_workbench_confirmation_dialog_model.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND
    assert loaded["capabilities"]["executes_commands"] is False


def test_cli_confirmation_dialog_json_and_out_dir(tmp_path: Path, capsys) -> None:
    reviewed = tmp_path / "reviewed.json"
    reviewed.write_text(json.dumps(_reviewed_plan()), encoding="utf-8")

    assert app_services_main(["review-workbench-confirmation-dialog", "--reviewed-decision-plan-json", str(reviewed), "--selected-lane", "duplicates", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND
    assert payload["summary"]["status"] == "confirmation_ready"
    assert payload["summary"]["apply_enabled"] is False

    out_dir = tmp_path / "confirmation-dialog"
    assert app_services_main(["review-workbench-confirmation-dialog", "--reviewed-decision-plan-json", str(reviewed), "--out-dir", str(out_dir)]) == 0
    assert "GUI Review Workbench confirmation dialog" in capsys.readouterr().out
    assert (out_dir / "review_workbench_confirmation_dialog_model.json").exists()


def test_page_and_lazy_qt_mount_expose_confirmation_dialog() -> None:
    page = build_page_model("review-workbench", {}, query="")
    assert page["confirmation_dialog"]["kind"] == REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND

    mount = build_review_workbench_page_widget(_QtWidgets, page)
    assert mount.confirmation_dialog["kind"] == REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND
    assert mount.model_sources["confirmation_dialog"]["capabilities"]["executes_commands"] is False
