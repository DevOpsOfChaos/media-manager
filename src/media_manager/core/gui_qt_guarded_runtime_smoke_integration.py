from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_desktop_integration_plan import build_qt_desktop_integration_plan
from .gui_qt_runtime_bootstrap_plan import build_qt_runtime_bootstrap_plan
from .gui_qt_runtime_handoff_manifest import build_qt_runtime_handoff_manifest
from .gui_qt_runtime_launch_contract import build_qt_runtime_launch_contract
from .gui_qt_runtime_manual_smoke_plan import build_qt_runtime_manual_smoke_plan
from .gui_qt_runtime_readiness_report import build_qt_runtime_readiness_report
from .gui_qt_runtime_smoke_adapter_bundle import build_qt_runtime_smoke_adapter_bundle
from .gui_qt_runtime_smoke_artifacts import build_qt_runtime_smoke_artifact_manifest
from .gui_qt_runtime_smoke_command_palette_binding import build_qt_runtime_smoke_command_palette_binding
from .gui_qt_runtime_smoke_dashboard import build_qt_runtime_smoke_dashboard
from .gui_qt_runtime_smoke_decision import build_qt_runtime_smoke_decision
from .gui_qt_runtime_smoke_desktop_acceptance_bundle import build_qt_runtime_smoke_desktop_acceptance_bundle
from .gui_qt_runtime_smoke_desktop_launch_dry_run import build_qt_runtime_smoke_desktop_launch_dry_run
from .gui_qt_runtime_smoke_desktop_rehearsal_bundle import build_qt_runtime_smoke_desktop_rehearsal_bundle
from .gui_qt_runtime_smoke_desktop_result_bundle import build_qt_runtime_smoke_desktop_result_bundle
from .gui_qt_runtime_smoke_desktop_start_bundle import build_qt_runtime_smoke_desktop_start_bundle
from .gui_qt_runtime_smoke_guarded_snapshot import build_qt_runtime_smoke_guarded_snapshot
from .gui_qt_runtime_smoke_guardrails import evaluate_qt_runtime_smoke_guardrails
from .gui_qt_runtime_smoke_integration_bundle import build_qt_runtime_smoke_integration_bundle
from .gui_qt_runtime_smoke_manual_readiness import build_qt_runtime_smoke_manual_readiness
from .gui_qt_runtime_smoke_page_handoff import build_qt_runtime_smoke_page_handoff
from .gui_qt_runtime_smoke_page_model import build_qt_runtime_smoke_page_model
from .gui_qt_runtime_smoke_qt_backend_probe import build_qt_runtime_smoke_qt_backend_probe
from .gui_qt_runtime_smoke_report import build_qt_runtime_smoke_report
from .gui_qt_runtime_smoke_route_resolver import resolve_qt_runtime_smoke_route
from .gui_qt_runtime_smoke_shell_action_registry import build_qt_runtime_smoke_shell_action_registry
from .gui_qt_runtime_smoke_shell_bundle import build_qt_runtime_smoke_shell_bundle
from .gui_qt_runtime_smoke_toolbar_binding import build_qt_runtime_smoke_toolbar_binding
from .gui_qt_runtime_smoke_visible_surface import build_qt_runtime_smoke_visible_surface
from .gui_qt_runtime_smoke_wiring_bundle import build_qt_runtime_smoke_wiring_bundle
from .gui_qt_runtime_smoke_workbench import build_qt_runtime_smoke_workbench

QT_GUARDED_RUNTIME_SMOKE_INTEGRATION_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _language(shell_model: Mapping[str, Any]) -> str:
    return "de" if str(shell_model.get("language") or "en").lower() == "de" else "en"


def _theme(shell_model: Mapping[str, Any]) -> str:
    theme = _mapping(shell_model.get("theme"))
    return str(theme.get("theme") or shell_model.get("theme") or "modern-dark")


def _density(shell_model: Mapping[str, Any]) -> str:
    layout = _mapping(shell_model.get("layout"))
    return str(layout.get("density") or "comfortable")


