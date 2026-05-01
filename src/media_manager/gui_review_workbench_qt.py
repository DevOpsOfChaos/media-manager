from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .core.gui_qt_review_workbench_widget_skeleton import build_qt_review_workbench_widget_skeleton
from .core.gui_review_workbench_interactions import build_review_workbench_interaction_intent


@dataclass(frozen=True, slots=True)
class ReviewWorkbenchQtWidgetMount:
    """Runtime mount returned by the lazy Review Workbench Qt builder."""

    root_widget: Any
    skeleton: Mapping[str, Any]
    widgets: Mapping[str, Any]
    actions: Mapping[str, Any]
    model_sources: Mapping[str, Any]
    interaction_plan: Mapping[str, Any]
    callback_mount_plan: Mapping[str, Any]
    apply_preview: Mapping[str, Any]
    confirmation_dialog: Mapping[str, Any]
    apply_executor_contract: Mapping[str, Any]
    executor_handoff_panel: Mapping[str, Any]
    stateful_rebuild_loop: Mapping[str, Any]
    stateful_callback_plan: Mapping[str, Any]
    callback_mounts: Mapping[str, Any]


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _set_object_name(widget: Any, name: str) -> None:
    setter = getattr(widget, "setObjectName", None)
    if callable(setter):
        setter(name)


def _set_property(widget: Any, key: str, value: object) -> None:
    setter = getattr(widget, "setProperty", None)
    if callable(setter):
        setter(key, value)


def _current_row(widget: Any) -> int | None:
    getter = getattr(widget, "currentRow", None)
    if callable(getter):
        try:
            row = getter()
        except TypeError:
            row = None
        if isinstance(row, int) and row >= 0:
            return row
    return None


def _connect_signal(widget: Any, signal_name: str, callback: Any) -> bool:
    if callback is None:
        return False
    signal = getattr(widget, signal_name, None)
    connect = getattr(signal, "connect", None)
    if callable(connect):
        connect(callback)
        return True
    return False


def _lane_ids_from_table_model(table_model: Mapping[str, Any]) -> list[str]:
    rows = [row for row in _as_list(table_model.get("rows")) if isinstance(row, Mapping)]
    lane_ids: list[str] = []
    for row in rows:
        lane_id = _text(row.get("lane_id") or row.get("id"))
        if lane_id:
            lane_ids.append(lane_id)
    return lane_ids


def _lane_id_for_row(table_model: Mapping[str, Any], row_index: object) -> str | None:
    rows = [row for row in _as_list(table_model.get("rows")) if isinstance(row, Mapping)]
    try:
        index = int(row_index)
    except (TypeError, ValueError):
        return None
    if 0 <= index < len(rows):
        return _text(rows[index].get("lane_id") or rows[index].get("id")) or None
    return None


def _dispatch_intent(
    intent_dispatcher: Any | None,
    intent: Mapping[str, Any],
    *,
    stateful_rebuild_handler: Any | None = None,
    service_bundle: Mapping[str, Any] | None = None,
) -> None:
    payload = dict(intent)
    if intent_dispatcher is not None:
        intent_dispatcher(payload)
    if stateful_rebuild_handler is not None and service_bundle is not None:
        from .core.gui_review_workbench_stateful_callbacks import build_review_workbench_stateful_callback_response

        stateful_rebuild_handler(build_review_workbench_stateful_callback_response(service_bundle, payload))


def _make_intent(
    interaction_plan: Mapping[str, Any],
    intent_kind: str,
    *,
    lane_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
    sort_mode: str | None = None,
    action_id: str | None = None,
    target_page_id: str | None = None,
    enabled: bool = True,
    reason: str | None = None,
) -> Mapping[str, Any]:
    catalog = [
        _as_mapping(item)
        for item in _as_list(interaction_plan.get("intent_catalog"))
        if _as_mapping(item).get("intent_kind") == intent_kind
    ]
    if catalog and all(value is None for value in (lane_id, status, query, sort_mode, action_id, target_page_id)) and enabled is True and reason is None:
        return dict(catalog[0])
    base = _as_mapping(catalog[0]) if catalog else {}
    return build_review_workbench_interaction_intent(
        intent_kind,
        lane_id=lane_id if lane_id is not None else _text(base.get("lane_id")) or None,
        status=status if status is not None else _text(base.get("status")) or None,
        query=query if query is not None else str(base.get("query") or ""),
        sort_mode=sort_mode if sort_mode is not None else _text(base.get("sort_mode")) or None,
        action_id=action_id if action_id is not None else _text(base.get("action_id")) or None,
        target_page_id=target_page_id if target_page_id is not None else _text(base.get("target_page_id")) or None,
        enabled=enabled,
        reason=reason,
    )


