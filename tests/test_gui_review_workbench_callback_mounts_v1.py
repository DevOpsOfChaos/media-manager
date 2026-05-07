from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_review_workbench_callback_mounts import (
    REVIEW_WORKBENCH_CALLBACK_MOUNT_KIND,
    build_review_workbench_callback_mount_plan,
    write_review_workbench_callback_mount_plan,
)
from media_manager.core.gui_review_workbench_service import build_gui_review_workbench_service_bundle
from media_manager.core.gui_page_models import build_page_model
from media_manager.gui_review_workbench_qt import build_review_workbench_page_widget


class _Signal:
    def __init__(self) -> None:
        self.callbacks: list[Any] = []

    def connect(self, callback: Any) -> None:
        self.callbacks.append(callback)

    def emit(self, *args: Any) -> None:
        for callback in list(self.callbacks):
            callback(*args)


class _Widget:
    def __init__(self, *args: Any) -> None:
        self.args = args
        self.object_name = ""
        self.properties: dict[str, Any] = {}
        self.children: list[Any] = []
        self.enabled = True
        self.text = ""
        self.items: list[str] = []
        self._current_row = 0
        self.triggered = _Signal()
        self.textChanged = _Signal()
        self.currentTextChanged = _Signal()
        self.itemSelectionChanged = _Signal()
        self.cellDoubleClicked = _Signal()
        self.clicked = _Signal()

    def setObjectName(self, name: str) -> None:
        self.object_name = name

    def setProperty(self, key: str, value: Any) -> None:
        self.properties[key] = value

    def setEnabled(self, value: Any) -> None:
        self.enabled = bool(value)

    def setWordWrap(self, value: Any) -> None:
        self.properties["word_wrap"] = bool(value)

    def setPlaceholderText(self, value: str) -> None:
        self.properties["placeholder"] = value

    def setText(self, value: str) -> None:
        self.text = value

    def setPlainText(self, value: str) -> None:
        self.text = value

    def setReadOnly(self, value: Any) -> None:
        self.properties["read_only"] = bool(value)

    def addItems(self, values: list[str]) -> None:
        self.items.extend(values)

    def setColumnCount(self, value: int) -> None:
        self.properties["column_count"] = value

    def setRowCount(self, value: int) -> None:
        self.properties["row_count"] = value

    def setHorizontalHeaderLabels(self, values: list[str]) -> None:
        self.properties["headers"] = list(values)

    def setItem(self, row: int, column: int, item: Any) -> None:
        self.children.append(("item", row, column, item))

    def setAlternatingRowColors(self, value: Any) -> None:
        self.properties["alternating"] = bool(value)

    def addAction(self, label: str) -> "_Widget":
        action = _Widget(label)
        self.children.append(("action", action))
        return action

    def setContentsMargins(self, *args: Any) -> None:
        self.properties["contents_margins"] = args

    def setSpacing(self, value: int) -> None:
        self.properties["spacing"] = value

    def addWidget(self, widget: Any, *args: Any) -> None:
        self.children.append(("widget", widget, args))

    def addLayout(self, layout: Any) -> None:
        self.children.append(("layout", layout))

    def addStretch(self, value: int = 1) -> None:
        self.children.append(("stretch", value))

    def currentRow(self) -> int:
        return self._current_row

    def setCurrentRow(self, row: int) -> None:
        self._current_row = row


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


def test_callback_mount_plan_describes_filter_table_toolbar_callbacks() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 2},
        people_review_summary={"group_count": 1, "face_count": 2},
        selected_lane_id="duplicates",
    )

    plan = build_review_workbench_callback_mount_plan(service)

    assert plan["kind"] == REVIEW_WORKBENCH_CALLBACK_MOUNT_KIND
    assert plan["ready"] is True
    assert plan["capabilities"]["executes_commands"] is False
    assert plan["summary"]["widget_callback_mount_count"] == 6
    assert plan["summary"]["toolbar_callback_mount_count"] == 4
    assert plan["summary"]["callback_mount_count"] == 10
    kinds = {mount["intent_kind"] for mount in plan["callback_mounts"]}
    assert {
        "filter_query_changed",
        "filter_status_changed",
        "sort_mode_changed",
        "lane_selected",
        "table_row_activated",
        "toolbar_open_selected_lane",
        "toolbar_apply_reviewed_decisions",
    } <= kinds
    apply_mount = next(mount for mount in plan["toolbar_callback_mounts"] if mount["intent_kind"] == "toolbar_apply_reviewed_decisions")
    assert apply_mount["enabled"] is False
    assert apply_mount["requires_explicit_user_confirmation"] is True
    assert apply_mount["executes_commands"] is False


