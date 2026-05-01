from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.app_services import (
    build_app_contract_inventory,
    build_gui_app_contract_bindings,
    build_gui_review_workbench_service_bundle,
    build_review_workbench_apply_executor_contract,
    build_review_workbench_executor_handoff_panel,
    build_review_workbench_stateful_rebuild_bundle,
    build_review_workbench_stateful_callback_plan,
    build_review_workbench_stateful_callback_response,
    map_review_workbench_callback_intent_to_rebuild_intent,
    normalize_review_workbench_rebuild_intent,
    write_review_workbench_stateful_rebuild_bundle,
    write_review_workbench_stateful_callback_plan,
    build_app_home_state,
    read_json_object,
    write_json_object,
    write_report_service_bundle,
    write_gui_review_workbench_service_bundle,
    write_review_workbench_interaction_plan,
    write_review_workbench_callback_mount_plan,
    write_review_workbench_apply_preview,
    write_review_workbench_confirmation_dialog_model,
    write_review_workbench_apply_executor_contract,
    write_review_workbench_executor_handoff_panel,
    write_qt_review_workbench_widget_binding_plan,
    write_qt_review_workbench_widget_skeleton,
)
from .core.app_startup import build_app_startup_state
from .core.gui_app_contract_bindings import summarize_gui_app_contract_bindings
from .core.gui_app_service_view_models import (
    build_ui_app_service_view_models,
    summarize_ui_app_service_view_models,
    write_ui_app_service_view_models,
)
from .core.gui_desktop_runtime_state import (
    build_gui_desktop_runtime_state,
    summarize_gui_desktop_runtime_state,
    write_gui_desktop_runtime_state,
)
from .core.gui_command_plan import (
    build_open_people_bundle_plan,
    build_people_review_apply_command_plan,
    build_profile_command_plan,
    write_command_plan,
)
from .core.gui_page_contracts import build_gui_navigation_state, build_gui_page_catalog
from .core.gui_state_store import (
    add_recent_path,
    build_default_gui_state,
    build_gui_state_summary,
    load_gui_state,
    register_people_bundle,
    set_active_page,
    write_gui_state,
)
from .core.people_review_audit import build_people_review_apply_preview, write_people_review_apply_preview
from .core.people_review_bundle_validator import validate_people_review_bundle, write_people_review_bundle_validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager app-services",
        description="GUI-facing service helpers for Media Manager frontends.",
    )
    subparsers = parser.add_subparsers(dest="service_command")

    home = subparsers.add_parser("home-state", help="Build a GUI dashboard/home state from profiles, runs, and optional people bundle.")
    home.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    home.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    home.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    home.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    home.add_argument("--run-limit", type=int, default=10, help="Maximum recent runs to include. Default: 10.")
    home.add_argument("--out", type=Path, help="Optional output JSON path.")
    home.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    startup = subparsers.add_parser("startup-state", help="Build the first state object a future GUI can load at startup.")
    startup.add_argument("--gui-state", type=Path, help="Optional persisted GUI state JSON path.")
    startup.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    startup.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    startup.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    startup.add_argument("--active-page", help="Override active GUI page id.")
    startup.add_argument("--out", type=Path, help="Optional output JSON path.")
    startup.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    desktop = subparsers.add_parser("desktop-runtime", help="Build the headless desktop runtime state consumed by the future Qt UI.")
    desktop.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    desktop.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    desktop.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    desktop.add_argument("--home-state-json", type=Path, help="Optional prebuilt app home-state JSON.")
    desktop.add_argument("--settings-json", type=Path, help="Optional GUI settings JSON.")
    desktop.add_argument("--view-state-json", type=Path, help="Optional GUI view-state JSON.")
    desktop.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    desktop.add_argument("--language", choices=["en", "de"], help="GUI language. Supported: en, de.")
    desktop.add_argument("--theme", help="GUI theme. Default comes from settings or modern-dark.")
    desktop.add_argument("--density", choices=["compact", "comfortable", "spacious"], help="GUI density.")
    desktop.add_argument("--out-dir", type=Path, help="Optional directory for split desktop-runtime JSON files.")
    desktop.add_argument("--out", type=Path, help="Optional output JSON path.")
    desktop.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    view_models = subparsers.add_parser("ui-view-models", help="Build product UI app-service view models for future Qt pages.")
    view_models.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    view_models.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    view_models.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    view_models.add_argument("--home-state-json", type=Path, help="Optional prebuilt app home-state JSON.")
    view_models.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    view_models.add_argument("--language", choices=["en", "de"], help="GUI language. Supported: en, de.")
    view_models.add_argument("--out-dir", type=Path, help="Optional directory for split view-model JSON files.")
    view_models.add_argument("--out", type=Path, help="Optional output JSON path.")
    view_models.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    report = subparsers.add_parser("report-bundle", help="Build ui_state, plan_snapshot, and action_model for one report.")
    report.add_argument("--command", required=True, help="Command name for the report.")
    report.add_argument("--report-json", type=Path, required=True, help="Report JSON path.")
    report.add_argument("--command-json", type=Path, help="Optional command.json path.")
    report.add_argument("--run-id", help="Optional run id.")
    report.add_argument("--entry-limit", type=int, default=200, help="Maximum plan snapshot rows. Default: 200.")
    report.add_argument("--out-dir", type=Path, required=True, help="Directory to write derived service artifacts.")
    report.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    pages = subparsers.add_parser("pages", help="Print GUI page contracts and navigation state.")
    pages.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    pages.add_argument("--out", type=Path, help="Optional output JSON path.")
    pages.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    contracts = subparsers.add_parser("contracts", help="Print GUI-facing app-service contract inventory.")
    contracts.add_argument("--out", type=Path, help="Optional output JSON path.")
    contracts.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    contract_bindings = subparsers.add_parser("contract-bindings", help="Validate GUI surface bindings for app-service contracts.")
    contract_bindings.add_argument("--out", type=Path, help="Optional output JSON path.")
    contract_bindings.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    review_workbench = subparsers.add_parser("review-workbench", help="Build a headless Qt-ready Review Workbench service bundle.")
    review_workbench.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    review_workbench.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    review_workbench.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    review_workbench.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    review_workbench.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    review_workbench.add_argument("--reviewed-decision-plan-json", type=Path, help="Optional reviewed decision plan JSON for non-executing apply preview.")
    review_workbench.add_argument("--selected-lane", help="Optional selected review lane id.")
    review_workbench.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    review_workbench.add_argument("--lane-query", default="", help="Lane search query.")
    review_workbench.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    review_workbench.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    review_workbench.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    review_workbench.add_argument("--out-dir", type=Path, help="Optional directory for split Review Workbench artifacts.")
    review_workbench.add_argument("--out", type=Path, help="Optional output JSON path.")
    review_workbench.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    widget_bindings = subparsers.add_parser(
        "review-workbench-widget-bindings",
        help="Build descriptor-only Qt widget bindings for the Review Workbench adapter package.",
    )
    widget_bindings.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    widget_bindings.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    widget_bindings.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    widget_bindings.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    widget_bindings.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    widget_bindings.add_argument("--selected-lane", help="Optional selected review lane id.")
    widget_bindings.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    widget_bindings.add_argument("--lane-query", default="", help="Lane search query.")
    widget_bindings.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    widget_bindings.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    widget_bindings.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    widget_bindings.add_argument("--out-dir", type=Path, help="Optional directory for the widget binding plan JSON.")
    widget_bindings.add_argument("--out", type=Path, help="Optional output JSON path.")
    widget_bindings.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    widget_skeleton = subparsers.add_parser(
        "review-workbench-widget-skeleton",
        help="Build the lazy PySide6 Review Workbench widget skeleton from the Qt binding plan.",
    )
    widget_skeleton.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    widget_skeleton.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    widget_skeleton.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    widget_skeleton.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    widget_skeleton.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    widget_skeleton.add_argument("--selected-lane", help="Optional selected review lane id.")
    widget_skeleton.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    widget_skeleton.add_argument("--lane-query", default="", help="Lane search query.")
    widget_skeleton.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    widget_skeleton.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    widget_skeleton.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    widget_skeleton.add_argument("--out-dir", type=Path, help="Optional directory for the widget skeleton JSON.")
    widget_skeleton.add_argument("--out", type=Path, help="Optional output JSON path.")
    widget_skeleton.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    interactions = subparsers.add_parser(
        "review-workbench-interactions",
        help="Build non-executing Qt signal and toolbar interaction intents for the Review Workbench.",
    )
    interactions.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    interactions.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    interactions.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    interactions.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    interactions.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    interactions.add_argument("--selected-lane", help="Optional selected review lane id.")
    interactions.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    interactions.add_argument("--lane-query", default="", help="Lane search query.")
    interactions.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    interactions.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    interactions.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    interactions.add_argument("--out-dir", type=Path, help="Optional directory for the interaction plan JSON.")
    interactions.add_argument("--out", type=Path, help="Optional output JSON path.")
    interactions.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    callback_mounts = subparsers.add_parser(
        "review-workbench-callback-mounts",
        help="Build concrete non-executing Qt signal callback mounts for the Review Workbench.",
    )
    callback_mounts.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    callback_mounts.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    callback_mounts.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    callback_mounts.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    callback_mounts.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    callback_mounts.add_argument("--selected-lane", help="Optional selected review lane id.")
    callback_mounts.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    callback_mounts.add_argument("--lane-query", default="", help="Lane search query.")
    callback_mounts.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    callback_mounts.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    callback_mounts.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    callback_mounts.add_argument("--out-dir", type=Path, help="Optional directory for the callback mount plan JSON.")
    callback_mounts.add_argument("--out", type=Path, help="Optional output JSON path.")
    callback_mounts.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    apply_preview = subparsers.add_parser(
        "review-workbench-apply-preview",
        help="Build a non-executing reviewed apply command-plan preview for the Review Workbench.",
    )
    apply_preview.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    apply_preview.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    apply_preview.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    apply_preview.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    apply_preview.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    apply_preview.add_argument("--reviewed-decision-plan-json", type=Path, help="Optional reviewed decision plan JSON.")
    apply_preview.add_argument("--selected-lane", help="Optional selected review lane id.")
    apply_preview.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    apply_preview.add_argument("--lane-query", default="", help="Lane search query.")
    apply_preview.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    apply_preview.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    apply_preview.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    apply_preview.add_argument("--out-dir", type=Path, help="Optional directory for the apply preview JSON bundle.")
    apply_preview.add_argument("--out", type=Path, help="Optional output JSON path.")
    apply_preview.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    confirmation_dialog = subparsers.add_parser(
        "review-workbench-confirmation-dialog",
        help="Build a guarded non-executing confirmation dialog model for the Review Workbench apply preview.",
    )
    confirmation_dialog.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    confirmation_dialog.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    confirmation_dialog.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    confirmation_dialog.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    confirmation_dialog.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    confirmation_dialog.add_argument("--reviewed-decision-plan-json", type=Path, help="Optional reviewed decision plan JSON.")
    confirmation_dialog.add_argument("--selected-lane", help="Optional selected review lane id.")
    confirmation_dialog.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    confirmation_dialog.add_argument("--lane-query", default="", help="Lane search query.")
    confirmation_dialog.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    confirmation_dialog.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    confirmation_dialog.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    confirmation_dialog.add_argument("--out-dir", type=Path, help="Optional directory for the confirmation dialog JSON bundle.")
    confirmation_dialog.add_argument("--out", type=Path, help="Optional output JSON path.")
    confirmation_dialog.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    apply_executor = subparsers.add_parser(
        "review-workbench-apply-executor-contract",
        help="Build a disabled-by-default dry-run executor contract for the Review Workbench confirmation dialog.",
    )
    apply_executor.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    apply_executor.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    apply_executor.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    apply_executor.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    apply_executor.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    apply_executor.add_argument("--reviewed-decision-plan-json", type=Path, help="Optional reviewed decision plan JSON.")
    apply_executor.add_argument("--typed-confirmation", help="Optional typed confirmation phrase for preflight evaluation. Never persisted as an execution approval.")
    apply_executor.add_argument("--executor-enabled", action="store_true", help="Probe the refusal path; this contract still never executes commands.")
    apply_executor.add_argument("--selected-lane", help="Optional selected review lane id.")
    apply_executor.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    apply_executor.add_argument("--lane-query", default="", help="Lane search query.")
    apply_executor.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    apply_executor.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    apply_executor.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    apply_executor.add_argument("--out-dir", type=Path, help="Optional directory for the apply executor contract JSON bundle.")
    apply_executor.add_argument("--out", type=Path, help="Optional output JSON path.")
    apply_executor.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")


    apply_handoff = subparsers.add_parser(
        "review-workbench-apply-handoff-panel",
        help="Build a display-only confirmation/executor handoff panel for the Review Workbench.",
    )
    apply_handoff.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    apply_handoff.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    apply_handoff.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    apply_handoff.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    apply_handoff.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    apply_handoff.add_argument("--reviewed-decision-plan-json", type=Path, help="Optional reviewed decision plan JSON.")
    apply_handoff.add_argument("--typed-confirmation", help="Optional typed confirmation phrase for handoff preview. Never persisted as approval.")
    apply_handoff.add_argument("--executor-enabled", action="store_true", help="Probe the refusal path; the handoff still never executes commands.")
    apply_handoff.add_argument("--selected-lane", help="Optional selected review lane id.")
    apply_handoff.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Lane status filter. Default: all.")
    apply_handoff.add_argument("--lane-query", default="", help="Lane search query.")
    apply_handoff.add_argument("--lane-sort", default="attention_first", help="Lane sort mode. Default: attention_first.")
    apply_handoff.add_argument("--page", type=int, default=1, help="Table page. Default: 1.")
    apply_handoff.add_argument("--page-size", type=int, default=20, help="Table page size. Default: 20.")
    apply_handoff.add_argument("--out-dir", type=Path, help="Optional directory for the handoff panel JSON bundle.")
    apply_handoff.add_argument("--out", type=Path, help="Optional output JSON path.")
    apply_handoff.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    stateful_rebuild = subparsers.add_parser(
        "review-workbench-stateful-rebuild",
        help="Apply one non-executing Review Workbench UI intent and rebuild the next page-state bundle.",
    )
    stateful_rebuild.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    stateful_rebuild.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    stateful_rebuild.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    stateful_rebuild.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    stateful_rebuild.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    stateful_rebuild.add_argument("--reviewed-decision-plan-json", type=Path, help="Optional reviewed decision plan JSON.")
    stateful_rebuild.add_argument("--intent-json", type=Path, help="Optional Review Workbench update intent JSON.")
    stateful_rebuild.add_argument(
        "--intent-action",
        default="refresh_view",
        choices=["select_lane", "set_filter", "set_query", "set_sort", "set_page", "set_page_size", "reset_view", "refresh_view", "open_selected_lane", "disabled_apply"],
        help="Intent action to reduce before rebuilding. Default: refresh_view.",
    )
    stateful_rebuild.add_argument("--intent-lane", help="Lane id for a select_lane intent.")
    stateful_rebuild.add_argument("--intent-status", choices=["all", "needs_review", "ready", "empty"], help="Status for a set_filter intent.")
    stateful_rebuild.add_argument("--intent-query", help="Query for a set_query intent.")
    stateful_rebuild.add_argument("--intent-sort", help="Sort mode for a set_sort intent.")
    stateful_rebuild.add_argument("--intent-page", type=int, help="Page for a set_page intent.")
    stateful_rebuild.add_argument("--intent-page-size", type=int, help="Page size for a set_page_size intent.")
    stateful_rebuild.add_argument("--selected-lane", help="Initial selected review lane id.")
    stateful_rebuild.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Initial lane status filter. Default: all.")
    stateful_rebuild.add_argument("--lane-query", default="", help="Initial lane search query.")
    stateful_rebuild.add_argument("--lane-sort", default="attention_first", help="Initial lane sort mode. Default: attention_first.")
    stateful_rebuild.add_argument("--page", type=int, default=1, help="Initial table page. Default: 1.")
    stateful_rebuild.add_argument("--page-size", type=int, default=20, help="Initial table page size. Default: 20.")
    stateful_rebuild.add_argument("--out-dir", type=Path, help="Optional directory for the stateful rebuild JSON bundle.")
    stateful_rebuild.add_argument("--out", type=Path, help="Optional output JSON path.")
    stateful_rebuild.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    stateful_callbacks = subparsers.add_parser(
        "review-workbench-stateful-callbacks",
        help="Build or run the non-executing Qt callback-to-stateful-rebuild bridge for the Review Workbench.",
    )
    stateful_callbacks.add_argument("--duplicate-review-json", type=Path, help="Optional duplicate-review summary JSON.")
    stateful_callbacks.add_argument("--similar-images-json", type=Path, help="Optional similar-images summary JSON.")
    stateful_callbacks.add_argument("--decision-summary-json", type=Path, help="Optional decision-summary JSON.")
    stateful_callbacks.add_argument("--people-review-summary-json", type=Path, help="Optional people-review summary JSON.")
    stateful_callbacks.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    stateful_callbacks.add_argument("--reviewed-decision-plan-json", type=Path, help="Optional reviewed decision plan JSON.")
    stateful_callbacks.add_argument("--callback-intent-json", type=Path, help="Optional callback intent JSON. If omitted, the command returns the callback plan.")
    stateful_callbacks.add_argument("--callback-kind", help="Callback intent kind, for example filter_query_changed or lane_selected.")
    stateful_callbacks.add_argument("--callback-lane", help="Lane id for lane callback intents.")
    stateful_callbacks.add_argument("--callback-status", choices=["all", "needs_review", "ready", "empty"], help="Status for filter_status_changed.")
    stateful_callbacks.add_argument("--callback-query", help="Query for filter_query_changed.")
    stateful_callbacks.add_argument("--callback-sort", help="Sort mode for sort_mode_changed.")
    stateful_callbacks.add_argument("--selected-lane", help="Initial selected review lane id.")
    stateful_callbacks.add_argument("--lane-status", default="all", choices=["all", "needs_review", "ready", "empty"], help="Initial lane status filter. Default: all.")
    stateful_callbacks.add_argument("--lane-query", default="", help="Initial lane search query.")
    stateful_callbacks.add_argument("--lane-sort", default="attention_first", help="Initial lane sort mode. Default: attention_first.")
    stateful_callbacks.add_argument("--page", type=int, default=1, help="Initial table page. Default: 1.")
    stateful_callbacks.add_argument("--page-size", type=int, default=20, help="Initial table page size. Default: 20.")
    stateful_callbacks.add_argument("--out-dir", type=Path, help="Optional directory for the stateful callback plan JSON bundle.")
    stateful_callbacks.add_argument("--out", type=Path, help="Optional output JSON path.")
    stateful_callbacks.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace = subparsers.add_parser("workspace", help="Create, show, or update persisted GUI workspace state.")
    workspace_sub = workspace.add_subparsers(dest="workspace_command")

    workspace_init = workspace_sub.add_parser("init", help="Create a GUI state JSON file.")
    workspace_init.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_init.add_argument("--workspace-root", type=Path, help="Optional local workspace root.")
    workspace_init.add_argument("--overwrite", action="store_true", help="Overwrite an existing state file.")
    workspace_init.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_show = workspace_sub.add_parser("show", help="Show a GUI state JSON summary.")
    workspace_show.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_show.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_page = workspace_sub.add_parser("set-page", help="Set the active GUI page.")
    workspace_page.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_page.add_argument("--page-id", required=True, help="Active page id to store.")
    workspace_page.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_recent = workspace_sub.add_parser("add-recent", help="Add a path to a GUI recent-list section.")
    workspace_recent.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_recent.add_argument("--section", choices=["run_dirs", "profile_dirs", "people_bundle_dirs", "catalog_paths"], required=True)
    workspace_recent.add_argument("--path", required=True, help="Path to add.")
    workspace_recent.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_people = workspace_sub.add_parser("register-people-bundle", help="Remember a people review bundle in GUI state.")
    workspace_people.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_people.add_argument("--bundle-dir", type=Path, required=True, help="People review bundle directory.")
    workspace_people.add_argument("--catalog", type=Path, help="Optional people catalog path.")
    workspace_people.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    preview = subparsers.add_parser("people-review-preview", help="Preview people review apply without writing the catalog.")
    preview.add_argument("--catalog", type=Path, required=True, help="People catalog JSON path.")
    preview.add_argument("--workflow-json", type=Path, required=True, help="Edited people review workflow JSON.")
    preview.add_argument("--report-json", type=Path, required=True, help="Original people scan report JSON with encodings.")
    preview.add_argument("--out-catalog", type=Path, help="Optional output catalog path that review-apply would write.")
    preview.add_argument("--out", type=Path, help="Optional preview output JSON path.")
    preview.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    validate_bundle = subparsers.add_parser("validate-people-bundle", help="Validate a people review bundle directory for GUI use.")
    validate_bundle.add_argument("--bundle-dir", type=Path, required=True, help="People review bundle directory.")
    validate_bundle.add_argument("--out", type=Path, help="Optional validation output JSON path.")
    validate_bundle.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    command_plan = subparsers.add_parser("command-plan", help="Build non-executing GUI command plans.")
    command_plan_sub = command_plan.add_subparsers(dest="plan_command")

    plan_profile = command_plan_sub.add_parser("profile", help="Build a command plan from an app profile.")
    plan_profile.add_argument("profile", type=Path, help="App profile JSON path.")
    plan_profile.add_argument("--out", type=Path, help="Optional output JSON path.")
    plan_profile.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    plan_people_apply = command_plan_sub.add_parser("people-review-apply", help="Build a command plan for applying reviewed people.")
    plan_people_apply.add_argument("--catalog", type=Path, required=True)
    plan_people_apply.add_argument("--workflow-json", type=Path, required=True)
    plan_people_apply.add_argument("--report-json", type=Path, required=True)
    plan_people_apply.add_argument("--out-catalog", type=Path)
    plan_people_apply.add_argument("--dry-run", action="store_true")
    plan_people_apply.add_argument("--out", type=Path, help="Optional output JSON path.")
    plan_people_apply.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    plan_open_bundle = command_plan_sub.add_parser("open-people-bundle", help="Build a command plan for opening/validating a people review bundle.")
    plan_open_bundle.add_argument("--bundle-dir", type=Path, required=True)
    plan_open_bundle.add_argument("--out", type=Path, help="Optional output JSON path.")
    plan_open_bundle.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser


