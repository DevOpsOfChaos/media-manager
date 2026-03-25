from __future__ import annotations

import sys

from media_manager.cli import main as cli_main
from media_manager.gui import main as gui_main


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(gui_main())
    raise SystemExit(cli_main())