def test_service_embeds_callback_mount_plan_and_writes_it(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1})

    assert service["capabilities"]["qt_callback_mount_plan_ready"] is True
    assert service["callback_mount_plan"]["readiness"]["ready"] is True
    assert service["summary"]["callback_mount_count"] == 10
    assert "review_workbench_callback_mount_plan.json" in service["artifact_names"]

    result = write_review_workbench_callback_mount_plan(tmp_path / "callbacks", service)
    assert result["written_file_count"] == 2
    assert (tmp_path / "callbacks" / "review_workbench_callback_mount_plan.json").exists()
    loaded = json.loads((tmp_path / "callbacks" / "review_workbench_callback_mount_plan.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == REVIEW_WORKBENCH_CALLBACK_MOUNT_KIND


def test_cli_callback_mounts_json_and_out_dir(tmp_path: Path, capsys) -> None:
    assert app_services_main(["review-workbench-callback-mounts", "--json", "--selected-lane", "duplicates"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == REVIEW_WORKBENCH_CALLBACK_MOUNT_KIND
    assert payload["readiness"]["ready"] is True
    assert payload["summary"]["callback_mount_count"] == 10

    out_dir = tmp_path / "callback-mounts"
    assert app_services_main(["review-workbench-callback-mounts", "--out-dir", str(out_dir)]) == 0
    text = capsys.readouterr().out
    assert "GUI Review Workbench callback mounts" in text
    assert (out_dir / "review_workbench_callback_mount_plan.json").exists()


def test_lazy_qt_builder_dispatches_filter_table_detail_and_toolbar_intents() -> None:
    sys.modules.pop("PySide6", None)
    captured: list[dict[str, Any]] = []
    page = build_page_model("review-workbench", {}, query="")

    mount = build_review_workbench_page_widget(_QtWidgets, page, intent_dispatcher=captured.append)

    assert mount.callback_mount_plan["readiness"]["ready"] is True
    assert mount.callback_mount_plan["summary"]["callback_mount_count"] == 10
    assert mount.widgets["query"].textChanged.callbacks
    assert mount.widgets["status_filter"].currentTextChanged.callbacks
    assert mount.widgets["sort_mode"].currentTextChanged.callbacks
    assert mount.widgets["lane_table"].itemSelectionChanged.callbacks
    assert mount.widgets["lane_table"].cellDoubleClicked.callbacks

    mount.widgets["query"].textChanged.emit("people")
    mount.widgets["status_filter"].currentTextChanged.emit("needs_review")
    mount.widgets["sort_mode"].currentTextChanged.emit("title")
    mount.widgets["lane_table"].setCurrentRow(0)
    mount.widgets["lane_table"].itemSelectionChanged.emit()
    mount.widgets["lane_table"].cellDoubleClicked.emit(0, 0)
    mount.actions["refresh-review-workbench"].triggered.emit()

    assert [item["intent_kind"] for item in captured[:3]] == [
        "filter_query_changed",
        "filter_status_changed",
        "sort_mode_changed",
    ]
    assert captured[0]["query"] == "people"
    assert captured[1]["status"] == "needs_review"
    assert captured[2]["sort_mode"] == "title"
    assert captured[3]["intent_kind"] == "lane_selected"
    assert captured[3]["lane_id"]
    assert captured[4]["intent_kind"] == "table_row_activated"
    assert captured[5]["intent_kind"] == "toolbar_refresh"
    assert all(item["executes_commands"] is False for item in captured)
    assert "PySide6" not in sys.modules