def _add_widget(layout: Any, widget: Any, stretch: int | None = None) -> None:
    add = getattr(layout, "addWidget", None)
    if not callable(add):
        return
    if stretch is None:
        add(widget)
    else:
        add(widget, stretch)


def _add_layout(layout: Any, child_layout: Any) -> None:
    add = getattr(layout, "addLayout", None)
    if callable(add):
        add(child_layout)


def _add_stretch(layout: Any, stretch: int = 1) -> None:
    add = getattr(layout, "addStretch", None)
    if callable(add):
        add(stretch)


def _layout(QtWidgets: Any, layout_class: str, parent: Any | None = None) -> Any:
    cls = getattr(QtWidgets, layout_class, getattr(QtWidgets, "QVBoxLayout"))
    try:
        return cls(parent)
    except TypeError:
        return cls()


def _widget(QtWidgets: Any, widget_class: str = "QWidget", *args: Any) -> Any:
    cls = getattr(QtWidgets, widget_class, getattr(QtWidgets, "QWidget"))
    try:
        return cls(*args)
    except TypeError:
        return cls()


def _label(QtWidgets: Any, text: object, *, object_name: str | None = None) -> Any:
    label = _widget(QtWidgets, "QLabel", _text(text))
    if object_name:
        _set_object_name(label, object_name)
    setter = getattr(label, "setWordWrap", None)
    if callable(setter):
        setter(True)
    return label


def _button(QtWidgets: Any, label: str, *, enabled: bool = True, object_name: str | None = None) -> Any:
    button = _widget(QtWidgets, "QPushButton", label)
    if object_name:
        _set_object_name(button, object_name)
    setter = getattr(button, "setEnabled", None)
    if callable(setter):
        setter(enabled)
    return button


def _table_widget(
    QtWidgets: Any,
    table_model: Mapping[str, Any],
    interaction_plan: Mapping[str, Any] | None = None,
    intent_dispatcher: Any | None = None,
    stateful_rebuild_handler: Any | None = None,
    service_bundle: Mapping[str, Any] | None = None,
) -> Any:
    rows = [row for row in _as_list(table_model.get("rows")) if isinstance(row, Mapping)]
    columns = [str(_as_mapping(column).get("id") or column) for column in _as_list(table_model.get("columns"))]
    table = _widget(QtWidgets, "QTableWidget", len(rows), len(columns))
    _set_object_name(table, "ReviewWorkbenchLaneTable")
    _set_property(table, "selection_intent_kind", "lane_selected")
    _set_property(table, "activation_intent_kind", "table_row_activated")
    _set_property(table, "lane_ids", _lane_ids_from_table_model(table_model))
    _set_property(table, "executes_commands", False)
    if hasattr(table, "setColumnCount"):
        table.setColumnCount(len(columns))
    if hasattr(table, "setRowCount"):
        table.setRowCount(len(rows))
    if hasattr(table, "setHorizontalHeaderLabels"):
        table.setHorizontalHeaderLabels(columns)
    item_cls = getattr(QtWidgets, "QTableWidgetItem", None)
    if item_cls is not None and hasattr(table, "setItem"):
        for row_index, row in enumerate(rows):
            for column_index, column in enumerate(columns):
                try:
                    item = item_cls(_text(row.get(column)))
                except TypeError:
                    item = item_cls()
                table.setItem(row_index, column_index, item)
    if hasattr(table, "setAlternatingRowColors"):
        table.setAlternatingRowColors(True)
    plan = _as_mapping(interaction_plan)
    if intent_dispatcher is not None:
        def dispatch_selected(*_args: Any) -> None:
            lane_id = _lane_id_for_row(table_model, _current_row(table))
            _dispatch_intent(intent_dispatcher, _make_intent(plan, "lane_selected", lane_id=lane_id), stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle)

        def dispatch_activated(row: object = None, *_args: Any) -> None:
            lane_id = _lane_id_for_row(table_model, row if row is not None else _current_row(table))
            _dispatch_intent(intent_dispatcher, _make_intent(plan, "table_row_activated", lane_id=lane_id), stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle)

        _connect_signal(table, "itemSelectionChanged", dispatch_selected)
        _connect_signal(table, "cellDoubleClicked", dispatch_activated)
    return table