def _print_home_text(payload: dict[str, object]) -> None:
    profiles = payload.get("profiles", {})
    runs = payload.get("runs", {})
    print("Media Manager GUI home state")
    if isinstance(profiles, dict):
        summary = profiles.get("summary", {})
        if isinstance(summary, dict):
            print(f"  Profiles: {summary.get('profile_count', 0)}")
    if isinstance(runs, dict):
        summary = runs.get("summary", {})
        if isinstance(summary, dict):
            print(f"  Recent runs: {summary.get('run_count', 0)}")
    print(f"  Suggested next step: {payload.get('suggested_next_step')}")


def _print_report_bundle_text(payload: dict[str, object]) -> None:
    print("Report service bundle")
    print(f"  Command: {payload.get('command')}")
    print(f"  Service dir: {payload.get('service_dir')}")
    for path in payload.get("written_files", []):
        print(f"  - {path}")


def _print_pages_text(payload: dict[str, object]) -> None:
    catalog = payload.get("catalog", {})
    print("GUI page contracts")
    if isinstance(catalog, dict):
        print(f"  Pages: {catalog.get('page_count', 0)}")
        for page in catalog.get("pages", []):
            if isinstance(page, dict):
                print(f"  - {page.get('page_id')}: {page.get('title')}")


def _print_contracts_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("GUI app-service contracts")
    print(f"  Contracts: {payload.get('contract_count', 0)}")
    if isinstance(summary, dict):
        print(f"  Stable: {summary.get('stable_contract_count', 0)}")
        print(f"  Draft: {summary.get('draft_contract_count', 0)}")
        print(f"  Sensitive: {summary.get('sensitive_contract_count', 0)}")
    for contract in payload.get("contracts", []):
        if isinstance(contract, dict):
            print(f"  - {contract.get('contract_id')}: {contract.get('title')}")


