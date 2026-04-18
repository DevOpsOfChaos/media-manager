from __future__ import annotations


LEGACY_GUI_NOTICE = (
    "Legacy notice: the desktop GUI is not the active product direction during the repository reset.\n"
    "It remains available only as an explicit legacy surface while the new core-first foundation is rebuilt.\n"
)


def main() -> int:
    print(LEGACY_GUI_NOTICE)
    try:
        from media_manager.gui_workflow import main as gui_main
    except ModuleNotFoundError as exc:
        if exc.name == "PySide6":
            print(
                "PySide6 is not available in this Python installation.\n"
                "Install the optional GUI dependencies and then retry the legacy GUI.\n\n"
                "Example:\n"
                "  pip install -e .[gui,dev]\n\n"
                "Core-first CLI examples:\n"
                "  python -m media_manager organize --source <SOURCE> --target <TARGET> --apply --copy\n"
                "  python -m media_manager rename --source <SOURCE>\n"
            )
            return 2
        raise
    return gui_main()
