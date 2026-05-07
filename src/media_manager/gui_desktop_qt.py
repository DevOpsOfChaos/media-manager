from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .core.gui_page_models import build_page_model
from .core.gui_qt_desktop_integration_plan import build_qt_desktop_integration_plan, summarize_qt_desktop_integration_plan
from .core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from .core.gui_qt_runtime_smoke_artifact_verifier import (
    summarize_qt_runtime_smoke_local_artifact_pack_verification,
    verify_qt_runtime_smoke_local_artifact_pack_dir,
    write_qt_runtime_smoke_local_artifact_pack_verification_report,
)
from .core.gui_qt_runtime_smoke_guarded_summary import summarize_guarded_qt_runtime_smoke_integration
from .core.gui_qt_runtime_smoke_local_artifact_pack import (
    build_qt_runtime_smoke_local_artifact_pack,
    summarize_qt_runtime_smoke_local_artifact_pack,
    write_qt_runtime_smoke_local_artifact_pack,
)
from .core.gui_qt_runtime_smoke_shell_model_adapter import apply_guarded_qt_runtime_smoke_to_shell_model
from .core.gui_theme import build_qt_stylesheet
from .gui_review_workbench_qt import build_review_workbench_page_widget
from .gui_similar_comparison_qt import build_similar_comparison_page_widget


class MissingQtDependencyError(RuntimeError):
    """Raised when the optional PySide6 GUI backend is not installed."""


def qt_install_guidance() -> str:
    return (
        "PySide6 is required for the modern desktop GUI.\n"
        "Install it with:\n"
        "  python -m pip install -e .[gui]\n"
        "Then run:\n"
        "  media-manager-gui"
    )


def load_qt_modules():
    try:  # pragma: no cover - depends on optional GUI dependency
        from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise MissingQtDependencyError(str(exc)) from exc
    return QtCore, QtGui, QtWidgets


def shell_model_to_pretty_json(model: Mapping[str, Any]) -> str:
    return json.dumps(dict(model), indent=2, ensure_ascii=False)


def build_qt_desktop_plan(model: Mapping[str, Any]) -> dict[str, object]:
    """Build the headless desktop integration plan used by the Qt runtime."""

    return build_qt_desktop_integration_plan(model)


def qt_desktop_plan_to_pretty_json(model: Mapping[str, Any]) -> str:
    return json.dumps(build_qt_desktop_plan(model), indent=2, ensure_ascii=False)


def summarize_qt_desktop_plan(model: Mapping[str, Any]) -> str:
    return summarize_qt_desktop_integration_plan(build_qt_desktop_plan(model))


def build_guarded_qt_runtime_smoke_plan(
    model: Mapping[str, Any],
    *,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    history_entries: list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
) -> dict[str, object]:
    """Build the guarded Runtime Smoke integration plan without opening Qt."""

    return build_guarded_qt_runtime_smoke_integration(
        model,
        results=results,
        history_entries=history_entries,
        reviewer=reviewer,
    )


def guarded_qt_runtime_smoke_plan_to_pretty_json(
    model: Mapping[str, Any],
    *,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
) -> str:
    return json.dumps(
        build_guarded_qt_runtime_smoke_plan(model, results=results, reviewer=reviewer),
        indent=2,
        ensure_ascii=False,
    )


def summarize_guarded_qt_runtime_smoke_plan(
    model: Mapping[str, Any],
    *,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
) -> str:
    return summarize_guarded_qt_runtime_smoke_integration(
        build_guarded_qt_runtime_smoke_plan(model, results=results, reviewer=reviewer)
    )


def attach_guarded_qt_runtime_smoke_to_shell_model(
    model: Mapping[str, Any],
    *,
    activate: bool = False,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
) -> dict[str, object]:
    integration = build_guarded_qt_runtime_smoke_plan(model, results=results, reviewer=reviewer)
    return apply_guarded_qt_runtime_smoke_to_shell_model(model, integration, activate=activate)


