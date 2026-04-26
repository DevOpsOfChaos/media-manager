from media_manager.core.gui_error_boundary import build_error_boundary, build_gui_error, error_from_exception


def test_error_boundary_counts_blocking_errors() -> None:
    payload = build_error_boundary([
        build_gui_error("a", "A", recoverable=True),
        build_gui_error("b", "B", recoverable=False),
    ])

    assert payload["error_count"] == 2
    assert payload["blocking_count"] == 1
    assert payload["can_continue"] is False


def test_error_from_exception_is_safe_message() -> None:
    err = error_from_exception(ValueError("bad input"))

    assert err["code"] == "unexpected_error"
    assert "ValueError" in err["message"]
