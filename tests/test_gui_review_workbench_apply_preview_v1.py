from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_review_workbench_apply_preview import (
    REVIEW_WORKBENCH_APPLY_PREVIEW_KIND,
    build_review_workbench_apply_preview,
    write_review_workbench_apply_preview,
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
        "reviewed_decision_count": 3,
        "command_preview": [["media-manager", "duplicates", "--import-decisions", "decisions.json", "--show-plan"]],
    }


def test_apply_preview_blocks_without_reviewed_plan() -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 2}, selected_lane_id="duplicates")
    preview = build_review_workbench_apply_preview(service)

    assert preview["kind"] == REVIEW_WORKBENCH_APPLY_PREVIEW_KIND
    assert preview["readiness"]["ready"] is False
    assert preview["summary"]["status"] == "blocked"
    assert preview["summary"]["apply_enabled"] is False
    assert preview["capabilities"]["executes_commands"] is False
    assert preview["command_plan_preview"]["enabled"] is False


def test_apply_preview_accepts_clean_reviewed_plan_without_execution() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 2},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )
    preview = service["apply_preview"]

    assert preview["readiness"]["ready"] is True
    assert preview["summary"]["preview_ready"] is True
    assert preview["summary"]["reviewed_decision_count"] == 3
    assert preview["summary"]["candidate_command_count"] == 1
    assert preview["summary"]["apply_enabled"] is False
    assert preview["command_plan_preview"]["confirmation"]["required"] is True
    assert preview["command_plan_preview"]["commands"][0]["executes_commands"] is False
    assert service["capabilities"]["review_workbench_apply_preview_ready"] is True


def test_apply_preview_writer_creates_split_artifacts(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1}, selected_lane_id="duplicates")
    result = write_review_workbench_apply_preview(tmp_path, service, reviewed_decision_plan=_reviewed_plan())

    assert result["written_file_count"] == 3
    assert (tmp_path / "review_workbench_apply_preview.json").exists()
    assert (tmp_path / "review_workbench_reviewed_command_plan_preview.json").exists()
    loaded = json.loads((tmp_path / "review_workbench_apply_preview.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == REVIEW_WORKBENCH_APPLY_PREVIEW_KIND
    assert loaded["capabilities"]["executes_commands"] is False


def test_cli_apply_preview_json_and_out_dir(tmp_path: Path, capsys) -> None:
    reviewed = tmp_path / "reviewed.json"
    reviewed.write_text(json.dumps(_reviewed_plan()), encoding="utf-8")

    assert app_services_main(["review-workbench-apply-preview", "--reviewed-decision-plan-json", str(reviewed), "--selected-lane", "duplicates", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == REVIEW_WORKBENCH_APPLY_PREVIEW_KIND
    assert payload["summary"]["preview_ready"] is True
    assert payload["capabilities"]["executes_commands"] is False

    out_dir = tmp_path / "apply-preview"
    assert app_services_main(["review-workbench-apply-preview", "--reviewed-decision-plan-json", str(reviewed), "--out-dir", str(out_dir)]) == 0
    assert "GUI Review Workbench apply preview" in capsys.readouterr().out
    assert (out_dir / "review_workbench_apply_preview.json").exists()


def test_qt_widget_mount_exposes_apply_preview_model_source() -> None:
    page = build_page_model("review-workbench", {}, query="")
    mount = build_review_workbench_page_widget(_QtWidgets, page)

    assert mount.apply_preview["kind"] == REVIEW_WORKBENCH_APPLY_PREVIEW_KIND
    assert mount.model_sources["apply_preview"]["capabilities"]["executes_commands"] is False
