from media_manager.core.gui_model_index import build_gui_model_index, summarize_gui_model_index


def test_model_index_lists_models() -> None:
    index = build_gui_model_index({"a": {"kind": "model_a", "schema_version": "1.0", "x": 1}})

    assert index["model_count"] == 1
    assert index["entries"][0]["kind"] == "model_a"
    assert summarize_gui_model_index(index) == "1 GUI models indexed"
