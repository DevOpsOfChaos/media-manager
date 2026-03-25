from __future__ import annotations


def main() -> int:
    try:
        from media_manager.gui_workflow import main as gui_main
    except ModuleNotFoundError as exc:
        if exc.name == "PySide6":
            print(
                "PySide6 is not available in this Python installation.\n"
                "Install project dependencies again and then retry the GUI.\n\n"
                "Example:\n"
                "  pip install -e .[dev]\n\n"
                "CLI example:\n"
                "  python -m media_manager organize --source <SOURCE> --target <TARGET> --apply --copy\n"
            )
            return 2
        raise
    return gui_main()
