"""Doctor bridge for the Tauri desktop app.

Reads doctor options JSON from stdin.
Runs preflight checks on source/target directories.
Output: doctor report JSON on stdout. Errors: JSON on stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from media_manager.core.doctor import DoctorOptions, build_doctor_report


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_check() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON doctor options.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    try:
        options = DoctorOptions(
            command=payload.get("command", "general"),
            source_dirs=tuple(Path(p) for p in payload.get("source_dirs", [])),
            target_root=Path(payload["target_root"]) if payload.get("target_root") else None,
            recursive=payload.get("recursive", True),
            include_hidden=payload.get("include_hidden", False),
            follow_symlinks=payload.get("follow_symlinks", False),
            include_patterns=tuple(payload.get("include_patterns", ())),
            exclude_patterns=tuple(payload.get("exclude_patterns", ())),
            max_scan_files=payload.get("max_scan_files", 5000),
            exiftool_path=Path(payload["exiftool_path"]) if payload.get("exiftool_path") else None,
        )
    except (TypeError, ValueError) as exc:
        return _fail(f"Invalid options: {exc}")

    try:
        report = build_doctor_report(options)
    except Exception as exc:
        return _fail(f"Doctor check failed: {exc}")

    output: dict = {
        "command": report.options.command,
        "status": report.status,
        "ready": report.ready,
        "next_action": report.next_action,
        "summary": {
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "info_count": report.info_count,
            "source_count": len(report.source_previews),
            "included_file_count": sum(s.included_file_count for s in report.source_previews),
            "scanned_file_count": sum(s.scanned_file_count for s in report.source_previews),
        },
        "diagnostics": [
            {
                "code": d.code,
                "severity": d.severity,
                "message": d.message,
                "path": str(d.path) if d.path else None,
                "hint": d.hint,
            }
            for d in report.diagnostics
        ],
        "source_previews": [
            {
                "source_root": str(s.source_root),
                "exists": s.exists,
                "is_dir": s.is_dir,
                "scanned_file_count": s.scanned_file_count,
                "included_file_count": s.included_file_count,
                "excluded_by_include_count": s.excluded_by_include_count,
                "excluded_by_exclude_count": s.excluded_by_exclude_count,
                "hidden_skipped_count": s.hidden_skipped_count,
                "scan_limited": s.scan_limited,
            }
            for s in report.source_previews
        ],
    }
    _emit(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="media_manager.bridge_doctor",
        description="Doctor bridge for Tauri desktop app.",
    )


def main(argv: list[str] | None = None) -> int:
    return cmd_check()


if __name__ == "__main__":
    raise SystemExit(main())
