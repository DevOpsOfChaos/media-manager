import os
import subprocess
import sys
from pathlib import Path


def open_file(path: Path | str) -> None:
    p = Path(path)
    if sys.platform == "win32":
        os.startfile(str(p))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(p)], check=False)
    else:
        subprocess.run(["xdg-open", str(p)], check=False)


def reveal_in_explorer(path: Path | str) -> None:
    p = Path(path)
    if sys.platform == "win32":
        subprocess.run(["explorer", "/select,", str(p)], check=False)
    elif sys.platform == "darwin":
        subprocess.run(["open", "-R", str(p)], check=False)
    else:
        subprocess.run(["xdg-open", str(p.parent)], check=False)


def get_app_data_dir() -> Path:
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        if xdg:
            return Path(xdg)
        return Path.home() / ".local" / "share"
