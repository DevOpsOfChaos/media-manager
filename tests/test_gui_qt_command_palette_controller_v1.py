from media_manager.core.gui_qt_command_palette_controller import build_qt_command_palette_controller, filter_palette_commands


def test_command_palette_filters_and_clamps_selection() -> None:
    commands = [
        {"id": "open_people", "label": "Open people review", "page_id": "people-review"},
        {"id": "open_runs", "label": "Open run history", "page_id": "run-history"},
    ]
    assert len(filter_palette_commands(commands, "people")) == 1
    model = build_qt_command_palette_controller(commands, query="open", selected_index=99)
    assert model["row_count"] == 2
    assert model["selected_index"] == 1
    assert model["selected_command"]["id"] == "open_runs"
