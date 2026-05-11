from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_INVENTORY_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class AppServiceContract:
    contract_id: str
    title: str
    description: str
    producer_commands: tuple[str, ...]
    consumer_surfaces: tuple[str, ...]
    required_inputs: tuple[str, ...] = ()
    produced_artifacts: tuple[str, ...] = ()
    optional_artifacts: tuple[str, ...] = ()
    safety_level: str = "safe"
    executes_media_operations: bool = False
    writes_app_state: bool = False
    requires_user_confirmation: bool = False
    headless_testable: bool = True
    gui_stability: str = "stable"

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "title": self.title,
            "description": self.description,
            "producer_commands": list(self.producer_commands),
            "consumer_surfaces": list(self.consumer_surfaces),
            "required_inputs": list(self.required_inputs),
            "produced_artifacts": list(self.produced_artifacts),
            "optional_artifacts": list(self.optional_artifacts),
            "safety_level": self.safety_level,
            "executes_media_operations": self.executes_media_operations,
            "writes_app_state": self.writes_app_state,
            "requires_user_confirmation": self.requires_user_confirmation,
            "headless_testable": self.headless_testable,
            "gui_stability": self.gui_stability,
        }


_CONTRACTS: tuple[AppServiceContract, ...] = (
    AppServiceContract(
        contract_id="app_manifest",
        title="App capability manifest",
        description="Machine-readable command capabilities, options, risk levels, supported formats, and run artifact expectations.",
        producer_commands=("media-manager app manifest --json", "media-manager-app manifest --json"),
        consumer_surfaces=("dashboard", "new-run", "profiles", "settings"),
        produced_artifacts=("app_manifest.json",),
        safety_level="safe",
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="home_state",
        title="GUI home state",
        description="Aggregated dashboard state from profiles, recent run folders, page contracts, and optional people review bundle metadata.",
        producer_commands=("media-manager app-services home-state --json", "media-manager-app-services home-state --json"),
        consumer_surfaces=("dashboard", "run-history", "profiles", "people-review"),
        required_inputs=("profile_dir?", "run_dir?", "people_bundle_dir?"),
        produced_artifacts=("service_home_state.json",),
        safety_level="safe",
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="startup_state",
        title="GUI startup state",
        description="First-load state for a desktop shell, combining persisted GUI state, navigation, page contracts, dashboard state, and people-bundle validation.",
        producer_commands=("media-manager app-services startup-state --json",),
        consumer_surfaces=("desktop-shell", "dashboard"),
        required_inputs=("gui_state?", "profile_dir?", "run_dir?", "people_bundle_dir?"),
        produced_artifacts=("startup_state.json",),
        optional_artifacts=("gui_state.json",),
        safety_level="safe",
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="report_service_bundle",
        title="Report service bundle",
        description="Derived GUI artifacts for one command report: compact UI state, plan snapshot, action model, and bundle metadata.",
        producer_commands=("media-manager app-services report-bundle --json",),
        consumer_surfaces=("run-history", "review-workbench", "decision-summary"),
        required_inputs=("report.json", "command.json?"),
        produced_artifacts=("ui_state.json", "plan_snapshot.json", "action_model.json", "service_bundle.json"),
        safety_level="safe",
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="ui_view_models",
        title="UI app-service view models",
        description="Headless view models for dashboard, scan setup, duplicate review, similar images, decision summary, run history, and review workbench pages.",
        producer_commands=("media-manager app-services ui-view-models --json",),
        consumer_surfaces=("dashboard", "new-run", "run-history", "review-workbench"),
        required_inputs=("home_state_json?", "profile_dir?", "run_dir?", "people_bundle_dir?"),
        produced_artifacts=("ui_view_models.json",),
        optional_artifacts=("home.json", "scan_setup.json", "duplicate_review.json", "similar_images.json", "decision_summary.json", "run_history.json", "review_workbench.json"),
        safety_level="safe",
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="review_workbench_service",
        title="Review Workbench service bundle",
        description="Headless Qt-ready Review Workbench bundle with lanes, table model, controller state, action plan, guarded Qt workbench, adapter descriptors, Qt widget bindings, a lazy widget skeleton, local interaction intents, concrete callback mounts, a non-executing apply preview contract, a guarded confirmation dialog model, a disabled-by-default apply executor contract, and a display-only confirmation/executor handoff panel, and a stateful page rebuild loop.",
        producer_commands=(
            "media-manager app-services review-workbench --json",
            "media-manager app-services review-workbench-widget-bindings --json",
            "media-manager app-services review-workbench-widget-skeleton --json",
            "media-manager app-services review-workbench-interactions --json",
            "media-manager app-services review-workbench-callback-mounts --json",
            "media-manager app-services review-workbench-apply-preview --json",
            "media-manager app-services review-workbench-confirmation-dialog --json",
            "media-manager app-services review-workbench-apply-executor-contract --json",
            "media-manager app-services review-workbench-apply-handoff-panel --json",
            "media-manager app-services review-workbench-stateful-rebuild --json",
        ),
        consumer_surfaces=("review-workbench", "run-history", "people-review", "desktop-shell"),
        required_inputs=("duplicate_review_json?", "similar_images_json?", "decision_summary_json?", "people_bundle_dir?"),
        produced_artifacts=(
            "review_workbench_service_bundle.json",
            "review_workbench_view_model.json",
            "review_workbench_table_model.json",
            "review_workbench_controller_state.json",
            "review_workbench_action_plan.json",
            "review_workbench_qt_workbench.json",
            "review_workbench_qt_adapter_package.json",
            "review_workbench_qt_widget_binding_plan.json",
            "review_workbench_qt_widget_skeleton.json",
            "review_workbench_interaction_plan.json",
            "review_workbench_callback_mount_plan.json",
            "review_workbench_apply_preview.json",
            "review_workbench_confirmation_dialog_model.json",
            "review_workbench_apply_executor_contract.json",
            "review_workbench_apply_executor_handoff_panel.json",
            "review_workbench_stateful_rebuild_loop.json",
        ),
        safety_level="safe",
        requires_user_confirmation=True,
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="review_workbench_apply_preview",
        title="Review Workbench apply preview",
        description="Non-executing reviewed command-plan preview for Review Workbench apply actions. It never performs media operations and remains confirmation-gated.",
        producer_commands=("media-manager app-services review-workbench-apply-preview --json",),
        consumer_surfaces=("review-workbench", "decision-summary", "desktop-shell"),
        required_inputs=("review_workbench_service_bundle?", "reviewed_decision_plan_json?"),
        produced_artifacts=("review_workbench_apply_preview.json", "review_workbench_reviewed_command_plan_preview.json"),
        safety_level="medium",
        requires_user_confirmation=True,
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="review_workbench_confirmation_dialog",
        title="Review Workbench confirmation dialog",
        description="Guarded non-executing confirmation dialog model for reviewed Review Workbench apply previews. It renders required checks, risk summary, and typed confirmation requirements without executing commands.",
        producer_commands=("media-manager app-services review-workbench-confirmation-dialog --json",),
        consumer_surfaces=("review-workbench", "desktop-shell"),
        required_inputs=("review_workbench_apply_preview?", "reviewed_decision_plan_json?"),
        produced_artifacts=("review_workbench_confirmation_dialog_model.json", "review_workbench_confirmation_checklist.json"),
        safety_level="medium",
        requires_user_confirmation=True,
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="review_workbench_apply_executor_contract",
        title="Review Workbench apply executor contract",
        description="Disabled-by-default dry-run executor boundary for a future reviewed apply path. It formalizes preflight, audit, and mutation policies without executing commands.",
        producer_commands=("media-manager app-services review-workbench-apply-executor-contract --json",),
        consumer_surfaces=("review-workbench", "decision-summary", "desktop-shell"),
        required_inputs=("review_workbench_confirmation_dialog?", "reviewed_decision_plan_json?"),
        produced_artifacts=(
            "review_workbench_apply_executor_contract.json",
            "review_workbench_apply_executor_preflight.json",
            "review_workbench_apply_executor_audit_plan.json",
            "review_workbench_apply_dry_run_execution_plan.json",
        ),
        safety_level="medium",
        requires_user_confirmation=True,
        gui_stability="draft",
    ),

    AppServiceContract(
        contract_id="review_workbench_apply_handoff_panel",
        title="Review Workbench apply handoff panel",
        description="Display-only GUI panel model that renders confirmation, preflight, dry-run plan, and audit metadata before any future executor can exist.",
        producer_commands=("media-manager app-services review-workbench-apply-handoff-panel --json",),
        consumer_surfaces=("review-workbench", "desktop-shell"),
        required_inputs=("review_workbench_confirmation_dialog?", "review_workbench_apply_executor_contract?"),
        produced_artifacts=(
            "review_workbench_apply_executor_handoff_panel.json",
            "review_workbench_apply_handoff_preflight.json",
            "review_workbench_apply_handoff_dry_run_plan.json",
            "review_workbench_apply_handoff_audit_plan.json",
        ),
        safety_level="medium",
        requires_user_confirmation=True,
        gui_stability="draft",
    ),
    AppServiceContract(
        contract_id="review_workbench_stateful_rebuild",
        title="Review Workbench stateful rebuild loop",
        description="Headless reducer/rebuild contract that applies one local UI intent and returns the next Review Workbench page-state bundle without writing app state or executing commands.",
        producer_commands=("media-manager app-services review-workbench-stateful-rebuild --json",),
        consumer_surfaces=("review-workbench", "desktop-shell"),
        required_inputs=("review_workbench_service_bundle?", "ui_intent?"),
        produced_artifacts=(
            "review_workbench_stateful_rebuild.json",
            "review_workbench_rebuild_transition.json",
            "review_workbench_next_service_bundle.json",
            "review_workbench_next_page_state.json",
            "review_workbench_next_interaction_plan.json",
        ),
        safety_level="safe",
        requires_user_confirmation=False,
        gui_stability="draft",
    ),
    AppServiceContract(
        contract_id="desktop_runtime",
        title="Desktop runtime state",
        description="Headless runtime payload for a future Qt desktop shell, including settings, visible pages, readiness, state, and view-model summaries.",
        producer_commands=("media-manager app-services desktop-runtime --json",),
        consumer_surfaces=("desktop-shell", "dashboard", "review-workbench"),
        required_inputs=("home_state_json?", "settings_json?", "view_state_json?"),
        produced_artifacts=("desktop_runtime.json",),
        safety_level="safe",
        gui_stability="draft",
    ),
    AppServiceContract(
        contract_id="workspace_state",
        title="Persisted GUI workspace state",
        description="Small local state file for active page, recent paths, and selected people-review bundle references.",
        producer_commands=(
            "media-manager app-services workspace init",
            "media-manager app-services workspace set-page",
            "media-manager app-services workspace add-recent",
            "media-manager app-services workspace register-people-bundle",
        ),
        consumer_surfaces=("desktop-shell", "dashboard", "people-review"),
        required_inputs=("state_json",),
        produced_artifacts=("gui_state.json",),
        safety_level="safe",
        writes_app_state=True,
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="people_review_bundle",
        title="People review bundle",
        description="Local-only, GUI-ready review workspace for unknown-face groups, face assets, and review decisions.",
        producer_commands=("media-manager people --bundle-dir <dir>", "media-manager app-services validate-people-bundle --json"),
        consumer_surfaces=("people-review", "review-workbench"),
        required_inputs=("people_report.json", "people_review_workflow.json", "people_review_workspace.json"),
        produced_artifacts=("bundle_manifest.json", "people_review_workspace.json", "people_review_workflow.json"),
        optional_artifacts=("assets/people_review_assets.json", "assets/faces/*.jpg", "people_report.json"),
        safety_level="sensitive",
        requires_user_confirmation=True,
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="people_review_apply_preview",
        title="People review apply preview",
        description="Non-destructive preview of people-review decisions before any catalog write is allowed.",
        producer_commands=("media-manager app-services people-review-preview --json",),
        consumer_surfaces=("people-review", "decision-summary"),
        required_inputs=("catalog", "workflow_json", "report_json"),
        produced_artifacts=("people_review_apply_preview.json",),
        safety_level="sensitive",
        requires_user_confirmation=True,
        gui_stability="stable",
    ),
    AppServiceContract(
        contract_id="command_plan",
        title="Non-executing command plan",
        description="GUI command preview contract for profiles and people-review actions. It never executes media operations.",
        producer_commands=(
            "media-manager app-services command-plan profile",
            "media-manager app-services command-plan people-review-apply",
            "media-manager app-services command-plan open-people-bundle",
        ),
        consumer_surfaces=("new-run", "profiles", "people-review", "decision-summary"),
        required_inputs=("profile_json?", "bundle_dir?", "catalog?", "workflow_json?", "report_json?"),
        produced_artifacts=("command_plan.json",),
        safety_level="medium",
        requires_user_confirmation=True,
        gui_stability="stable",
    ),
)


