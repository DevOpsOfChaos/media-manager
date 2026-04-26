from media_manager.core.gui_log_stream_model import append_log_entry, build_log_entry, build_log_stream


def test_log_stream_counts_errors() -> None:
    stream = build_log_stream([build_log_entry("ok"), build_log_entry("bad", level="error")])
    assert stream["entry_count"] == 2
    assert stream["has_errors"] is True


def test_append_log_entry() -> None:
    stream = append_log_entry(build_log_stream(), "queued", level="info", job_id="j1")
    assert stream["entries"][0]["job_id"] == "j1"