def _print_contract_bindings_text(payload: dict[str, object]) -> None:
    print(summarize_gui_app_contract_bindings(payload))


def _print_preview_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("People review apply preview")
    print(f"  Status: {payload.get('status')}")
    print(f"  Safe to apply: {payload.get('safe_to_apply')}")
    if isinstance(summary, dict):
        print(f"  Ready groups: {summary.get('ready_group_count', 0)}")
        print(f"  Blocked groups: {summary.get('blocked_group_count', 0)}")
        print(f"  Embeddings to add: {summary.get('embeddings_added', 0)}")
    print(f"  Next action: {payload.get('next_action')}")


def _print_validation_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("People review bundle validation")
    print(f"  Status: {payload.get('status')}")
    print(f"  Ready for GUI: {payload.get('ready_for_gui')}")
    if isinstance(summary, dict):
        print(f"  Errors: {summary.get('error_count', 0)}")
        print(f"  Warnings: {summary.get('warning_count', 0)}")
        print(f"  Assets: {summary.get('asset_count', 0)}")
    print(f"  Next action: {payload.get('next_action')}")


def _print_workspace_text(payload: dict[str, object]) -> None:
    print("GUI workspace state")
    print(f"  Active page: {payload.get('active_page_id')}")
    print(f"  Workspace root: {payload.get('workspace_root')}")
    recent = payload.get("recent_counts", {})
    if isinstance(recent, dict):
        print(f"  Recent people bundles: {recent.get('people_bundle_dirs', 0)}")


