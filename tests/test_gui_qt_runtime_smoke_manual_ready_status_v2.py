from __future__ import annotations

from media_manager.core.gui_qt_runtime_handoff_manifest import build_qt_runtime_handoff_manifest
from media_manager.core.gui_qt_runtime_launch_contract import build_qt_runtime_launch_contract
from media_manager.core.gui_qt_runtime_manual_smoke_plan import build_qt_runtime_manual_smoke_plan
from media_manager.core.gui_qt_runtime_readiness_report import build_qt_runtime_readiness_report
from media_manager.core.gui_qt_runtime_smoke_artifacts import build_qt_runtime_smoke_artifact_manifest
from media_manager.core.gui_qt_runtime_smoke_dashboard import build_qt_runtime_smoke_dashboard
from media_manager.core.gui_qt_runtime_smoke_decision import build_qt_runtime_smoke_decision
from media_manager.core.gui_qt_runtime_smoke_report import build_qt_runtime_smoke_report
from media_manager.core.gui_qt_runtime_smoke_status import build_qt_runtime_smoke_status_badge


def _ready_runtime_inputs() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    readiness = build_qt_runtime_readiness_report(
        {
            "kind": "qt_runtime_bootstrap_plan",
            "active_page_id": "runtime-smoke",
            "ready_for_runtime": True,
            "summary": {"blocking_problem_count": 0},
            "capabilities": {
                "requires_pyside6": False,
                "opens_window": False,
                "headless_testable": True,
                "executes_commands": False,
                "local_only": True,
            },
        }
    )
    handoff = build_qt_runtime_handoff_manifest(readiness)
    launch = build_qt_runtime_launch_contract(handoff)
    manual = build_qt_runtime_manual_smoke_plan(handoff)
    return handoff, launch, manual


def test_smoke_report_separates_manual_launch_readiness_from_evidence_gate() -> None:
    handoff, launch, manual = _ready_runtime_inputs()

    report = build_qt_runtime_smoke_report(handoff, launch, manual, {})

    summary = report["summary"]
    assert summary["ready_for_manual_smoke"] is True
    assert summary["ready_for_release_gate"] is False
    assert summary["evidence_complete"] is False
    assert summary["missing_required_count"] == 4
    assert summary["incomplete_privacy_check_count"] == 1
    assert summary["blocking_problem_count"] == 0


def test_status_badge_marks_missing_only_manual_evidence_as_ready_to_start() -> None:
    handoff, launch, manual = _ready_runtime_inputs()
    report = build_qt_runtime_smoke_report(handoff, launch, manual, {})

    badge = build_qt_runtime_smoke_status_badge(report, label="Current smoke")

    assert badge["state"] == "ready"
    assert badge["text"] == "Ready for manual smoke"
    assert badge["ready"] is True
    assert badge["ready_for_manual_smoke"] is True
    assert badge["evidence_complete"] is False
    assert badge["problem_count"] == 0
    assert badge["missing_required_count"] == 4


def test_dashboard_and_decision_are_ready_for_manual_smoke_before_results() -> None:
    handoff, launch, manual = _ready_runtime_inputs()
    report = build_qt_runtime_smoke_report(handoff, launch, manual, {})
    artifacts = build_qt_runtime_smoke_artifact_manifest({"smoke_report": report}, root_dir=".media-manager/runtime-smoke")

    dashboard = build_qt_runtime_smoke_dashboard(
        current_report=report,
        history=[],
        artifact_manifest=artifacts,
    )
    decision = build_qt_runtime_smoke_decision(dashboard)

    assert dashboard["summary"]["blocked_badge_count"] == 0
    assert dashboard["summary"]["ready_to_start_manual_smoke"] is True
    assert dashboard["summary"]["evidence_complete"] is False
    assert dashboard["ready_for_runtime_review"] is True
    assert decision["decision"] == "ready_for_manual_qt_smoke"
    assert decision["severity"] == "success"
    assert "evidence is still pending" in decision["recommended_next_step"]