def _existing_pages(shell_model: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    pages: list[Mapping[str, Any]] = []
    for raw in _list(shell_model.get("navigation")):
        if isinstance(raw, Mapping):
            pages.append({"page_id": raw.get("id") or raw.get("page_id"), "label": raw.get("label"), "enabled": raw.get("enabled", True)})
    return pages


def _existing_routes(shell_model: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    router = _mapping(shell_model.get("router"))
    routes = [item for item in _list(router.get("routes")) if isinstance(item, Mapping)]
    if routes:
        return routes
    return [{"route_id": item.get("page_id"), "page_id": item.get("page_id")} for item in _existing_pages(shell_model)]


def build_guarded_qt_runtime_smoke_integration(
    shell_model: Mapping[str, Any],
    *,
    results: Mapping[str, bool] | list[Mapping[str, Any]] | None = None,
    history_entries: list[Mapping[str, Any]] | None = None,
    reviewer: str = "",
) -> dict[str, object]:
    """Build the full guarded Runtime Smoke route integration without opening Qt."""

    lang = _language(shell_model)
    theme = _theme(shell_model)
    desktop_plan = build_qt_desktop_integration_plan(shell_model)
    bootstrap_plan = build_qt_runtime_bootstrap_plan(desktop_plan)
    readiness_report = build_qt_runtime_readiness_report(bootstrap_plan)
    handoff_manifest = build_qt_runtime_handoff_manifest(readiness_report)
    launch_contract = build_qt_runtime_launch_contract(handoff_manifest, language=lang, theme=theme)
    manual_smoke_plan = build_qt_runtime_manual_smoke_plan(handoff_manifest, language=lang)
    smoke_report = build_qt_runtime_smoke_report(handoff_manifest, launch_contract, manual_smoke_plan, results or {}, reviewer=reviewer)
    artifact_manifest = build_qt_runtime_smoke_artifact_manifest(
        {
            "readiness_report": readiness_report,
            "handoff_manifest": handoff_manifest,
            "launch_contract": launch_contract,
            "manual_smoke_plan": manual_smoke_plan,
            "smoke_report": smoke_report,
        },
        root_dir=".media-manager/runtime-smoke",
    )
    dashboard = build_qt_runtime_smoke_dashboard(
        current_report=smoke_report,
        history=history_entries or [],
        artifact_manifest=artifact_manifest,
    )
    decision = build_qt_runtime_smoke_decision(dashboard)
    workbench = build_qt_runtime_smoke_workbench(dashboard, decision, language=lang)
    page_model = build_qt_runtime_smoke_page_model(workbench, {"actions": []})
    visible_surface = build_qt_runtime_smoke_visible_surface(page_model, density=_density(shell_model))
    adapter_bundle = build_qt_runtime_smoke_adapter_bundle(visible_surface)
    page_handoff = build_qt_runtime_smoke_page_handoff(adapter_bundle, existing_pages=_existing_pages(shell_model))
    shell_bundle = build_qt_runtime_smoke_shell_bundle(page_handoff, existing_navigation_items=_list(shell_model.get("navigation")))
    integration_bundle = build_qt_runtime_smoke_integration_bundle(
        adapter_bundle=adapter_bundle,
        page_handoff=page_handoff,
        shell_bundle=shell_bundle,
    )
    wiring_bundle = build_qt_runtime_smoke_wiring_bundle(
        integration_bundle,
        shell_bundle,
        existing_routes=_existing_routes(shell_model),
    )
    command_palette_binding = build_qt_runtime_smoke_command_palette_binding(shell_bundle)
    toolbar_binding = build_qt_runtime_smoke_toolbar_binding(shell_bundle)
    action_registry = build_qt_runtime_smoke_shell_action_registry(
        page_model=page_model,
        shell_bundle=shell_bundle,
        command_palette_binding=command_palette_binding,
    )
    page_model = {
        **page_model,
        "actions": list(action_registry.get("actions", [])),
        "summary": {
            **dict(_mapping(page_model.get("summary"))),
            "action_count": _mapping(action_registry.get("summary")).get("action_count", 0),
        },
    }
    visible_surface = build_qt_runtime_smoke_visible_surface(page_model, density=_density(shell_model))
    adapter_bundle = build_qt_runtime_smoke_adapter_bundle(visible_surface)
    page_handoff = build_qt_runtime_smoke_page_handoff(adapter_bundle, existing_pages=_existing_pages(shell_model))
    shell_bundle = build_qt_runtime_smoke_shell_bundle(page_handoff, existing_navigation_items=_list(shell_model.get("navigation")))
    integration_bundle = build_qt_runtime_smoke_integration_bundle(
        adapter_bundle=adapter_bundle,
        page_handoff=page_handoff,
        shell_bundle=shell_bundle,
    )
    wiring_bundle = build_qt_runtime_smoke_wiring_bundle(
        integration_bundle,
        shell_bundle,
        existing_routes=_existing_routes(shell_model),
    )
    rehearsal_bundle = build_qt_runtime_smoke_desktop_rehearsal_bundle(wiring_bundle, language=lang, theme=theme)
    start_bundle = build_qt_runtime_smoke_desktop_start_bundle(rehearsal_bundle, language=lang)
    result_bundle = build_qt_runtime_smoke_desktop_result_bundle(results or [])
    acceptance_bundle = build_qt_runtime_smoke_desktop_acceptance_bundle(
        result_bundle,
        start_bundle,
        history_entries=history_entries,
    )
    backend_probe = build_qt_runtime_smoke_qt_backend_probe()
    dry_run = build_qt_runtime_smoke_desktop_launch_dry_run(
        wiring_bundle=wiring_bundle,
        rehearsal_bundle=rehearsal_bundle,
        start_bundle=start_bundle,
        backend_probe=backend_probe,
    )
    manual_readiness = build_qt_runtime_smoke_manual_readiness(
        dry_run=dry_run,
        start_bundle=start_bundle,
        acceptance_bundle=acceptance_bundle,
    )
    route_resolution = resolve_qt_runtime_smoke_route(
        {
            "page_model": page_model,
            "visible_surface": visible_surface,
            "page_handoff": page_handoff,
            "wiring_bundle": wiring_bundle,
        }
    )
    guardrails = evaluate_qt_runtime_smoke_guardrails(
        desktop_plan,
        bootstrap_plan,
        readiness_report,
        handoff_manifest,
        launch_contract,
        manual_smoke_plan,
        page_model,
        visible_surface,
        adapter_bundle,
        page_handoff,
        shell_bundle,
        integration_bundle,
        wiring_bundle,
        rehearsal_bundle,
        start_bundle,
        dry_run,
        manual_readiness,
    )
    ready_for_shell_route = (
        bool(route_resolution.get("ready"))
        and bool(page_handoff.get("ready_for_shell_registration"))
        and bool(shell_bundle.get("ready_for_shell"))
        and bool(wiring_bundle.get("ready_for_guarded_shell_wiring"))
        and bool(guardrails.get("valid"))
    )
    bundle: dict[str, object] = {
        "schema_version": QT_GUARDED_RUNTIME_SMOKE_INTEGRATION_SCHEMA_VERSION,
        "kind": "guarded_qt_runtime_smoke_integration",
        "page_id": "runtime-smoke",
        "language": lang,
        "desktop_plan": desktop_plan,
        "bootstrap_plan": bootstrap_plan,
        "readiness_report": readiness_report,
        "handoff_manifest": handoff_manifest,
        "launch_contract": launch_contract,
        "manual_smoke_plan": manual_smoke_plan,
        "smoke_report": smoke_report,
        "artifact_manifest": artifact_manifest,
        "dashboard": dashboard,
        "decision": decision,
        "workbench": workbench,
        "page_model": page_model,
        "visible_surface": visible_surface,
        "adapter_bundle": adapter_bundle,
        "page_handoff": page_handoff,
        "shell_bundle": shell_bundle,
        "integration_bundle": integration_bundle,
        "wiring_bundle": wiring_bundle,
        "command_palette_binding": command_palette_binding,
        "toolbar_binding": toolbar_binding,
        "action_registry": action_registry,
        "rehearsal_bundle": rehearsal_bundle,
        "start_bundle": start_bundle,
        "result_bundle": result_bundle,
        "acceptance_bundle": acceptance_bundle,
        "backend_probe": backend_probe,
        "dry_run": dry_run,
        "manual_readiness": manual_readiness,
        "route_resolution": route_resolution,
        "guardrails": guardrails,
        "ready_for_shell_route": ready_for_shell_route,
        "summary": {
            "ready_for_shell_route": ready_for_shell_route,
            "ready_to_start_manual_smoke": manual_readiness.get("ready_to_start_manual_smoke"),
            "accepted_after_results": manual_readiness.get("accepted_after_results"),
            "problem_count": int(_mapping(guardrails.get("summary")).get("problem_count") or 0)
            + int(_mapping(adapter_bundle.get("summary")).get("problem_count") or 0)
            + int(_mapping(wiring_bundle.get("summary")).get("problem_count") or 0),
            "action_count": _mapping(action_registry.get("summary")).get("action_count", 0),
            "command_palette_item_count": _mapping(command_palette_binding.get("summary")).get("item_count", 0),
            "toolbar_button_count": _mapping(toolbar_binding.get("summary")).get("button_count", 0),
            "route_resolved": route_resolution.get("resolved"),
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }
    bundle["snapshot"] = build_qt_runtime_smoke_guarded_snapshot(bundle)
    return bundle


def build_guarded_qt_runtime_smoke_page_model(shell_model: Mapping[str, Any]) -> dict[str, object]:
    return dict(build_guarded_qt_runtime_smoke_integration(shell_model).get("page_model", {}))


__all__ = [
    "QT_GUARDED_RUNTIME_SMOKE_INTEGRATION_SCHEMA_VERSION",
    "build_guarded_qt_runtime_smoke_integration",
    "build_guarded_qt_runtime_smoke_page_model",
]