def _intent_for_action(interaction_plan: Mapping[str, Any], action_id: str) -> Mapping[str, Any]:
    wanted = _text(action_id)
    for intent in _as_list(interaction_plan.get("intent_catalog")):
        intent_map = _as_mapping(intent)
        if str(intent_map.get("action_id") or "") == wanted:
            return intent_map
    return {}


def _connect_triggered(action: Any, callback: Any) -> None:
    if callback is None:
        return
    triggered = getattr(action, "triggered", None)
    connect = getattr(triggered, "connect", None)
    if callable(connect):
        connect(callback)

def _build_toolbar(
    QtWidgets: Any,
    action_plan: Mapping[str, Any],
    interaction_plan: Mapping[str, Any],
    intent_dispatcher: Any | None = None,
    stateful_rebuild_handler: Any | None = None,
    service_bundle: Mapping[str, Any] | None = None,
) -> tuple[Any, dict[str, Any]]:
    toolbar = _widget(QtWidgets, "QToolBar", "Review Workbench")
    _set_object_name(toolbar, "ReviewWorkbenchToolbar")
    actions: dict[str, Any] = {}
    add_action = getattr(toolbar, "addAction", None)
    for raw_action in _as_list(action_plan.get("actions")):
        action = _as_mapping(raw_action)
        action_id = _text(action.get("id"), "action")
        label = _text(action.get("label"), action_id.replace("_", " ").title())
        if callable(add_action):
            try:
                qt_action = add_action(label)
            except TypeError:
                qt_action = None
        else:
            qt_action = _button(QtWidgets, label, enabled=bool(action.get("enabled", True)))
        if qt_action is not None:
            intent = _intent_for_action(interaction_plan, action_id)
            _set_property(qt_action, "action_id", action_id)
            _set_property(qt_action, "intent_kind", intent.get("intent_kind"))
            _set_property(qt_action, "target_page_id", action.get("page_id"))
            _set_property(qt_action, "executes_commands", False)
            setter = getattr(qt_action, "setEnabled", None)
            if callable(setter):
                setter(bool(action.get("enabled", True)))
            if intent and intent_dispatcher is not None:
                payload = dict(intent)
                _connect_triggered(qt_action, lambda *_args, payload=payload: _dispatch_intent(intent_dispatcher, payload, stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle))
            actions[action_id] = qt_action
    return toolbar, actions


