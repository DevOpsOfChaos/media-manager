"""Runtime diagnostics bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_diagnostics

Output: JSON on stdout. Errors: JSON on stderr.
Reports Python version, import health, and settings path status.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit

logger = logging.getLogger(__name__)


def get_gpu_diagnostics() -> dict:
    """Report GPU availability for face recognition."""
    info = {
        "cuda": False,
        "openvino": False,
        "opencv_dnn": False,
        "opencv_version": None,
        "recommendation": "CPU-only mode",
    }

    try:
        import cv2
        cv2_version = cv2.__version__
        info["opencv_dnn"] = True
        info["opencv_version"] = cv2_version

        try:
            net = cv2.dnn.readNetFromONNX("dummy")
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            info["cuda"] = True
            info["recommendation"] = "CUDA GPU available"
        except (cv2.error, OSError, RuntimeError):
            pass

        try:
            net = cv2.dnn.readNetFromONNX("dummy")
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
            info["openvino"] = True
            if not info["cuda"]:
                info["recommendation"] = "OpenVINO available"
        except (cv2.error, OSError, RuntimeError):
            pass
    except ImportError:
        info["recommendation"] = "OpenCV not installed"

    return info


def _check_import(module_name: str) -> dict:
    try:
        __import__(module_name)
        return {"ok": True}
    except ImportError as exc:
        return {"ok": False, "error": str(exc)}


def _get_system_diagnostics() -> dict:
    """Collect system-level info: disk space, CPU count."""
    info = {}
    try:
        import multiprocessing
        info["cpu_count"] = multiprocessing.cpu_count()
    except Exception:
        info["cpu_count"] = None

    try:
        home = Path.home()
        usage = shutil.disk_usage(home)
        info["disk_free_gb"] = round(usage.free / (1024 ** 3), 1)
        info["disk_total_gb"] = round(usage.total / (1024 ** 3), 1)
    except Exception:
        info["disk_free_gb"] = None
        info["disk_total_gb"] = None

    return info


def _get_exiftool_version(exiftool_path: str | None = None) -> str | None:
    """Get ExifTool version string."""
    import subprocess
    cmd = [exiftool_path or "exiftool", "-ver"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def cmd_diagnostics() -> int:
    """Collect runtime diagnostics: Python version, imports, settings, GPU support."""
    logger.info("Diagnostics: starting")
    py_version = sys.version

    mm_import = _check_import("media_manager")
    bs_import = _check_import("media_manager.bridge_settings")

    # Resolve settings path (same logic as bridge_settings)
    from media_manager.bridge_settings import _resolve_settings_path
    settings_path = _resolve_settings_path()

    result = {
        "python_version": py_version,
        "media_manager_import": mm_import,
        "bridge_settings_import": bs_import,
        "settings_path": str(settings_path),
        "settings_file_exists": settings_path.is_file(),
        "gpu": get_gpu_diagnostics(),
        "system": _get_system_diagnostics(),
        "exiftool_version": _get_exiftool_version(),
    }
    _emit(result)
    logger.info("Diagnostics: complete")
    return 0


def main(argv: list[str] | None = None) -> int:
    return cmd_diagnostics()


if __name__ == "__main__":
    raise SystemExit(main())
