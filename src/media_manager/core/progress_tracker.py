"""Shared progress tracker — usable by CLI (console output) and GUI (progress bar)."""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass(slots=True)
class ProgressPhase:
    """A named phase with a percentage range of the total operation."""
    name: str
    start_pct: int   # inclusive
    end_pct: int     # exclusive


# Callback signature: (phase_name: str, overall_pct: int, message: str, elapsed: float, eta: float)
ProgressCallback = Callable[[str, int, str, float, float], None] | None


class ProgressTracker:
    """Tracks progress through named phases with percentage interpolation.

    Usage:
        tracker = ProgressTracker([
            ProgressPhase("scanning", 0, 10),
            ProgressPhase("resolving_dates", 10, 50),
            ProgressPhase("building_plan", 50, 80),
            ProgressPhase("executing", 80, 98),
            ProgressPhase("done", 98, 100),
        ])
        tracker.enter_phase("scanning", "Discovering media files...")
        for i, file in enumerate(files):
            tracker.tick(i / len(files), f"File {i+1}/{len(files)}")
        tracker.enter_phase("done", "Complete")
    """

    def __init__(self, phases: list[ProgressPhase] | None = None, *,
                 on_update: ProgressCallback = None,
                 throttle_ms: int = 80):
        self.phases: list[ProgressPhase] = list(phases) if phases else []
        self._on_update = on_update
        self._throttle_ms = throttle_ms
        self._current_idx: int = -1
        self._start_time: float = time.time()
        self._last_emit: float = 0.0
        self._current_total: int = 0   # set when known
        self._current_done: int = 0

    # ── phase navigation ──

    def enter_phase(self, name: str, message: str = "") -> None:
        """Move to the named phase and emit its start percentage."""
        for i, ph in enumerate(self.phases):
            if ph.name == name:
                self._current_idx = i
                self._emit(name, ph.start_pct, message)
                return
        # Phase not found — stay at current position
        self._emit(name, self.overall_pct, message)

    def tick(self, fraction: float, message: str = ""):
        """Report progress within the current phase. fraction 0.0–1.0."""
        if self._current_idx < 0:
            return
        ph = self.phases[self._current_idx]
        f = min(1.0, max(0.0, fraction))
        pct = int(ph.start_pct + (ph.end_pct - ph.start_pct) * f)
        self._emit(ph.name, pct, message)

    def tick_count(self, done: int, total: int, message: str = ""):
        """Convenience: tick with absolute counts (done/total) rather than fraction."""
        self._current_total = max(1, total)
        self._current_done = min(total, max(0, done))
        self.tick(self._current_done / self._current_total, message)

    def done(self, message: str = ""):
        """Mark as 100% complete. Jumps to the last phase's end_pct."""
        if self.phases:
            last = self.phases[-1]
            self._current_idx = len(self.phases) - 1
            self._emit(last.name, last.end_pct, message)
        else:
            self._emit("done", 100, message)

    # ── computed properties ──

    @property
    def overall_pct(self) -> int:
        if self._current_idx < 0:
            return 0
        return self.phases[self._current_idx].start_pct

    @property
    def elapsed(self) -> float:
        return time.time() - self._start_time

    @property
    def eta(self) -> float:
        """Estimated seconds remaining based on current phase progress."""
        pct = max(1, self.overall_pct)
        if pct >= 100 or self._current_done <= 0:
            return 0.0
        return (self.elapsed / pct) * (100 - pct)

    @property
    def current_phase_name(self) -> str:
        if self._current_idx < 0:
            return ""
        return self.phases[self._current_idx].name

    # ── internal ──

    def _emit(self, phase_name: str, pct: int, message: str):
        now = time.time()
        # Throttle: skip if emitted recently (unless phase change or 100%)
        if self._last_emit > 0 and pct < 100 and (now - self._last_emit) < (self._throttle_ms / 1000.0):
            return
        self._last_emit = now
        if self._on_update:
            self._on_update(phase_name, pct, message, self.elapsed, self.eta)

    # ── predefined phase sets ──

    @classmethod
    def for_organize_plan(cls) -> "ProgressTracker":
        return cls([
            ProgressPhase("scanning",          0,  5),
            ProgressPhase("resolving_dates",   5, 55),
            ProgressPhase("building_plan",    55, 70),
            ProgressPhase("resolving_conflicts", 70, 75),
            ProgressPhase("done",             75, 100),
        ])

    @classmethod
    def for_organize_execute(cls, plan_total: int = 0) -> "ProgressTracker":
        _ = plan_total
        return cls([
            ProgressPhase("creating_dirs",    0,  2),
            ProgressPhase("moving_files",     2, 95),
            ProgressPhase("cleaning_up",     95, 98),
            ProgressPhase("done",            98, 100),
        ])


# ── console (CLI) progress display ──

def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}m{s:02d}s"


def console_progress_callback(phase_name: str, pct: int, message: str,
                               elapsed: float, eta: float) -> None:
    """Render a one-line progress bar to stderr. Suitable for CLI use."""
    bar_width = 30
    filled = int(bar_width * pct / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    elapsed_str = _format_duration(elapsed)
    eta_str = _format_duration(eta) if eta > 0 else "..."
    line = f"\r{bar} {pct:3d}% | {message[:50]:<50} | {elapsed_str} elapsed | ~{eta_str} remaining"
    # Pad to terminal width to clear previous content
    line = line.ljust(120)
    sys.stderr.write(line)
    sys.stderr.flush()


def console_progress_done(message: str = "") -> None:
    """Print a newline-terminated completion line."""
    sys.stderr.write(f"\r{'✓ ' + message if message else '✓ Done'}\n")
    sys.stderr.flush()