def _build_filter_bar(
    QtWidgets: Any,
    view_model: Mapping[str, Any],
    interaction_plan: Mapping[str, Any],
    intent_dispatcher: Any | None = None,
    stateful_rebuild_handler: Any | None = None,
    service_bundle: Mapping[str, Any] | None = None,
) -> tuple[Any, dict[str, Any]]:
    frame = _widget(QtWidgets, "QWidget")
    _set_object_name(frame, "ReviewWorkbenchFilterBar")
    layout = _layout(QtWidgets, "QHBoxLayout", frame)
    lane_filter = _as_mapping(view_model.get("lane_filter"))
    lane_sort = _as_mapping(view_model.get("lane_sort"))
    query = _widget(QtWidgets, "QLineEdit")
    _set_object_name(query, "ReviewWorkbenchQuery")
    _set_property(query, "intent_kind", "filter_query_changed")
    _set_property(query, "executes_commands", False)
    if hasattr(query, "setPlaceholderText"):
        query.setPlaceholderText("Filter review lanes")
    if hasattr(query, "setText"):
        query.setText(_text(lane_filter.get("query")))
    status = _widget(QtWidgets, "QComboBox")
    _set_object_name(status, "ReviewWorkbenchStatusFilter")
    _set_property(status, "intent_kind", "filter_status_changed")
    _set_property(status, "executes_commands", False)
    if hasattr(status, "addItems"):
        status.addItems([str(item) for item in _as_list(lane_filter.get("available_statuses"))] or ["all"])
    sort = _widget(QtWidgets, "QComboBox")
    _set_object_name(sort, "ReviewWorkbenchSortMode")
    _set_property(sort, "intent_kind", "sort_mode_changed")
    _set_property(sort, "executes_commands", False)
    if hasattr(sort, "addItems"):
        sort.addItems([str(item) for item in _as_list(lane_sort.get("available_modes"))] or ["attention_first"])
    if intent_dispatcher is not None:
        _connect_signal(query, "textChanged", lambda value="": _dispatch_intent(intent_dispatcher, _make_intent(interaction_plan, "filter_query_changed", query=str(value or "")), stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle))
        _connect_signal(status, "currentTextChanged", lambda value="all": _dispatch_intent(intent_dispatcher, _make_intent(interaction_plan, "filter_status_changed", status=str(value or "all")), stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle))
        _connect_signal(sort, "currentTextChanged", lambda value="attention_first": _dispatch_intent(intent_dispatcher, _make_intent(interaction_plan, "sort_mode_changed", sort_mode=str(value or "attention_first")), stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle))
    _add_widget(layout, _label(QtWidgets, "Filter", object_name="Muted"))
    _add_widget(layout, query, 1)
    _add_widget(layout, status)
    _add_widget(layout, sort)
    return frame, {"filter_bar": frame, "query": query, "status_filter": status, "sort_mode": sort}


def _build_detail_panel(
    QtWidgets: Any,
    view_model: Mapping[str, Any],
    interaction_plan: Mapping[str, Any],
    intent_dispatcher: Any | None = None,
    stateful_rebuild_handler: Any | None = None,
    service_bundle: Mapping[str, Any] | None = None,
) -> tuple[Any, dict[str, Any]]:
    detail = _as_mapping(view_model.get("selected_lane_detail"))
    frame = _widget(QtWidgets, "QWidget")
    _set_object_name(frame, "ReviewWorkbenchLaneDetail")
    layout = _layout(QtWidgets, "QVBoxLayout", frame)
    _add_widget(layout, _label(QtWidgets, detail.get("headline") or "No lane selected", object_name="SectionTitle"))
    description = _widget(QtWidgets, "QTextEdit")
    _set_object_name(description, "ReviewWorkbenchLaneDescription")
    if hasattr(description, "setPlainText"):
        description.setPlainText(_text(detail.get("description")))
    if hasattr(description, "setReadOnly"):
        description.setReadOnly(True)
    _add_widget(layout, description, 1)
    next_step = detail.get("recommended_next_step")
    if next_step:
        _add_widget(layout, _label(QtWidgets, next_step, object_name="Muted"))
    widgets = {"lane_detail": frame, "lane_description": description}
    primary = _as_mapping(detail.get("primary_action"))
    if primary:
        button = _button(QtWidgets, _text(primary.get("label"), "Open"), enabled=bool(primary.get("enabled", True)), object_name="ReviewWorkbenchLaneDetailPrimaryAction")
        _set_property(button, "intent_kind", "toolbar_open_selected_lane")
        _set_property(button, "executes_commands", False)
        if intent_dispatcher is not None:
            lane_id = _text(detail.get("lane_id") or view_model.get("selected_lane_id")) or None
            target_page_id = _text(primary.get("page_id") or view_model.get("navigation_target_page_id")) or None
            _connect_signal(
                button,
                "clicked",
                lambda *_args, lane_id=lane_id, target_page_id=target_page_id: _dispatch_intent(
                    intent_dispatcher,
                    _make_intent(
                        interaction_plan,
                        "toolbar_open_selected_lane",
                        lane_id=lane_id,
                        target_page_id=target_page_id,
                        enabled=bool(primary.get("enabled", True)),
                    ),
                    stateful_rebuild_handler=stateful_rebuild_handler,
                    service_bundle=service_bundle,
                ),
            )
        _add_widget(layout, button)
        widgets["primary_action"] = button
    _add_stretch(layout)
    return frame, widgets


