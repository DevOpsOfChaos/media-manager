from __future__ import annotations

import time
from contextlib import contextmanager
from logging import Logger


@contextmanager
def timer(label: str, logger: Logger | None = None):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    if logger:
        logger.info("%s took %.2fs", label, elapsed)
