from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_page_models import build_page_model
from media_manager.core.gui_review_workbench_service import build_gui_review_workbench_service_bundle, write_gui_review_workbench_service_bundle
from media_manager.core.gui_review_workbench_stateful_callbacks import (
    REVIEW_WORKBENCH_STATEFUL_CALLBACK_PLAN_KIND,
    REVIEW_WORKBENCH_STATEFUL_CALLBACK_RESPONSE_KIND,
    build_review_workbench_stateful_callback_plan,
    build_review_workbench_stateful_callback_response,
    map_review_workbench_callback_intent_to_rebuild_intent,
    write_review_workbench_stateful_callback_plan,
)
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


def test_stateful_callback_plan_maps_qt_callbacks_to_rebuild_actions() -> None:
    service = build_gui_review_workbench_service_bundle(selected_lane_id="duplicates")

    plan = build_review_workbench_stateful_callback_plan(service)

    assert plan["kind"] == REVIEW_WORKBENCH_STATEFUL_CALLBACK_PLAN_KIND
    assert plan["readiness"]["ready"] is True
    assert plan["capabilities"]["executes_commands"] is False
    assert plan["summary"]["page_rebuild_callback_count"] == 6
    mapping = {row["intent_kind"]: row["rebuild_action"] for row in plan["callback_rebuild_bindings"]}
    assert mapping["filter_query_changed"] == "set_query"
    assert mapping["filter_status_changed"] == "set_filter"
    assert mapping["sort_mode_changed"] == "set_sort"
    assert mapping["lane_selected"] == "select_lane"
    assert mapping["toolbar_refresh"] == "refresh_view"
    assert mapping["toolbar_apply_reviewed_decisions"] == "disabled_apply"


def test_stateful_callback_response_rebuilds_next_page_state() -> None:
    service = build_gui_review_workbench_service_bundle(selected_lane_id="duplicates")
    callback_intent = {"intent_kind": "filter_query_changed", "query": "people", "executes_commands": False}

    response = build_review_workbench_stateful_callback_response(service, callback_intent)

    assert response["kind"] == REVIEW_WORKBENCH_STATEFUL_CALLBACK_RESPONSE_KIND
    assert response["readiness"]["ready"] is True
    assert response["capabilities"]["executes_commands"] is False
    assert response["normalized_rebuild_intent"]["action"] == "set_query"
    assert response["summary"]["selected_lane_id"] == "people-review"
    assert response["summary"]["table_row_count"] == 1
    assert response["next_page_state"]["view_model"]["selected_lane_id"] == "people-review"


def test_callback_intent_mapper_keeps_route_and_disabled_apply_non_executing() -> None:
    route = map_review_workbench_callback_intent_to_rebuild_intent({"intent_kind": "toolbar_open_selected_lane", "lane_id": "people-review"})
    disabled = map_review_workbench_callback_intent_to_rebuild_intent({"intent_kind": "toolbar_apply_reviewed_decisions"})

    assert route["action"] == "open_selected_lane"
    assert disabled["action"] == "disabled_apply"
    assert route["executes_commands"] is False
    assert disabled["executes_commands"] is False


def test_service_embeds_stateful_callback_plan_and_writes_it(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle()

    assert service["capabilities"]["review_workbench_stateful_callback_plan_ready"] is True
    assert service["stateful_callback_plan"]["readiness"]["ready"] is True
    assert service["summary"]["stateful_callback_page_rebuild_count"] == 6
    assert "review_workbench_stateful_callback_plan.json" in service["artifact_names"]

    plan = write_review_workbench_stateful_callback_plan(tmp_path / "callbacks", service)
    assert plan["written_file_count"] == 3
    assert (tmp_path / "callbacks" / "review_workbench_stateful_callback_plan.json").exists()

    bundle = write_gui_review_workbench_service_bundle(tmp_path / "service")
    assert (tmp_path / "service" / "review_workbench_stateful_callback_plan.json").exists()
    assert bundle["written_file_count"] >= 18


def test_cli_stateful_callbacks_plan_and_response(tmp_path: Path, capsys) -> None:
    assert app_services_main(["review-workbench-stateful-callbacks", "--json"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["kind"] == REVIEW_WORKBENCH_STATEFUL_CALLBACK_PLAN_KIND
    assert plan["summary"]["page_rebuild_callback_count"] == 6

    assert app_services_main([
        "review-workbench-stateful-callbacks",
        "--callback-kind",
        "filter_query_changed",
        "--callback-query",
        "people",
        "--json",
    ]) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["kind"] == REVIEW_WORKBENCH_STATEFUL_CALLBACK_RESPONSE_KIND
    assert response["summary"]["selected_lane_id"] == "people-review"

    out_dir = tmp_path / "stateful-callbacks"
    assert app_services_main([
        "review-workbench-stateful-callbacks",
        "--callback-kind",
        "filter_query_changed",
        "--callback-query",
        "people",
        "--out-dir",
        str(out_dir),
    ]) == 0
    assert (out_dir / "review_workbench_stateful_callback_response.json").exists()
    assert (out_dir / "review_workbench_stateful_callback_next_page_state.json").exists()


def test_lazy_qt_callbacks_can_request_stateful_rebuilds_without_pyside6() -> None:
    sys.modules.pop("PySide6", None)
    intents: list[dict[str, Any]] = []
    rebuilds: list[dict[str, Any]] = []
    page = build_page_model("review-workbench", {}, query="")

    mount = build_review_workbench_page_widget(
        _QtWidgets,
        page,
        intent_dispatcher=intents.append,
        stateful_rebuild_handler=rebuilds.append,
    )

    assert mount.stateful_callback_plan["readiness"]["ready"] is True
    assert mount.root_widget.properties["stateful_callback_plan_ready"] is True
    mount.widgets["query"].textChanged.emit("people")
    mount.widgets["lane_table"].setCurrentRow(0)
    mount.widgets["lane_table"].itemSelectionChanged.emit()

    assert [item["intent_kind"] for item in intents[:2]] == ["filter_query_changed", "lane_selected"]
    assert len(rebuilds) == 2
    assert rebuilds[0]["kind"] == REVIEW_WORKBENCH_STATEFUL_CALLBACK_RESPONSE_KIND
    assert rebuilds[0]["summary"]["rebuild_action"] == "set_query"
    assert rebuilds[0]["summary"]["selected_lane_id"] == "people-review"
    assert rebuilds[1]["summary"]["rebuild_action"] == "select_lane"
    assert all(item["capabilities"]["executes_commands"] is False for item in rebuilds)
    assert "PySide6" not in sys.modules