def _build_body(
    QtWidgets: Any,
    table_model: Mapping[str, Any],
    view_model: Mapping[str, Any],
    interaction_plan: Mapping[str, Any],
    intent_dispatcher: Any | None = None,
    stateful_rebuild_handler: Any | None = None,
    service_bundle: Mapping[str, Any] | None = None,
) -> tuple[Any, dict[str, Any]]:
    splitter = _widget(QtWidgets, "QSplitter")
    _set_object_name(splitter, "ReviewWorkbenchSplitter")
    add = getattr(splitter, "addWidget", None)
    table = _table_widget(QtWidgets, table_model, interaction_plan, intent_dispatcher, stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle)
    detail, detail_widgets = _build_detail_panel(QtWidgets, view_model, interaction_plan, intent_dispatcher, stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle)
    if callable(add):
        add(table)
        add(detail)
    else:
        layout = _layout(QtWidgets, "QHBoxLayout", splitter)
        _add_widget(layout, table, 3)
        _add_widget(layout, detail, 2)
    return splitter, {"body": splitter, "lane_table": table, **detail_widgets}



def _section_by_id(panel: Mapping[str, Any], section_id: str) -> Mapping[str, Any]:
    for section in _as_list(panel.get("sections")):
        section_map = _as_mapping(section)
        if section_map.get("id") == section_id:
            return section_map
    return {}


def _rows_as_text(rows: object, *, limit: int = 12) -> str:
    lines: list[str] = []
    for raw in _as_list(rows)[: max(0, limit)]:
        row = _as_mapping(raw)
        label = _text(row.get("label") or row.get("id"), "item")
        if "argv_preview" in row:
            suffix = _text(row.get("argv_preview"))
        elif "value" in row:
            suffix = str(row.get("value"))
        elif "satisfied" in row:
            suffix = "ok" if row.get("satisfied") is True else _text(row.get("blocked_reason"), "blocked")
        else:
            suffix = _text(row.get("blocked_reason"))
        lines.append(f"- {label}: {suffix}" if suffix else f"- {label}")
    return "\n".join(lines)