def _print_command_plan_text(payload: dict[str, object]) -> None:
    print("GUI command plan")
    print(f"  ID: {payload.get('plan_id')}")
    print(f"  Title: {payload.get('title')}")
    print(f"  Enabled: {payload.get('enabled')}")
    print(f"  Risk: {payload.get('risk_level')}")
    print(f"  Command: {payload.get('command_preview')}")


def _print_desktop_runtime_text(payload: dict[str, object]) -> None:
    print(summarize_gui_desktop_runtime_state(payload))
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_ui_view_models_text(payload: dict[str, object]) -> None:
    print(summarize_ui_app_service_view_models(payload))
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_review_workbench_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench service bundle")
    if isinstance(summary, dict):
        print(f"  Lanes: {summary.get('lane_count', 0)}")
        print(f"  Needs review: {summary.get('attention_count', 0)}")
        print(f"  Selected lane: {summary.get('selected_lane_id')}")
        print(f"  Qt components: {summary.get('qt_component_count', 0)}")
        print(f"  Qt widget bindings: {summary.get('qt_widget_binding_count', 0)}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_widget_bindings_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench Qt widget bindings")
    if isinstance(summary, dict):
        print(f"  Widget bindings: {summary.get('widget_binding_count', 0)}")
        print(f"  Model bindings: {summary.get('model_binding_count', 0)}")
        print(f"  Action bindings: {summary.get('action_binding_count', 0)}")
        print(f"  Sensitive widgets: {summary.get('sensitive_widget_count', 0)}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_widget_skeleton_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench Qt widget skeleton")
    if isinstance(summary, dict):
        print(f"  Nodes: {summary.get('node_count', 0)}")
        print(f"  Model mounts: {summary.get('model_mount_count', 0)}")
        print(f"  Signal wires: {summary.get('signal_wire_count', 0)}")
        print(f"  Route wires: {summary.get('route_wire_count', 0)}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")




