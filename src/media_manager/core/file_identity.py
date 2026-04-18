from __future__ import annotations

from pathlib import Path


def files_have_same_size(first_path: Path, second_path: Path) -> bool:
    try:
        return first_path.stat().st_size == second_path.stat().st_size
    except OSError:
        return False


def files_have_identical_content(first_path: Path, second_path: Path, *, chunk_size: int = 1024 * 1024) -> bool:
    if not files_have_same_size(first_path, second_path):
        return False
    try:
        with first_path.open("rb") as first_handle, second_path.open("rb") as second_handle:
            while True:
                first_chunk = first_handle.read(chunk_size)
                second_chunk = second_handle.read(chunk_size)
                if first_chunk != second_chunk:
                    return False
                if not first_chunk:
                    return True
    except OSError:
        return False