def _build_executor_handoff_panel(QtWidgets: Any, executor_handoff_panel: Mapping[str, Any]) -> tuple[Any, dict[str, Any]]:
    frame = _widget(QtWidgets, "QWidget")
    _set_object_name(frame, "ReviewWorkbenchExecutorHandoffPanel")
    _set_property(frame, "panel_id", executor_handoff_panel.get("panel_id"))
    _set_property(frame, "executes_commands", False)
    _set_property(frame, "execution_enabled", False)
    _set_property(frame, "apply_enabled", False)
    layout = _layout(QtWidgets, "QVBoxLayout", frame)
    summary = _as_mapping(executor_handoff_panel.get("summary"))
    _add_widget(layout, _label(QtWidgets, "Apply handoff", object_name="SectionTitle"))
    _add_widget(
        layout,
        _label(
            QtWidgets,
            f"Status: {summary.get('status', 'blocked')}   Executor: {summary.get('executor_status', 'blocked')}   Commands: {summary.get('dry_run_command_count', 0)}   Failed checks: {summary.get('preflight_failed_check_count', 0)}",
            object_name="MetricText",
        ),
    )
    confirmation = _section_by_id(executor_handoff_panel, "typed-confirmation")
    preflight = _section_by_id(executor_handoff_panel, "preflight")
    dry_run = _section_by_id(executor_handoff_panel, "dry-run-plan")
    audit = _section_by_id(executor_handoff_panel, "audit-plan")

    phrase = _text(confirmation.get("phrase"), "APPLY REVIEWED DECISIONS")
    phrase_label = _label(QtWidgets, f"Required phrase: {phrase}", object_name="Muted")
    _set_property(phrase_label, "confirmation_phrase", phrase)
    _set_property(phrase_label, "typed_confirmation_is_persisted", False)
    _add_widget(layout, phrase_label)

    preflight_box = _widget(QtWidgets, "QTextEdit")
    _set_object_name(preflight_box, "ReviewWorkbenchExecutorPreflight")
    if hasattr(preflight_box, "setPlainText"):
        preflight_box.setPlainText(_rows_as_text(preflight.get("rows")) or "No preflight rows")
    if hasattr(preflight_box, "setReadOnly"):
        preflight_box.setReadOnly(True)
    _set_property(preflight_box, "executes_commands", False)
    _add_widget(layout, preflight_box)

    command_box = _widget(QtWidgets, "QTextEdit")
    _set_object_name(command_box, "ReviewWorkbenchExecutorDryRunPlan")
    if hasattr(command_box, "setPlainText"):
        command_box.setPlainText(_rows_as_text(dry_run.get("rows")) or "No dry-run commands")
    if hasattr(command_box, "setReadOnly"):
        command_box.setReadOnly(True)
    _set_property(command_box, "executes_commands", False)
    _add_widget(layout, command_box)

    audit_box = _widget(QtWidgets, "QTextEdit")
    _set_object_name(audit_box, "ReviewWorkbenchExecutorAuditPlan")
    if hasattr(audit_box, "setPlainText"):
        audit_box.setPlainText(_rows_as_text(audit.get("rows")) or "No audit rows")
    if hasattr(audit_box, "setReadOnly"):
        audit_box.setReadOnly(True)
    _set_property(audit_box, "executes_commands", False)
    _add_widget(layout, audit_box)

    confirm_button = _button(QtWidgets, "Confirm apply", enabled=False, object_name="ReviewWorkbenchExecutorConfirmApply")
    _set_property(confirm_button, "action_id", "confirm_apply")
    _set_property(confirm_button, "executes_commands", False)
    _set_property(confirm_button, "execution_enabled", False)
    _add_widget(layout, confirm_button)
    return frame, {
        "executor_handoff_panel": frame,
        "executor_preflight": preflight_box,
        "executor_dry_run_plan": command_box,
        "executor_audit_plan": audit_box,
        "executor_confirm_apply": confirm_button,
    }

def build_review_workbench_widget_skeleton_from_page(page_model: Mapping[str, Any]) -> dict[str, object]:
    """Return the pure-data widget skeleton embedded in a Review Workbench page."""

    binding_plan = _as_mapping(page_model.get("qt_widget_binding_plan"))
    return build_qt_review_workbench_widget_skeleton(binding_plan)


