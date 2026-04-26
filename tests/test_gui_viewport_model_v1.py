from media_manager.core.gui_viewport_model import choose_column_count, normalize_density, normalize_viewport


def test_viewport_normalizes_breakpoint_and_density() -> None:
    viewport = normalize_viewport(width=1440, height=900, density="spacious")

    assert viewport["breakpoint"] == "lg"
    assert viewport["orientation"] == "landscape"
    assert viewport["density"] == "spacious"
    assert choose_column_count(viewport, item_count=3) == 3


def test_viewport_clamps_invalid_values() -> None:
    viewport = normalize_viewport({"width": 1, "height": 2, "density": "weird"})

    assert viewport["width"] == 320
    assert viewport["height"] == 240
    assert normalize_density("weird") == "comfortable"