def build_guarded_qt_runtime_smoke_local_artifact_pack(
    model: Mapping[str, Any],
    *,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
    result_payload_report: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    plan = build_guarded_qt_runtime_smoke_plan(model, results=results, reviewer=reviewer)
    return build_qt_runtime_smoke_local_artifact_pack(plan, result_payload_report=result_payload_report)


def summarize_guarded_qt_runtime_smoke_local_artifact_pack(
    model: Mapping[str, Any],
    *,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
    result_payload_report: Mapping[str, Any] | None = None,
) -> str:
    return summarize_qt_runtime_smoke_local_artifact_pack(
        build_guarded_qt_runtime_smoke_local_artifact_pack(
            model,
            results=results,
            reviewer=reviewer,
            result_payload_report=result_payload_report,
        )
    )


def write_guarded_qt_runtime_smoke_local_artifact_pack(
    model: Mapping[str, Any],
    output_dir: str,
    *,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
    result_payload_report: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    plan = build_guarded_qt_runtime_smoke_plan(model, results=results, reviewer=reviewer)
    return write_qt_runtime_smoke_local_artifact_pack(
        plan,
        output_dir,
        result_payload_report=result_payload_report,
    )


def verify_guarded_qt_runtime_smoke_local_artifact_pack(output_dir: str) -> dict[str, object]:
    """Verify a local Runtime Smoke artifact pack without importing Qt."""

    return verify_qt_runtime_smoke_local_artifact_pack_dir(output_dir)


def summarize_guarded_qt_runtime_smoke_local_artifact_pack_verification(output_dir: str) -> str:
    """Summarize local Runtime Smoke artifact-pack verification."""

    return summarize_qt_runtime_smoke_local_artifact_pack_verification(
        verify_guarded_qt_runtime_smoke_local_artifact_pack(output_dir)
    )


def write_guarded_qt_runtime_smoke_local_artifact_pack_verification_report(
    output_dir: str,
    *,
    report_dir: str | None = None,
) -> dict[str, object]:
    """Write local verification proof files for a Runtime Smoke artifact pack."""

    return write_qt_runtime_smoke_local_artifact_pack_verification_report(
        output_dir,
        output_dir=report_dir,
    )


def _text(value: object, fallback: str = "") -> str:
    return str(value) if value is not None else fallback


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _metric_text(metrics: Mapping[str, Any]) -> str:
    return "   ".join(f"{key}: {value}" for key, value in metrics.items())


def _add_label(layout, QtWidgets, text: str, *, object_name: str | None = None, word_wrap: bool = True):
    label = QtWidgets.QLabel(text)
    if object_name:
        label.setObjectName(object_name)
    label.setWordWrap(word_wrap)
    layout.addWidget(label)
    return label


def _build_metric_card(QtWidgets, title: str, subtitle: str, metrics: Mapping[str, Any], *, actions: list[Any] | None = None):
    card = QtWidgets.QFrame()
    card.setObjectName("Card")
    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(8)
    _add_label(layout, QtWidgets, title, object_name="CardTitle")
    if subtitle:
        _add_label(layout, QtWidgets, subtitle, object_name="Muted")
    if metrics:
        _add_label(layout, QtWidgets, _metric_text(metrics), object_name="MetricText")
    if actions:
        row = QtWidgets.QHBoxLayout()
        for raw in actions[:2]:
            action = _mapping(raw)
            button = QtWidgets.QPushButton(_text(action.get("label"), "Open"))
            button.setProperty("secondary", True)
            row.addWidget(button)
        row.addStretch(1)
        layout.addLayout(row)
    return card


def _build_section_frame(QtWidgets, title: str, subtitle: str = ""):
    frame = QtWidgets.QFrame()
    frame.setObjectName("Section")
    layout = QtWidgets.QVBoxLayout(frame)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)
    _add_label(layout, QtWidgets, title, object_name="SectionTitle")
    if subtitle:
        _add_label(layout, QtWidgets, subtitle, object_name="Muted")
    return frame, layout


def _render_dashboard(QtWidgets, layout, page: Mapping[str, Any]):
    hero = _mapping(page.get("hero"))
    frame, hero_layout = _build_section_frame(QtWidgets, _text(hero.get("title"), _text(page.get("title"))), _text(hero.get("subtitle"), _text(page.get("description"))))
    metrics = _mapping(hero.get("metrics"))
    if metrics:
        _add_label(hero_layout, QtWidgets, _metric_text(metrics), object_name="MetricText")
    layout.addWidget(frame)
    grid = QtWidgets.QGridLayout()
    grid.setSpacing(16)
    for index, raw_card in enumerate(_list(page.get("cards"))):
        card = _mapping(raw_card)
        grid.addWidget(
            _build_metric_card(QtWidgets, _text(card.get("title")), _text(card.get("subtitle")), _mapping(card.get("metrics")), actions=_list(card.get("actions"))),
            index // 3,
            index % 3,
        )
    layout.addLayout(grid)


def _render_people_review(QtWidgets, layout, page: Mapping[str, Any]):
    overview = _mapping(page.get("overview"))
    top, top_layout = _build_section_frame(QtWidgets, _text(page.get("title")), _text(page.get("description")))
    _add_label(top_layout, QtWidgets, _metric_text(overview), object_name="MetricText")
    layout.addWidget(top)
    body = QtWidgets.QHBoxLayout()
    groups_frame, groups_layout = _build_section_frame(QtWidgets, "Groups", _text(page.get("query")))
    groups_frame.setMinimumWidth(360)
    for raw_group in _list(page.get("groups"))[:50]:
        group = _mapping(raw_group)
        button = QtWidgets.QPushButton(f"{_text(group.get('display_label') or group.get('group_id'))}\n{group.get('status')} · faces={group.get('face_count', 0)}")
        button.setProperty("groupButton", True)
        groups_layout.addWidget(button)
    if not _list(page.get("groups")):
        empty = _mapping(page.get("empty_state"))
        _add_label(groups_layout, QtWidgets, _text(empty.get("title"), "No people review bundle."), object_name="Muted")
    detail = _mapping(page.get("detail"))
    detail_frame, detail_layout = _build_section_frame(QtWidgets, _text(detail.get("title"), "Selection"), _text(detail.get("subtitle"), "Choose a group to inspect faces."))
    for raw_face in _list(detail.get("faces"))[:24]:
        face = _mapping(raw_face)
        detail_layout.addWidget(_build_metric_card(QtWidgets, _text(face.get("face_id")), _text(face.get("path")), {"status": face.get("decision_status", "pending")}))
    body.addWidget(groups_frame, 1)
    body.addWidget(detail_frame, 2)
    layout.addLayout(body)


def _render_table(QtWidgets, layout, page: Mapping[str, Any]):
    columns = [str(item) for item in _list(page.get("columns"))]
    rows = [_mapping(row) for row in _list(page.get("rows"))]
    if not rows:
        empty = _mapping(page.get("empty_state"))
        _add_label(layout, QtWidgets, _text(empty.get("title"), "No rows"), object_name="Muted")
        _add_label(layout, QtWidgets, _text(empty.get("description")), object_name="Muted")
        return
    table = QtWidgets.QTableWidget(len(rows), len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    for row_index, row in enumerate(rows):
        for col_index, col_name in enumerate(columns):
            value = row.get(col_name)
            if isinstance(value, Mapping):
                value = value.get("value") or value.get("path") or value.get("exists")
            table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(_text(value)))
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setVisible(False)
    layout.addWidget(table)


def _render_new_run(QtWidgets, layout, page: Mapping[str, Any]):
    wizard = _mapping(page.get("wizard"))
    frame, frame_layout = _build_section_frame(QtWidgets, "Guided workflow", "Preview first, review second, apply only after confirmation.")
    for raw_step in _list(wizard.get("steps")):
        step = _mapping(raw_step)
        marker = "✓" if step.get("complete") else "•"
        _add_label(frame_layout, QtWidgets, f"{marker} {_text(step.get('title'))}", object_name="MetricText")
    layout.addWidget(frame)


def _render_settings(QtWidgets, layout, page: Mapping[str, Any]):
    for raw_section in _list(page.get("sections")):
        section = _mapping(raw_section)
        frame, section_layout = _build_section_frame(QtWidgets, _text(section.get("title")))
        for raw_item in _list(section.get("items")):
            item = _mapping(raw_item)
            _add_label(section_layout, QtWidgets, f"{item.get('label')}: {item.get('value')}", object_name="MetricText")
        layout.addWidget(frame)


def _render_runtime_smoke(QtWidgets, layout, page: Mapping[str, Any]):
    presenter = _mapping(page.get("presenter"))
    metrics = _mapping(presenter.get("metrics"))
    status_frame, status_layout = _build_section_frame(
        QtWidgets,
        _text(page.get("title"), "Runtime Smoke"),
        _text(page.get("subtitle") or presenter.get("subtitle"), "Review guarded Qt runtime readiness."),
    )
    _add_label(
        status_layout,
        QtWidgets,
        _metric_text(
            {
                "status": presenter.get("status"),
                "severity": presenter.get("severity"),
                "ready": metrics.get("ready_for_runtime_review"),
                "requires_confirmation": metrics.get("requires_user_confirmation"),
            }
        ),
        object_name="MetricText",
    )
    layout.addWidget(status_frame)

    table = _mapping(page.get("table"))
    rows = [row for row in _list(table.get("rows")) if isinstance(row, Mapping)]
    table_frame, table_layout = _build_section_frame(QtWidgets, "Runtime Smoke checks", "Metadata-only checks; no command executes from this page.")
    if rows:
        widget = QtWidgets.QTableWidget(len(rows), 4)
        widget.setHorizontalHeaderLabels(["Area", "Status", "Problems", "Ready"])
        widget.setAlternatingRowColors(True)
        widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        for row_index, row in enumerate(rows):
            values = [
                row.get("label") or row.get("id"),
                row.get("status") or row.get("state"),
                row.get("problem_count", 0),
                row.get("ready"),
            ]
            for col_index, value in enumerate(values):
                widget.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(_text(value)))
        widget.horizontalHeader().setStretchLastSection(True)
        widget.verticalHeader().setVisible(False)
        table_layout.addWidget(widget)
    else:
        _add_label(table_layout, QtWidgets, "No runtime smoke rows available yet.", object_name="Muted")
    layout.addWidget(table_frame)

    detail = _mapping(page.get("detail"))
    detail_frame, detail_layout = _build_section_frame(QtWidgets, "Guardrails", _text(detail.get("recommended_next_step")))
    privacy = _mapping(detail.get("privacy"))
    _add_label(
        detail_layout,
        QtWidgets,
        _metric_text(
            {
                "local_only": privacy.get("local_only", True),
                "network_required": privacy.get("network_required", False),
                "opens_window": False,
                "executes_commands": False,
            }
        ),
        object_name="MetricText",
    )
    layout.addWidget(detail_frame)

    actions = [action for action in _list(page.get("actions")) if isinstance(action, Mapping)]
    if actions:
        actions_frame, actions_layout = _build_section_frame(QtWidgets, "Deferred actions", "Buttons describe guarded intents only.")
        row = QtWidgets.QHBoxLayout()
        for raw_action in actions[:4]:
            action = _mapping(raw_action)
            label = _text(action.get("label"), _text(action.get("id"), "Action"))
            if action.get("requires_confirmation"):
                label = f"{label}…"
            button = QtWidgets.QPushButton(label)
            button.setEnabled(bool(action.get("enabled", True)))
            button.setProperty("secondary", True)
            row.addWidget(button)
        row.addStretch(1)
        actions_layout.addLayout(row)
        layout.addWidget(actions_frame)