def build_review_workbench_page_widget(
    QtWidgets: Any,
    page_model: Mapping[str, Any],
    *,
    intent_dispatcher: Any | None = None,
    stateful_rebuild_handler: Any | None = None,
) -> ReviewWorkbenchQtWidgetMount:
    """Build the Review Workbench page widget from an explicit QtWidgets module.

    The module import itself remains PySide6-lazy. Tests can pass a fake
    QtWidgets namespace; the real desktop runtime passes PySide6.QtWidgets after
    the optional GUI dependency has been loaded.
    """

    skeleton = build_review_workbench_widget_skeleton_from_page(page_model)
    root = _widget(QtWidgets, "QWidget")
    _set_object_name(root, "ReviewWorkbenchPage")
    layout = _layout(QtWidgets, "QVBoxLayout", root)
    view_model = _as_mapping(page_model.get("view_model"))
    table_model = _as_mapping(page_model.get("table_model"))
    action_plan = _as_mapping(page_model.get("action_plan"))
    interaction_plan = _as_mapping(page_model.get("interaction_plan"))
    callback_mount_plan = _as_mapping(page_model.get("callback_mount_plan"))
    apply_preview = _as_mapping(page_model.get("apply_preview"))
    confirmation_dialog = _as_mapping(page_model.get("confirmation_dialog"))
    apply_executor_contract = _as_mapping(page_model.get("apply_executor_contract"))
    executor_handoff_panel = _as_mapping(page_model.get("executor_handoff_panel"))
    stateful_rebuild_loop = _as_mapping(page_model.get("stateful_rebuild_loop"))
    stateful_callback_plan = _as_mapping(page_model.get("stateful_callback_plan"))
    service_bundle = _as_mapping(page_model.get("workbench_service"))
    _set_property(root, "stateful_rebuild_loop_ready", _as_mapping(stateful_rebuild_loop.get("readiness")).get("ready"))
    _set_property(root, "stateful_rebuild_intent_count", _as_mapping(stateful_rebuild_loop.get("summary")).get("stateful_intent_count", 0))
    _set_property(root, "stateful_callback_plan_ready", _as_mapping(stateful_callback_plan.get("readiness")).get("ready"))
    _set_property(root, "stateful_callback_rebuild_count", _as_mapping(stateful_callback_plan.get("summary")).get("page_rebuild_callback_count", 0))
    confirmation_summary = _as_mapping(confirmation_dialog.get("summary"))
    apply_executor_summary = _as_mapping(apply_executor_contract.get("summary"))
    apply_preview_summary = _as_mapping(apply_preview.get("summary"))
    summary = _as_mapping(page_model.get("summary"))

    header = _widget(QtWidgets, "QWidget")
    _set_object_name(header, "ReviewWorkbenchHeader")
    header_layout = _layout(QtWidgets, "QVBoxLayout", header)
    _add_widget(header_layout, _label(QtWidgets, page_model.get("title") or "Review Workbench", object_name="PageTitle"))
    _add_widget(
        header_layout,
        _label(
            QtWidgets,
            f"Lanes: {summary.get('lane_count', 0)}   Needs review: {summary.get('attention_count', 0)}   Apply preview: {apply_preview_summary.get('status', summary.get('apply_preview_status', 'blocked'))}   Confirmation: {confirmation_summary.get('status', summary.get('confirmation_dialog_status', 'blocked'))}   Executor: {apply_executor_summary.get('status', summary.get('apply_executor_contract_status', 'blocked'))}   Apply enabled: {summary.get('apply_enabled', False)}",
            object_name="MetricText",
        ),
    )
    _add_widget(layout, header)

    toolbar, actions = _build_toolbar(QtWidgets, action_plan, interaction_plan, intent_dispatcher, stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle)
    _add_widget(layout, toolbar)
    filter_bar, filter_widgets = _build_filter_bar(QtWidgets, view_model, interaction_plan, intent_dispatcher, stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle)
    _add_widget(layout, filter_bar)
    body, body_widgets = _build_body(QtWidgets, table_model, view_model, interaction_plan, intent_dispatcher, stateful_rebuild_handler=stateful_rebuild_handler, service_bundle=service_bundle)
    _add_widget(layout, body, 1)
    handoff, handoff_widgets = _build_executor_handoff_panel(QtWidgets, executor_handoff_panel)
    _add_widget(layout, handoff)

    widgets = {
        "root": root,
        "header": header,
        "toolbar": toolbar,
        **filter_widgets,
        **body_widgets,
        **handoff_widgets,
    }
    return ReviewWorkbenchQtWidgetMount(
        root_widget=root,
        skeleton=skeleton,
        widgets=widgets,
        actions=actions,
        model_sources={
            "view_model": view_model,
            "table_model": table_model,
            "action_plan": action_plan,
            "callback_mount_plan": callback_mount_plan,
            "apply_preview": apply_preview,
            "confirmation_dialog": confirmation_dialog,
            "apply_executor_contract": apply_executor_contract,
            "executor_handoff_panel": executor_handoff_panel,
            "stateful_rebuild_loop": stateful_rebuild_loop,
            "stateful_callback_plan": stateful_callback_plan,
        },
        interaction_plan=interaction_plan,
        callback_mount_plan=callback_mount_plan,
        apply_preview=apply_preview,
        confirmation_dialog=confirmation_dialog,
        apply_executor_contract=apply_executor_contract,
        executor_handoff_panel=executor_handoff_panel,
        stateful_rebuild_loop=stateful_rebuild_loop,
        stateful_callback_plan=stateful_callback_plan,
        callback_mounts={"widgets": widgets, "actions": actions},
    )


__all__ = [
    "ReviewWorkbenchQtWidgetMount",
    "build_review_workbench_page_widget",
    "build_review_workbench_widget_skeleton_from_page",
]
