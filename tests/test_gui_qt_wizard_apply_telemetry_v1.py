from media_manager.core.gui_qt_people_apply_bar import build_people_apply_bar
from media_manager.core.gui_qt_telemetry_snapshot import build_local_telemetry_snapshot
from media_manager.core.gui_qt_wizard_validation import validate_new_run_wizard


def test_wizard_validation_blocks_apply_and_warns_for_encodings() -> None:
    result = validate_new_run_wizard({"command": "people", "sources": ["D:/Photos"], "include_encodings": True, "apply": True})

    assert result["valid"] is False
    assert result["warning_count"] == 1
    assert result["problem_count"] == 1


def test_people_apply_bar_requires_confirmation() -> None:
    audit = {"summary": {"ready_group_count": 2, "blocked_group_count": 0, "embedding_count": 10}}
    blocked = build_people_apply_bar(audit, confirmation_acknowledged=False)
    enabled = build_people_apply_bar(audit, confirmation_acknowledged=True)

    assert blocked["apply_enabled"] is False
    assert enabled["apply_enabled"] is True
    assert enabled["executes_immediately"] is False


def test_telemetry_snapshot_is_local_and_privacy_safe() -> None:
    snap = build_local_telemetry_snapshot(shell_model={"active_page_id": "dashboard", "language": "de", "theme": {"theme": "modern-dark"}, "page": {"kind": "dashboard_page"}})

    assert snap["privacy"]["local_only"] is True
    assert snap["privacy"]["network_transmission"] is False
    assert snap["shell"]["active_page_id"] == "dashboard"
