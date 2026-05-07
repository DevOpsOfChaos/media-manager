from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_review_workbench_apply_executor_contract import (
    REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND,
    build_review_workbench_apply_executor_contract,
    write_review_workbench_apply_executor_contract,
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
        "reviewed_decision_count": 2,
        "command_preview": [["media-manager", "duplicates", "--import-decisions", "decisions.json", "--show-plan"]],
    }


def test_apply_executor_contract_blocks_without_typed_confirmation() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )
    contract = service["apply_executor_contract"]

    assert contract["kind"] == REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND
    assert contract["summary"]["status"] == "awaiting_typed_confirmation"
    assert contract["summary"]["typed_confirmation_matches"] is False
    assert contract["summary"]["apply_enabled"] is False
    assert contract["capabilities"]["executes_commands"] is False
    assert contract["mutation_policy"]["dry_run_only"] is True
    assert contract["dry_run_execution_plan"]["commands"][0]["executable_in_this_contract"] is False


def test_apply_executor_contract_accepts_phrase_but_stays_non_executing() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )
    contract = build_review_workbench_apply_executor_contract(
        service["confirmation_dialog"],
        typed_confirmation="APPLY REVIEWED DECISIONS",
    )

    assert contract["summary"]["status"] == "future_executor_eligible"
    assert contract["summary"]["typed_confirmation_matches"] is True
    assert contract["summary"]["ready_for_future_executor"] is True
    assert contract["summary"]["execution_enabled"] is False
    assert contract["readiness"]["ready"] is True
    assert contract["capabilities"]["executes_commands"] is False
    assert contract["dry_run_execution_plan"]["execution_enabled"] is False


def test_apply_executor_contract_refuses_executor_enabled_probe() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )
    contract = build_review_workbench_apply_executor_contract(
        service["confirmation_dialog"],
        typed_confirmation="APPLY REVIEWED DECISIONS",
        executor_enabled=True,
    )

    assert contract["summary"]["status"] == "execution_refused"
    assert contract["summary"]["execution_enabled"] is False
    assert contract["capabilities"]["executes_commands"] is False
    assert any(item["id"] == "executor-disabled-by-default" and item["satisfied"] is False for item in contract["preflight"]["checks"])


def test_apply_executor_contract_writer_creates_split_artifacts(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
        reviewed_decision_plan=_reviewed_plan(),
    )
    result = write_review_workbench_apply_executor_contract(
        tmp_path,
        service["confirmation_dialog"],
        typed_confirmation="APPLY REVIEWED DECISIONS",
    )

    assert result["written_file_count"] == 5
    assert (tmp_path / "review_workbench_apply_executor_contract.json").exists()
    assert (tmp_path / "review_workbench_apply_executor_preflight.json").exists()
    assert (tmp_path / "review_workbench_apply_executor_audit_plan.json").exists()
    assert (tmp_path / "review_workbench_apply_dry_run_execution_plan.json").exists()
    loaded = json.loads((tmp_path / "review_workbench_apply_executor_contract.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND
    assert loaded["capabilities"]["executes_commands"] is False


def test_cli_apply_executor_contract_json_and_out_dir(tmp_path: Path, capsys) -> None:
    reviewed = tmp_path / "reviewed.json"
    reviewed.write_text(json.dumps(_reviewed_plan()), encoding="utf-8")

    assert app_services_main([
        "review-workbench-apply-executor-contract",
        "--reviewed-decision-plan-json",
        str(reviewed),
        "--selected-lane",
        "duplicates",
        "--typed-confirmation",
        "APPLY REVIEWED DECISIONS",
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND
    assert payload["summary"]["ready_for_future_executor"] is True
    assert payload["summary"]["execution_enabled"] is False

    out_dir = tmp_path / "apply-executor-contract"
    assert app_services_main([
        "review-workbench-apply-executor-contract",
        "--reviewed-decision-plan-json",
        str(reviewed),
        "--typed-confirmation",
        "APPLY REVIEWED DECISIONS",
        "--out-dir",
        str(out_dir),
    ]) == 0
    assert "GUI Review Workbench apply executor contract" in capsys.readouterr().out
    assert (out_dir / "review_workbench_apply_executor_contract.json").exists()


def test_page_and_lazy_qt_mount_expose_apply_executor_contract() -> None:
    page = build_page_model("review-workbench", {}, query="")
    assert page["apply_executor_contract"]["kind"] == REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND

    mount = build_review_workbench_page_widget(_QtWidgets, page)
    assert mount.apply_executor_contract["kind"] == REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND
    assert mount.model_sources["apply_executor_contract"]["capabilities"]["executes_commands"] is False
