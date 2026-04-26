from media_manager.core.gui_qt_demo_workspace import build_demo_shell_model
from media_manager.core.gui_qt_localization_surface import build_localization_surface, merge_localization_surfaces
from media_manager.core.gui_qt_model_fixture_pack import build_model_fixture_pack, get_fixture


def test_localization_surface_and_fixtures() -> None:
    surface = build_localization_surface(build_demo_shell_model(), language="de")
    assert surface["string_count"] > 0
    merged = merge_localization_surfaces(surface)
    assert merged["string_count"] == surface["string_count"]

    pack = build_model_fixture_pack()
    assert pack["fixture_count"] == 3
    assert get_fixture("people_page")["page_id"] == "people-review"