_BOUNDARY_RULES: tuple[str, ...] = (
    "GUI surfaces must consume app-service contracts or run artifacts; they must not parse human console output.",
    "GUI apply actions must be represented as command plans or action models before execution is allowed.",
    "Destructive media operations remain preview/apply flows with explicit confirmation and journal/undo artifacts where supported.",
    "People recognition data is local-only and must be treated as sensitive biometric metadata.",
    "CLI and GUI must share core/application logic; duplicated GUI-only business rules are a regression.",
)


def list_app_service_contracts() -> list[AppServiceContract]:
    return list(_CONTRACTS)


def build_app_contract_inventory() -> dict[str, object]:
    contracts = [contract.to_dict() for contract in _CONTRACTS]
    sensitive = [contract for contract in _CONTRACTS if contract.safety_level == "sensitive"]
    destructive = [contract for contract in _CONTRACTS if contract.executes_media_operations]
    writable = [contract for contract in _CONTRACTS if contract.writes_app_state]
    stable = [contract for contract in _CONTRACTS if contract.gui_stability == "stable"]
    return {
        "schema_version": CONTRACT_INVENTORY_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "kind": "app_contract_inventory",
        "contract_count": len(contracts),
        "contracts": contracts,
        "summary": {
            "stable_contract_count": len(stable),
            "draft_contract_count": len(_CONTRACTS) - len(stable),
            "sensitive_contract_count": len(sensitive),
            "destructive_contract_count": len(destructive),
            "writes_app_state_count": len(writable),
            "headless_testable_count": sum(1 for contract in _CONTRACTS if contract.headless_testable),
        },
        "boundary_rules": list(_BOUNDARY_RULES),
        "next_gui_step": "Wire one guarded desktop page to these contracts before adding new GUI-only behavior.",
    }


def write_app_contract_inventory(path: str | Path) -> dict[str, object]:
    import json

    payload = build_app_contract_inventory()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**payload, "written_file": str(output_path)}


__all__ = [
    "AppServiceContract",
    "CONTRACT_INVENTORY_SCHEMA_VERSION",
    "build_app_contract_inventory",
    "list_app_service_contracts",
    "write_app_contract_inventory",
]
