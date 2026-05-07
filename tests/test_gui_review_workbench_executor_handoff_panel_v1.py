from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_review_workbench_executor_handoff_panel import (
    REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND,
    build_review_workbench_executor_handoff_panel,
    write_review_workbench_executor_handoff_panel,
)
from media_manager.core.gui_review_workbench_apply_executor_contract import build_review_workbench_apply_executor_contract
from media_manager.core.gui_review_workbench_service import build_gui_review_workbench_service_bundle
from media_manager.core.gui_page_models import build_page_model
from media_manager.core.gui_desktop_runtime_state import build_gui_desktop_runtime_state
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
        "reviewed_decision_count": 2,
        "command_preview": [["media-manager", "duplicates", "--import-decisions", "decisions.json", "--show-plan"]],
    }


def _service() -> dict[str, object]:
    return build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )


def test_executor_handoff_panel_is_display_only_and_renderable() -> None:
    service = _service()
    panel = service["executor_handoff_panel"]

    assert panel["kind"] == REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND
    assert panel["summary"]["status"] == "renderable"
    assert panel["summary"]["section_count"] >= 6
    assert panel["summary"]["dry_run_command_count"] == 1
    assert panel["summary"]["execution_enabled"] is False
    assert panel["capabilities"]["executes_commands"] is False
    assert panel["mutation_policy"]["dry_run_only"] is True
    assert any(section["id"] == "dry-run-plan" for section in panel["sections"])


def test_executor_handoff_panel_reflects_typed_confirmation_contract() -> None:
    service = _service()
    executor = build_review_workbench_apply_executor_contract(
        service["confirmation_dialog"],
        typed_confirmation="APPLY REVIEWED DECISIONS",
    )
    panel = build_review_workbench_executor_handoff_panel(service["confirmation_dialog"], executor)

    assert panel["summary"]["executor_status"] == "future_executor_eligible"
    assert panel["summary"]["typed_confirmation_matches"] is True
    assert panel["summary"]["ready_for_future_executor"] is True
    assert panel["summary"]["execution_enabled"] is False
    assert panel["capabilities"]["executes_commands"] is False


def test_executor_handoff_writer_creates_split_artifacts(tmp_path: Path) -> None:
    service = _service()
    result = write_review_workbench_executor_handoff_panel(
        tmp_path,
        service["confirmation_dialog"],
        service["apply_executor_contract"],
    )

    assert result["written_file_count"] == 6
    assert (tmp_path / "review_workbench_apply_executor_handoff_panel.json").exists()
    assert (tmp_path / "review_workbench_apply_handoff_preflight.json").exists()
    assert (tmp_path / "review_workbench_apply_handoff_dry_run_plan.json").exists()
    loaded = json.loads((tmp_path / "review_workbench_apply_executor_handoff_panel.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND
    assert loaded["capabilities"]["executes_commands"] is False


def test_cli_executor_handoff_json_and_out_dir(tmp_path: Path, capsys) -> None:
    reviewed = tmp_path / "reviewed.json"
    reviewed.write_text(json.dumps(_reviewed_plan()), encoding="utf-8")

    assert app_services_main([
        "review-workbench-apply-handoff-panel",
        "--reviewed-decision-plan-json",
        str(reviewed),
        "--selected-lane",
        "duplicates",
        "--typed-confirmation",
        "APPLY REVIEWED DECISIONS",
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND
    assert payload["summary"]["ready_for_future_executor"] is True
    assert payload["summary"]["execution_enabled"] is False

    out_dir = tmp_path / "apply-handoff-panel"
    assert app_services_main([
        "review-workbench-apply-handoff-panel",
        "--reviewed-decision-plan-json",
        str(reviewed),
        "--typed-confirmation",
        "APPLY REVIEWED DECISIONS",
        "--out-dir",
        str(out_dir),
    ]) == 0
    assert "GUI Review Workbench apply handoff panel" in capsys.readouterr().out
    assert (out_dir / "review_workbench_apply_executor_handoff_panel.json").exists()


def test_page_runtime_and_lazy_qt_mount_expose_handoff_panel() -> None:
    page = build_page_model("review-workbench", {}, query="")
    assert page["executor_handoff_panel"]["kind"] == REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND

    mount = build_review_workbench_page_widget(_QtWidgets, page)
    assert mount.executor_handoff_panel["kind"] == REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND
    assert mount.model_sources["executor_handoff_panel"]["capabilities"]["executes_commands"] is False
    assert mount.widgets["executor_handoff_panel"].properties["executes_commands"] is False
    assert mount.widgets["executor_confirm_apply"].enabled is False


def test_desktop_runtime_writes_executor_handoff_panel(tmp_path: Path) -> None:
    state = build_gui_desktop_runtime_state(active_page_id="review-workbench")
    assert state["summary"]["review_workbench_executor_handoff_panel_status"] == "renderable"
    assert state["review_workbench_service"]["executor_handoff_panel"]["capabilities"]["executes_commands"] is False