def _print_interactions_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench interactions")
    if isinstance(summary, dict):
        print(f"  Intents: {summary.get('intent_count', 0)}")
        print(f"  Signal bindings: {summary.get('signal_binding_count', 0)}")
        print(f"  Toolbar bindings: {summary.get('toolbar_binding_count', 0)}")
        print(f"  Route previews: {summary.get('route_preview_count', 0)}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_callback_mounts_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench callback mounts")
    if isinstance(summary, dict):
        print(f"  Callback mounts: {summary.get('callback_mount_count', 0)}")
        print(f"  Widget callbacks: {summary.get('widget_callback_mount_count', 0)}")
        print(f"  Toolbar callbacks: {summary.get('toolbar_callback_mount_count', 0)}")
        print(f"  Enabled callbacks: {summary.get('enabled_callback_mount_count', 0)}")
        print(f"  Route-deferred callbacks: {summary.get('route_deferred_callback_count', 0)}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_apply_preview_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench apply preview")
    if isinstance(summary, dict):
        print(f"  Selected lane: {summary.get('selected_lane_id')}")
        print(f"  Reviewed decisions: {summary.get('reviewed_decision_count', 0)}")
        print(f"  Candidate commands: {summary.get('candidate_command_count', 0)}")
        print(f"  Preview ready: {summary.get('preview_ready')}")
        print(f"  Apply enabled: {summary.get('apply_enabled')}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_confirmation_dialog_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    confirmation = payload.get("confirmation", {})
    print("GUI Review Workbench confirmation dialog")
    if isinstance(summary, dict):
        print(f"  Selected lane: {summary.get('selected_lane_id')}")
        print(f"  Risk level: {summary.get('risk_level')}")
        print(f"  Candidate commands: {summary.get('candidate_command_count', 0)}")
        print(f"  Required checks: {summary.get('required_satisfied_count', 0)}/{summary.get('required_check_count', 0)}")
        print(f"  Apply enabled: {summary.get('apply_enabled')}")
    if isinstance(confirmation, dict):
        print(f"  Confirmation phrase: {confirmation.get('phrase')}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_apply_executor_contract_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    gate = payload.get("confirmation_gate", {})
    print("GUI Review Workbench apply executor contract")
    if isinstance(summary, dict):
        print(f"  Selected lane: {summary.get('selected_lane_id')}")
        print(f"  Status: {summary.get('status')}")
        print(f"  Candidate commands: {summary.get('candidate_command_count', 0)}")
        print(f"  Typed confirmation matches: {summary.get('typed_confirmation_matches')}")
        print(f"  Execution enabled: {summary.get('execution_enabled')}")
    if isinstance(gate, dict):
        print(f"  Required phrase: {gate.get('phrase')}")
    if isinstance(readiness, dict):
        print(f"  Ready for future executor: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")



def _print_apply_handoff_panel_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench apply handoff panel")
    if isinstance(summary, dict):
        print(f"  Selected lane: {summary.get('selected_lane_id')}")
        print(f"  Status: {summary.get('status')}")
        print(f"  Executor status: {summary.get('executor_status')}")
        print(f"  Sections: {summary.get('section_count', 0)}")
        print(f"  Dry-run commands: {summary.get('dry_run_command_count', 0)}")
        print(f"  Failed preflight checks: {summary.get('preflight_failed_check_count', 0)}")
        print(f"  Execution enabled: {summary.get('execution_enabled')}")
    if isinstance(readiness, dict):
        print(f"  Ready/renderable: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_stateful_rebuild_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    transition = payload.get("transition", {})
    print("GUI Review Workbench stateful rebuild")
    if isinstance(summary, dict):
        print(f"  Intent action: {summary.get('intent_action')}")
        print(f"  Changed: {summary.get('changed')}")
        print(f"  Selected lane: {summary.get('selected_lane_id')}")
        print(f"  Table rows: {summary.get('table_row_count', 0)}")
        print(f"  Apply preview: {summary.get('apply_preview_status')}")
        print(f"  Confirmation dialog: {summary.get('confirmation_dialog_status')}")
        print(f"  Executes commands: {summary.get('executes_commands')}")
    if isinstance(transition, dict):
        print(f"  Rebuild required: {transition.get('rebuild_required')}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")

def _print_stateful_callbacks_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    readiness = payload.get("readiness", {})
    print("GUI Review Workbench stateful callbacks")
    if isinstance(summary, dict):
        print(f"  Callback kind: {summary.get('callback_intent_kind')}")
        print(f"  Rebuild action: {summary.get('rebuild_action')}")
        print(f"  Rebuild callbacks: {summary.get('page_rebuild_callback_count', 0)}")
        print(f"  Changed: {summary.get('changed')}")
        print(f"  Selected lane: {summary.get('selected_lane_id')}")
        print(f"  Executes commands: {summary.get('executes_commands')}")
    if isinstance(readiness, dict):
        print(f"  Ready: {readiness.get('ready')}")
        print(f"  Status: {readiness.get('status')}")
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")

def _emit(payload: dict[str, object], *, out: Path | None, json_output: bool, text_printer) -> None:
    if out is not None:
        write_json_object(out, payload)
    if json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        text_printer(payload)


def _workspace_summary_payload(state: dict[str, object]) -> dict[str, object]:
    return {**state, **build_gui_state_summary(state)}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.service_command or "home-state"

    if command == "home-state":
        payload = build_app_home_state(
            profile_dir=args.profile_dir,
            run_dir=args.run_dir,
            people_bundle_dir=args.people_bundle_dir,
            active_page_id=args.active_page,
            run_limit=args.run_limit,
        )
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_home_text)
        return 0

    if command == "startup-state":
        payload = build_app_startup_state(
            gui_state_path=args.gui_state,
            profile_dir=args.profile_dir,
            run_dir=args.run_dir,
            people_bundle_dir=args.people_bundle_dir,
            active_page_id=args.active_page,
        )
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_home_text)
        return 0

    if command == "desktop-runtime":
        try:
            if args.out_dir is not None:
                payload = write_gui_desktop_runtime_state(
                    args.out_dir,
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    settings_json=args.settings_json,
                    view_state_json=args.view_state_json,
                    language=args.language,
                    theme=args.theme,
                    density=args.density,
                )
            else:
                payload = build_gui_desktop_runtime_state(
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    settings_json=args.settings_json,
                    view_state_json=args.view_state_json,
                    language=args.language,
                    theme=args.theme,
                    density=args.density,
                )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_desktop_runtime_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2

    if command == "ui-view-models":
        try:
            if args.out_dir is not None:
                payload = write_ui_app_service_view_models(
                    args.out_dir,
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    language=args.language,
                )
            else:
                payload = build_ui_app_service_view_models(
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    language=args.language,
                )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_ui_view_models_text)
        return 0

    if command == "report-bundle":
        try:
            report_payload = read_json_object(args.report_json)
            command_payload = read_json_object(args.command_json) if args.command_json is not None else None
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = write_report_service_bundle(
            args.out_dir,
            command_name=args.command,
            report_payload=report_payload,
            command_payload=command_payload,
            run_id=args.run_id,
            entry_limit=args.entry_limit,
        )
        _emit(payload, out=None, json_output=args.json, text_printer=_print_report_bundle_text)
        return 0

    if command == "pages":
        payload = {"catalog": build_gui_page_catalog(), "navigation": build_gui_navigation_state(args.active_page)}
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_pages_text)
        return 0

    if command == "contracts":
        payload = build_app_contract_inventory()
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_contracts_text)
        return 0

    if command == "contract-bindings":
        payload = build_gui_app_contract_bindings()
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_contract_bindings_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2

    if command == "review-workbench":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            reviewed_decision_plan = read_json_object(args.reviewed_decision_plan_json) if args.reviewed_decision_plan_json is not None else None
            kwargs = {
                "duplicate_review": duplicate_review,
                "similar_images": similar_images,
                "decision_summary": decision_summary,
                "people_review_summary": people_review_summary,
                "people_bundle_dir": args.people_bundle_dir,
                "reviewed_decision_plan": reviewed_decision_plan,
                "selected_lane_id": args.selected_lane,
                "lane_status_filter": args.lane_status,
                "lane_query": args.lane_query,
                "lane_sort_mode": args.lane_sort,
                "page": args.page,
                "page_size": args.page_size,
            }
            if args.out_dir is not None:
                payload = write_gui_review_workbench_service_bundle(args.out_dir, **kwargs)
            else:
                payload = build_gui_review_workbench_service_bundle(**kwargs)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_review_workbench_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2

    if command == "review-workbench-widget-bindings":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            if args.out_dir is not None:
                payload = write_qt_review_workbench_widget_binding_plan(args.out_dir, service["qt_adapter_package"])
            else:
                payload = dict(service["qt_widget_binding_plan"])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_widget_bindings_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2

    if command == "review-workbench-widget-skeleton":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            if args.out_dir is not None:
                payload = write_qt_review_workbench_widget_skeleton(args.out_dir, service["qt_widget_binding_plan"])
            else:
                payload = dict(service["qt_widget_skeleton"])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_widget_skeleton_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2


    if command == "review-workbench-interactions":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            if args.out_dir is not None:
                payload = write_review_workbench_interaction_plan(args.out_dir, service)
            else:
                payload = dict(service["interaction_plan"])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_interactions_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2

    if command == "review-workbench-callback-mounts":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            if args.out_dir is not None:
                payload = write_review_workbench_callback_mount_plan(args.out_dir, service)
            else:
                payload = dict(service["callback_mount_plan"])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_callback_mounts_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2

    if command == "review-workbench-apply-preview":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            reviewed_decision_plan = read_json_object(args.reviewed_decision_plan_json) if args.reviewed_decision_plan_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                reviewed_decision_plan=reviewed_decision_plan,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            if args.out_dir is not None:
                payload = write_review_workbench_apply_preview(args.out_dir, service, reviewed_decision_plan=reviewed_decision_plan)
            else:
                payload = dict(service["apply_preview"])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_apply_preview_text)
        return 0 if payload.get("capabilities", {}).get("executes_commands") is False else 2

    if command == "review-workbench-confirmation-dialog":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            reviewed_decision_plan = read_json_object(args.reviewed_decision_plan_json) if args.reviewed_decision_plan_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                reviewed_decision_plan=reviewed_decision_plan,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            if args.out_dir is not None:
                payload = write_review_workbench_confirmation_dialog_model(args.out_dir, service["apply_preview"])
            else:
                payload = dict(service["confirmation_dialog"])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_confirmation_dialog_text)
        return 0 if payload.get("capabilities", {}).get("executes_commands") is False else 2

    if command == "review-workbench-apply-executor-contract":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            reviewed_decision_plan = read_json_object(args.reviewed_decision_plan_json) if args.reviewed_decision_plan_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                reviewed_decision_plan=reviewed_decision_plan,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            if args.out_dir is not None:
                payload = write_review_workbench_apply_executor_contract(
                    args.out_dir,
                    service["confirmation_dialog"],
                    typed_confirmation=args.typed_confirmation,
                    executor_enabled=args.executor_enabled,
                )
            else:
                payload = dict(service["apply_executor_contract"])
                if args.typed_confirmation or args.executor_enabled:
                    payload = build_review_workbench_apply_executor_contract(
                        service["confirmation_dialog"],
                        typed_confirmation=args.typed_confirmation,
                        executor_enabled=args.executor_enabled,
                    )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_apply_executor_contract_text)
        return 0 if payload.get("capabilities", {}).get("executes_commands") is False else 2


    if command == "review-workbench-apply-handoff-panel":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            reviewed_decision_plan = read_json_object(args.reviewed_decision_plan_json) if args.reviewed_decision_plan_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                reviewed_decision_plan=reviewed_decision_plan,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            executor_contract = service["apply_executor_contract"]
            if args.typed_confirmation or args.executor_enabled:
                executor_contract = build_review_workbench_apply_executor_contract(
                    service["confirmation_dialog"],
                    typed_confirmation=args.typed_confirmation,
                    executor_enabled=args.executor_enabled,
                )
            if args.out_dir is not None:
                payload = write_review_workbench_executor_handoff_panel(
                    args.out_dir,
                    service["confirmation_dialog"],
                    executor_contract,
                )
            else:
                payload = build_review_workbench_executor_handoff_panel(service["confirmation_dialog"], executor_contract)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_apply_handoff_panel_text)
        return 0 if payload.get("capabilities", {}).get("executes_commands") is False else 2

    if command == "review-workbench-stateful-rebuild":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            reviewed_decision_plan = read_json_object(args.reviewed_decision_plan_json) if args.reviewed_decision_plan_json is not None else None
            raw_intent = read_json_object(args.intent_json) if args.intent_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                reviewed_decision_plan=reviewed_decision_plan,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            intent = normalize_review_workbench_rebuild_intent(
                raw_intent,
                action=args.intent_action,
                lane_id=args.intent_lane,
                status=args.intent_status,
                query=args.intent_query,
                sort_mode=args.intent_sort,
                page=args.intent_page,
                page_size=args.intent_page_size,
            )
            if args.out_dir is not None:
                payload = write_review_workbench_stateful_rebuild_bundle(
                    args.out_dir,
                    service,
                    intent,
                    duplicate_review=duplicate_review,
                    similar_images=similar_images,
                    decision_summary=decision_summary,
                    people_review_summary=people_review_summary,
                    people_bundle_dir=args.people_bundle_dir,
                    reviewed_decision_plan=reviewed_decision_plan,
                )
            else:
                payload = build_review_workbench_stateful_rebuild_bundle(
                    service,
                    intent,
                    duplicate_review=duplicate_review,
                    similar_images=similar_images,
                    decision_summary=decision_summary,
                    people_review_summary=people_review_summary,
                    people_bundle_dir=args.people_bundle_dir,
                    reviewed_decision_plan=reviewed_decision_plan,
                )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_stateful_rebuild_text)
        return 0 if payload.get("capabilities", {}).get("executes_commands") is False else 2

    if command == "review-workbench-stateful-callbacks":
        try:
            duplicate_review = read_json_object(args.duplicate_review_json) if args.duplicate_review_json is not None else None
            similar_images = read_json_object(args.similar_images_json) if args.similar_images_json is not None else None
            decision_summary = read_json_object(args.decision_summary_json) if args.decision_summary_json is not None else None
            people_review_summary = read_json_object(args.people_review_summary_json) if args.people_review_summary_json is not None else None
            reviewed_decision_plan = read_json_object(args.reviewed_decision_plan_json) if args.reviewed_decision_plan_json is not None else None
            raw_callback = read_json_object(args.callback_intent_json) if args.callback_intent_json is not None else None
            service = build_gui_review_workbench_service_bundle(
                duplicate_review=duplicate_review,
                similar_images=similar_images,
                decision_summary=decision_summary,
                people_review_summary=people_review_summary,
                people_bundle_dir=args.people_bundle_dir,
                reviewed_decision_plan=reviewed_decision_plan,
                selected_lane_id=args.selected_lane,
                lane_status_filter=args.lane_status,
                lane_query=args.lane_query,
                lane_sort_mode=args.lane_sort,
                page=args.page,
                page_size=args.page_size,
            )
            callback_intent = raw_callback
            if callback_intent is None and args.callback_kind:
                callback_intent = {
                    "kind": "ui_review_workbench_interaction_intent",
                    "intent_kind": args.callback_kind,
                    "lane_id": args.callback_lane,
                    "status": args.callback_status,
                    "query": args.callback_query or "",
                    "sort_mode": args.callback_sort,
                    "executes_commands": False,
                    "executes_immediately": False,
                }
            if callback_intent is None:
                if args.out_dir is not None:
                    payload = write_review_workbench_stateful_callback_plan(args.out_dir, service)
                else:
                    payload = build_review_workbench_stateful_callback_plan(service)
            else:
                payload = build_review_workbench_stateful_callback_response(
                    service,
                    callback_intent,
                    duplicate_review=duplicate_review,
                    similar_images=similar_images,
                    decision_summary=decision_summary,
                    people_review_summary=people_review_summary,
                    people_bundle_dir=args.people_bundle_dir,
                    reviewed_decision_plan=reviewed_decision_plan,
                )
                if args.out_dir is not None:
                    args.out_dir.mkdir(parents=True, exist_ok=True)
                    write_json_object(args.out_dir / "review_workbench_stateful_callback_response.json", payload)
                    write_json_object(args.out_dir / "review_workbench_stateful_callback_normalized_intent.json", payload.get("normalized_rebuild_intent", {}))
                    write_json_object(args.out_dir / "review_workbench_stateful_callback_next_page_state.json", payload.get("next_page_state", {}))
                    write_json_object(args.out_dir / "review_workbench_stateful_callback_rebuild_bundle.json", payload.get("rebuild_bundle", {}))
                    readme = args.out_dir / "README.txt"
                    readme.write_text(
                        "Review Workbench stateful callback response\n"
                        "Applies one non-executing Qt callback intent through the stateful rebuild loop and writes the next page-state payload.\n",
                        encoding="utf-8",
                    )
                    payload = {
                        **payload,
                        "output_dir": str(args.out_dir),
                        "written_files": [
                            str(args.out_dir / "review_workbench_stateful_callback_response.json"),
                            str(args.out_dir / "review_workbench_stateful_callback_normalized_intent.json"),
                            str(args.out_dir / "review_workbench_stateful_callback_next_page_state.json"),
                            str(args.out_dir / "review_workbench_stateful_callback_rebuild_bundle.json"),
                            str(readme),
                        ],
                        "written_file_count": 5,
                    }
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_stateful_callbacks_text)
        return 0 if payload.get("capabilities", {}).get("executes_commands") is False else 2

    if command == "workspace":
        workspace_command = args.workspace_command or "show"
        if workspace_command == "init":
            if args.state_json.exists() and not args.overwrite:
                parser.error(f"GUI state already exists: {args.state_json}")
            state = build_default_gui_state(workspace_root=args.workspace_root)
            write_gui_state(args.state_json, state)
            payload = _workspace_summary_payload(state)
            _emit(payload, out=None, json_output=args.json, text_printer=_print_workspace_text)
            return 0
        try:
            state = load_gui_state(args.state_json)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        if workspace_command == "show":
            payload = _workspace_summary_payload(state)
            _emit(payload, out=None, json_output=args.json, text_printer=_print_workspace_text)
            return 0
        if workspace_command == "set-page":
            state = set_active_page(state, args.page_id)
        elif workspace_command == "add-recent":
            state = add_recent_path(state, section=args.section, path=args.path)
        elif workspace_command == "register-people-bundle":
            state = register_people_bundle(state, bundle_dir=args.bundle_dir, catalog_path=args.catalog)
        else:
            parser.error(f"Unsupported workspace command: {workspace_command}")
        write_gui_state(args.state_json, state)
        payload = _workspace_summary_payload(state)
        _emit(payload, out=None, json_output=args.json, text_printer=_print_workspace_text)
        return 0

    if command == "people-review-preview":
        try:
            workflow_payload = read_json_object(args.workflow_json)
            report_payload = read_json_object(args.report_json)
            payload = build_people_review_apply_preview(
                catalog_path=args.catalog,
                workflow_payload=workflow_payload,
                report_payload=report_payload,
                output_catalog_path=args.out_catalog,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        if args.out is not None:
            write_people_review_apply_preview(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_preview_text(payload)
        return 0 if payload.get("status") == "ok" else 1

    if command == "validate-people-bundle":
        payload = validate_people_review_bundle(args.bundle_dir)
        if args.out is not None:
            write_people_review_bundle_validation(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_validation_text(payload)
        return 0 if payload.get("status") == "ok" else 1

    if command == "command-plan":
        plan_command = args.plan_command or "profile"
        try:
            if plan_command == "profile":
                payload = build_profile_command_plan(args.profile)
            elif plan_command == "people-review-apply":
                payload = build_people_review_apply_command_plan(
                    catalog_path=args.catalog,
                    workflow_json=args.workflow_json,
                    report_json=args.report_json,
                    out_catalog=args.out_catalog,
                    dry_run=args.dry_run,
                )
            elif plan_command == "open-people-bundle":
                payload = build_open_people_bundle_plan(args.bundle_dir)
            else:
                parser.error(f"Unsupported command-plan command: {plan_command}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        if args.out is not None:
            write_command_plan(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_command_plan_text(payload)
        return 0 if payload.get("enabled", True) else 1

    parser.error(f"Unsupported app service command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
