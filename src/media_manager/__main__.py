import sys

from media_manager.cli import main as cli_main


def _run_gui() -> int:
    try:
        from media_manager.gui import main as gui_main
    except ModuleNotFoundError as exc:
        if exc.name == "tkinter":
            print(
                "Tkinter is not available in this Python installation.\n"
                "Use the CLI for now or install a Python build with Tcl/Tk support.\n\n"
                "CLI example:\n"
                "  python -m media_manager organize <SOURCE> <TARGET> --apply --copy\n"
            )
            return 2
        raise
    return gui_main()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(_run_gui())
    raise SystemExit(cli_main())