def _render_page_content(QtWidgets, page: Mapping[str, Any]):
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(30, 28, 30, 28)
    layout.setSpacing(18)
    _add_label(layout, QtWidgets, _text(page.get("title"), "Media Manager"), object_name="PageTitle")
    if page.get("description"):
        _add_label(layout, QtWidgets, _text(page.get("description")), object_name="Muted")

    kind = page.get("kind")
    if kind == "dashboard_page":
        _render_dashboard(QtWidgets, layout, page)
    elif kind == "people_review_page":
        _render_people_review(QtWidgets, layout, page)
    elif kind in {"table_page", "profiles_page"}:
        _render_table(QtWidgets, layout, page)
    elif kind == "new_run_page":
        _render_new_run(QtWidgets, layout, page)
    elif kind == "settings_page":
        _render_settings(QtWidgets, layout, page)
    elif kind == "qt_runtime_smoke_page_model":
        _render_runtime_smoke(QtWidgets, layout, page)
    elif kind == "review_workbench_page":
        mount = build_review_workbench_page_widget(QtWidgets, page)
        layout.addWidget(mount.root_widget, 1)
    elif kind == "similar_comparison_page":
        mount = build_similar_comparison_page_widget(QtWidgets, page)
        layout.addWidget(mount.root_widget, 1)
    else:
        empty = _mapping(page.get("empty_state"))
        _add_label(layout, QtWidgets, _text(empty.get("title"), "This view is ready for the next GUI iteration."), object_name="Muted")
        _add_label(layout, QtWidgets, _text(empty.get("description")), object_name="Muted")
    layout.addStretch(1)
    return container


