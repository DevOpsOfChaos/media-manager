"""Persistent ExifTool process using -stay_open mode for massive speedup.

The -stay_open mode avoids spawning a new subprocess for every batch, but
may not work with all ExifTool distributions (e.g. standalone Windows .exe
sometimes fails to flush JSON output).  This module auto-detects whether
stay_open is functional and permanently disables itself if not.
"""
from __future__ import annotations
import json
import logging
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_STARTUP_TIMEOUT = 2.0

class PersistentExifTool:
    """Manages a persistent ExifTool process for repeated metadata queries."""

    def __init__(self, exiftool_path: Path | None = None):
        from media_manager.exiftool import resolve_exiftool_path
        self._exe = resolve_exiftool_path(exiftool_path)
        self._proc: subprocess.Popen | None = None
        self._last_used = 0.0
        self._available: bool | None = None

    def _verify_responsive(self) -> bool:
        """Send a real metadata request through stay_open and check we get {ready}."""
        if self._proc is None:
            return False
        result: list[bool] = [False]
        def _check():
            try:
                self._proc.stdin.write("-ver\n-execute\n")
                self._proc.stdin.flush()
                while True:
                    line = self._proc.stdout.readline()
                    if not line:
                        return
                    if line.strip() == "{ready}":
                        break
                result[0] = True
            except Exception:
                return
        t = threading.Thread(target=_check, daemon=True)
        t.start()
        t.join(timeout=_STARTUP_TIMEOUT)
        if t.is_alive():
            return False
        return result[0]

    def _verify_json_output(self) -> bool:
        """Send a JSON read for a temporary file and check for valid JSON + {ready}."""
        if self._proc is None:
            return False
        result: list[bool] = [False]
        def _check():
            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    tmp.write(b"\xff\xd8\xff\xe0")
                    tmp_path = tmp.name
                try:
                    cmd = f"-json\n-s\n--\n{tmp_path}\n-execute\n"
                    self._proc.stdin.write(cmd)
                    self._proc.stdin.flush()
                    output_lines: list[str] = []
                    while True:
                        line = self._proc.stdout.readline()
                        if not line:
                            return
                        if line.strip() == "{ready}":
                            break
                        output_lines.append(line)
                    data = json.loads("".join(output_lines))
                    if isinstance(data, list):
                        result[0] = True
                finally:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
            except Exception:
                return
        t = threading.Thread(target=_check, daemon=True)
        t.start()
        t.join(timeout=_STARTUP_TIMEOUT)
        if t.is_alive():
            return False
        return result[0]

    def start(self) -> bool:
        if self._available is False:
            return False
        if self._proc is not None:
            return True
        if self._exe is None:
            self._available = False
            return False
        try:
            self._proc = subprocess.Popen(
                [str(self._exe), "-stay_open", "True", "-@", "-"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, encoding="utf-8",
            )
            if not self._verify_responsive():
                logger.debug("Persistent ExifTool not responding (ver check) — disabling")
                self._cleanup_proc()
                self._available = False
                return False
            if not self._verify_json_output():
                logger.debug("Persistent ExifTool JSON output check failed — disabling")
                self._cleanup_proc()
                self._available = False
                return False
            self._available = True
            self._last_used = time.time()
            logger.info("Persistent ExifTool started and verified")
            return True
        except Exception as e:
            logger.warning("Failed to start persistent ExifTool: %s", e)
            self._available = False
            return False

    def _cleanup_proc(self):
        if self._proc:
            try:
                self._proc.kill()
            except Exception:
                pass
            self._proc = None

    def _send_and_read(self, cmd: str, timeout_seconds: float = 120.0) -> str | None:
        if not self._proc:
            return None
        try:
            self._proc.stdin.write(cmd)
            self._proc.stdin.flush()

            result_lines: list[str] = []
            deadline = time.time() + timeout_seconds
            while time.time() < deadline:
                line = self._proc.stdout.readline()
                if not line:
                    break
                if line.strip() == "{ready}":
                    self._last_used = time.time()
                    return "".join(result_lines)
                result_lines.append(line)
            logger.debug("Persistent ExifTool read timed out after %.0fs", timeout_seconds)
            return None
        except Exception as e:
            logger.debug("Persistent ExifTool query failed: %s", e)
            return None

    def read_metadata(self, file_path: Path) -> dict[str, object] | None:
        if not self.start():
            return None
        raw = self._send_and_read(
            f"-json\n-G0:1\n-s\n-time:all\n--\n{file_path}\n-execute\n"
        )
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            return data[0] if isinstance(data, list) and data else {}
        except (json.JSONDecodeError, IndexError):
            return {}

    def read_metadata_batch(self, file_paths: list[Path]) -> dict[Path, dict[str, object]]:
        if not self.start():
            return {}
        cmd_parts = ["-json", "-G0:1", "-s", "-time:all", "--"]
        cmd_parts.extend(str(p) for p in file_paths)
        cmd_parts.append("-execute\n")
        raw = self._send_and_read("\n".join(cmd_parts))
        if raw is None:
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        result: dict[Path, dict[str, object]] = {}
        if isinstance(data, list):
            for item in data:
                src = item.get("SourceFile", "")
                if src:
                    result[Path(src)] = item
        return result

    def close(self):
        if self._proc:
            try:
                self._proc.stdin.write("-stay_open\nFalse\n")
                self._proc.stdin.flush()
                self._proc.wait(timeout=5)
            except Exception:
                self._proc.kill()
            self._proc = None

    @property
    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def keepalive(self, max_idle: float = 300):
        if self._proc and time.time() - self._last_used > max_idle:
            self.close()


_persistent_instance: PersistentExifTool | None = None

def get_persistent_exiftool() -> PersistentExifTool:
    global _persistent_instance
    if _persistent_instance is None:
        _persistent_instance = PersistentExifTool()
    return _persistent_instance
