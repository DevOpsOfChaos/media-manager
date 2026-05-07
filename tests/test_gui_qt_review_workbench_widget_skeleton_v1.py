from __future__ import annotations

import json
import sys
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_qt_review_workbench_widget_skeleton import (
    QT_REVIEW_WORKBENCH_WIDGET_SKELETON_KIND,
    build_qt_review_workbench_widget_skeleton,
    write_qt_review_workbench_widget_skeleton,
)
from media_manager.core.gui_review_workbench_service import build_gui_review_workbench_service_bundle
from media_manager.core.gui_page_models import build_page_model
from media_manager.gui_review_workbench_qt import build_review_workbench_page_widget
from media_manager.gui_desktop_qt import _render_page_content


class _FakeWidget:
    def __init__(self, *args):
        self.args = args
        self.object_name = ""
        self.properties = {}
        self.children = []
        self.enabled = True
        self.text = ""
        self.items = []

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
        self.items.extend(values)

    def setColumnCount(self, value):
        self.properties["column_count"] = value

    def setRowCount(self, value):
        self.properties["row_count"] = value

    def setHorizontalHeaderLabels(self, values):
        self.properties["headers"] = list(values)

    def setItem(self, row, column, item):
        self.children.append(("item", row, column, item))

    def setAlternatingRowColors(self, value):
        self.properties["alternating"] = bool(value)

    def addAction(self, label):
        action = _FakeWidget(label)
        self.children.append(("action", action))
        return action

    def setContentsMargins(self, *args):
        self.properties["contents_margins"] = args

    def setSpacing(self, value):
        self.properties["spacing"] = value

    def addWidget(self, widget, *args):
        self.children.append(("widget", widget, args))

    def addLayout(self, layout):
        self.children.append(("layout", layout))

    def addStretch(self, value=1):
        self.children.append(("stretch", value))


class _FakeLayout(_FakeWidget):
    pass


class _FakeQtWidgets:
    QWidget = _FakeWidget
    QLabel = _FakeWidget
    QToolBar = _FakeWidget
    QLineEdit = _FakeWidget
    QComboBox = _FakeWidget
    QTableWidget = _FakeWidget
    QTableWidgetItem = _FakeWidget
    QTextEdit = _FakeWidget
    QPushButton = _FakeWidget
    QSplitter = _FakeWidget
    QVBoxLayout = _FakeLayout
    QHBoxLayout = _FakeLayout


def test_widget_skeleton_builds_runtime_mount_contract_without_importing_qt() -> None:
    sys.modules.pop("PySide6", None)
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 2},
        people_review_summary={"group_count": 1, "face_count": 3},
        selected_lane_id="people-review",
    )
    skeleton = build_qt_review_workbench_widget_skeleton(service["qt_widget_binding_plan"])

    assert skeleton["kind"] == QT_REVIEW_WORKBENCH_WIDGET_SKELETON_KIND
    assert skeleton["ready"] is True
    assert skeleton["capabilities"]["requires_pyside6"] is False
    assert skeleton["capabilities"]["loads_pyside6_at_import_time"] is False
    assert skeleton["summary"]["node_count"] == 4
    assert skeleton["summary"]["model_mount_count"] == 4
    assert skeleton["summary"]["route_wire_count"] >= 1
    assert skeleton["builder_contract"]["module"] == "media_manager.gui_review_workbench_qt"
    assert "PySide6" not in sys.modules


def test_review_workbench_service_embeds_widget_skeleton_and_writes_it(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1})

    assert service["capabilities"]["qt_widget_skeleton_ready"] is True
    assert service["qt_widget_skeleton"]["readiness"]["ready"] is True
    assert service["summary"]["qt_widget_skeleton_node_count"] == 4
    assert "review_workbench_qt_widget_skeleton.json" in service["artifact_names"]

    result = write_qt_review_workbench_widget_skeleton(tmp_path / "skeleton", service["qt_widget_binding_plan"])
    assert result["written_file_count"] == 2
    assert (tmp_path / "skeleton" / "review_workbench_qt_widget_skeleton.json").exists()
    loaded = json.loads((tmp_path / "skeleton" / "review_workbench_qt_widget_skeleton.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == QT_REVIEW_WORKBENCH_WIDGET_SKELETON_KIND


def test_cli_review_workbench_widget_skeleton_json_and_out_dir(tmp_path: Path, capsys) -> None:
    assert app_services_main(["review-workbench-widget-skeleton", "--json", "--selected-lane", "duplicates"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == QT_REVIEW_WORKBENCH_WIDGET_SKELETON_KIND
    assert payload["readiness"]["ready"] is True
    assert payload["summary"]["node_count"] == 4

    out_dir = tmp_path / "widget-skeleton"
    assert app_services_main(["review-workbench-widget-skeleton", "--out-dir", str(out_dir)]) == 0
    text = capsys.readouterr().out
    assert "GUI Review Workbench Qt widget skeleton" in text
    assert (out_dir / "review_workbench_qt_widget_skeleton.json").exists()


def test_lazy_review_workbench_qt_builder_consumes_page_model_with_fake_qtwidgets() -> None:
    sys.modules.pop("PySide6", None)
    page = build_page_model("review-workbench", {}, query="duplicate")

    mount = build_review_workbench_page_widget(_FakeQtWidgets, page)

    assert mount.root_widget.object_name == "ReviewWorkbenchPage"
    assert mount.skeleton["ready"] is True
    assert mount.skeleton["summary"]["node_count"] == 4
    assert set(mount.widgets) >= {"root", "toolbar", "filter_bar", "body"}
    assert "PySide6" not in sys.modules


def test_desktop_qt_renderer_uses_review_workbench_builder_with_fake_qtwidgets() -> None:
    sys.modules.pop("PySide6", None)
    page = build_page_model("review-workbench", {})

    rendered = _render_page_content(_FakeQtWidgets, page)

    assert rendered.object_name == ""
    assert "PySide6" not in sys.modules
