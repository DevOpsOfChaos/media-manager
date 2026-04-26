from media_manager.core.gui_qt_demo_workspace import build_demo_shell_model
from media_manager.core.gui_qt_product_surface import build_product_surface, validate_product_surface
from media_manager.core.gui_qt_release_smoke_pack import build_release_smoke_pack, validate_release_smoke_pack


def test_release_smoke_pack_is_safe() -> None:
    pack = build_release_smoke_pack(shell_model=build_demo_shell_model())
    assert pack["scenario_count"] >= 4
    assert pack["privacy_sensitive_count"] >= 1
    assert validate_release_smoke_pack(pack)["valid"] is True


def test_product_surface_combines_visible_surface_parts() -> None:
    surface = build_product_surface(build_demo_shell_model(), language="de", density="comfortable")
    assert surface["kind"] == "qt_product_surface"
    assert surface["executes_commands"] is False
    assert surface["summary"]["command_count"] >= 5
    assert validate_product_surface(surface)["valid"] is True
