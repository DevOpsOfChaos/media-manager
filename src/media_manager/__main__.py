from __future__ import annotations

import sys

from media_manager.cli import main as cli_main


def _run_gui() -> int:
    try:
        from media_manager.gui import main as gui_main
    except ModuleNotFoundError as exc:
        if exc.name == "tkinter":
            print(
                "Tkinter ist in dieser Python-Installation nicht verfügbar.\n"
                "Nutze vorerst die CLI oder installiere eine Python-Version mit Tcl/Tk-Unterstützung.\n\n"
                "CLI-Beispiel:\n"
                "  python -m media_manager organize <QUELLE> <ZIEL> --apply --copy\n"
            )
            return 2
        raise
    return gui_main()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(_run_gui())
    raise SystemExit(cli_main())
