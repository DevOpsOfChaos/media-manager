from __future__ import annotations

import sys


def cli_progress(current: int, total: int, label: str = "") -> None:
    if total <= 0:
        return
    pct = current / total * 100
    bar_width = 40
    filled = int(bar_width * current / total)
    bar = "\u2588" * filled + "\u2591" * (bar_width - filled)
    sys.stderr.write(f"\r{label} [{bar}] {pct:.0f}%")
    sys.stderr.flush()


def cli_progress_done(label: str = "") -> None:
    sys.stderr.write(f"\r{label} {' ' * 20}\n")
    sys.stderr.flush()