def _rebuild_page(model: Mapping[str, Any], page_id: str) -> dict[str, Any]:
    if page_id == "runtime-smoke":
        return dict(attach_guarded_qt_runtime_smoke_to_shell_model(model, activate=True))
    home_state = _mapping(model.get("home_state"))
    language = _text(model.get("language"), "en")
    density = _text(_mapping(model.get("layout")).get("density"), "comfortable")
    page = build_page_model(page_id, home_state, language=language, density=density)
    payload = dict(model)
    payload["active_page_id"] = page_id
    payload["page"] = page
    nav = []
    for raw in _list(model.get("navigation")):
        item = dict(_mapping(raw))
        item["active"] = item.get("id") == page_id
        nav.append(item)
    payload["navigation"] = nav
    return payload


def run_qt_gui(model: Mapping[str, Any]) -> int:  # pragma: no cover - GUI runtime
    QtCore, QtGui, QtWidgets = load_qt_modules()
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    theme = _mapping(model.get("theme"))
    app.setStyleSheet(build_qt_stylesheet(str(theme.get("theme") or "modern-dark")))

    activate_runtime_smoke = _text(model.get("active_page_id")) == "runtime-smoke"
    current_model: dict[str, Any] = dict(attach_guarded_qt_runtime_smoke_to_shell_model(model, activate=activate_runtime_smoke))
    window = QtWidgets.QMainWindow()
    win = _mapping(current_model.get("window"))
    window.setWindowTitle(_text(win.get("title"), "Media Manager"))
    window.resize(int(win.get("width", 1440)), int(win.get("height", 940)))
    window.setMinimumSize(int(win.get("minimum_width", 1180)), int(win.get("minimum_height", 760)))
    central = QtWidgets.QWidget()
    root = QtWidgets.QHBoxLayout(central)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    sidebar = QtWidgets.QFrame()
    sidebar.setObjectName("Sidebar")
    sidebar.setFixedWidth(280)
    side_layout = QtWidgets.QVBoxLayout(sidebar)
    side_layout.setContentsMargins(20, 26, 20, 20)
    side_layout.setSpacing(12)
    app_info = _mapping(current_model.get("application"))
    _add_label(side_layout, QtWidgets, _text(app_info.get("title"), "Media Manager"), object_name="AppTitle")
    _add_label(side_layout, QtWidgets, _text(app_info.get("subtitle")), object_name="Muted")

    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)

    buttons: dict[str, Any] = {}

    def switch_page(page_id: str) -> None:
        nonlocal current_model
        current_model = _rebuild_page(current_model, page_id)
        for nav_id, button in buttons.items():
            button.setChecked(nav_id == page_id)
        scroll.setWidget(_render_page_content(QtWidgets, _mapping(current_model.get("page"))))
        status = _mapping(current_model.get("status_bar"))
        window.statusBar().showMessage(_text(status.get("text"), "Ready."))

    for item in _list(current_model.get("navigation")):
        nav = _mapping(item)
        nav_id = _text(nav.get("id"))
        button = QtWidgets.QPushButton(_text(nav.get("label")))
        button.setCheckable(True)
        button.setChecked(bool(nav.get("active")))
        button.setEnabled(bool(nav.get("enabled", True)))
        button.clicked.connect(lambda checked=False, page_id=nav_id: switch_page(page_id))
        buttons[nav_id] = button
        side_layout.addWidget(button)
    side_layout.addSpacing(16)
    palette_label = QtWidgets.QLabel("Ctrl+K · Command palette")
    palette_label.setObjectName("Muted")
    side_layout.addWidget(palette_label)
    side_layout.addStretch(1)

    scroll.setWidget(_render_page_content(QtWidgets, _mapping(current_model.get("page"))))
    root.addWidget(sidebar)
    root.addWidget(scroll, 1)
    window.setCentralWidget(central)
    status = _mapping(current_model.get("status_bar"))
    window.statusBar().showMessage(_text(status.get("text"), "Ready."))
    window.show()
    return int(app.exec())


__all__ = [
    "MissingQtDependencyError",
    "attach_guarded_qt_runtime_smoke_to_shell_model",
    "build_guarded_qt_runtime_smoke_plan",
    "build_qt_desktop_plan",
    "guarded_qt_runtime_smoke_plan_to_pretty_json",
    "load_qt_modules",
    "qt_desktop_plan_to_pretty_json",
    "qt_install_guidance",
    "run_qt_gui",
    "shell_model_to_pretty_json",
    "summarize_guarded_qt_runtime_smoke_plan",
    "summarize_qt_desktop_plan",
]
