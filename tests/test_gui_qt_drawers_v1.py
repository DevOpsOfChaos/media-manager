from media_manager.core.gui_qt_diagnostics_drawer import build_qt_diagnostics_drawer
from media_manager.core.gui_qt_notification_drawer import build_qt_notification_drawer


def test_notification_drawer_prioritizes_errors() -> None:
    drawer = build_qt_notification_drawer([{"level": "info", "message": "ok"}, {"level": "error", "message": "bad"}])
    assert drawer["has_errors"] is True
    assert drawer["items"][0]["level"] == "error"


def test_diagnostics_drawer_reports_status() -> None:
    drawer = build_qt_diagnostics_drawer([{"severity": "warning", "message": "check"}])
    assert drawer["status"] == "warning"
    assert drawer["warning_count"] == 1
