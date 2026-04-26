from media_manager.core.gui_qt_release_checklist import build_qt_release_checklist


def test_release_checklist_requires_backend_tests_pages_and_performance() -> None:
    checklist = build_qt_release_checklist(
        backend_available=True,
        tests_green=True,
        page_readiness={"blocked_count": 0},
        performance={"ok": True},
        localization={"ok": False},
    )
    assert checklist["ready_for_manual_smoke"] is True
    assert checklist["passed_required_count"] == checklist["required_count"]
    localization = next(item for item in checklist["items"] if item["id"] == "localization")
    assert localization["required"] is False
