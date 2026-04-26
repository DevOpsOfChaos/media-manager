from media_manager.core.gui_status_footer_model import build_status_footer


def test_status_footer_reports_warning_state() -> None:
    footer = build_status_footer(active_page_id="people-review", diagnostics={"warning_count": 1})

    assert footer["kind"] == "status_footer"
    assert footer["status"] == "warning"
    assert footer["safe_mode"] is True
