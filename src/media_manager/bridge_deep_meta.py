"""Deep metadata extraction bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse as _ap
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, read_stdin_json
from media_manager.core.metadata.inspect import extract_deep_metadata, compute_metadata_score

logger = logging.getLogger(__name__)


def cmd_deep_meta() -> int:
    payload = read_stdin_json()
    file_path = Path(payload["file_path"])
    result = extract_deep_metadata(file_path)
    _emit(result)
    return 0


def cmd_meta_score() -> int:
    payload = read_stdin_json()
    file_path = Path(payload["file_path"])
    meta = extract_deep_metadata(file_path)
    score = compute_metadata_score(meta)
    _emit(score)
    return 0


def cmd_meta_compare() -> int:
    payload = read_stdin_json()
    path_a = Path(payload["file_a"])
    path_b = Path(payload["file_b"])

    meta_a = extract_deep_metadata(path_a)
    meta_b = extract_deep_metadata(path_b)

    score_a = compute_metadata_score(meta_a)
    score_b = compute_metadata_score(meta_b)

    def _safe_items(d):
        if isinstance(d, dict):
            return d
        return {}

    diff = {}
    for section in ["camera", "shot", "gps", "image", "copyright", "software"]:
        a_sec = _safe_items(meta_a.get(section))
        b_sec = _safe_items(meta_b.get(section))
        for key in set(a_sec.keys()) | set(b_sec.keys()):
            a_val = a_sec.get(key)
            b_val = b_sec.get(key)
            if a_val != b_val:
                k = f"{section}.{key}"
                diff[k] = {"a": a_val, "b": b_val}

    _emit({
        "file_a": str(path_a),
        "file_b": str(path_b),
        "score_a": score_a,
        "score_b": score_b,
        "differences": diff,
    })
    return 0


def build_parser() -> _ap.ArgumentParser:
    parser = _ap.ArgumentParser(prog="media_manager.bridge_deep_meta")
    parser.add_argument("action", choices=["deep-meta", "meta-score", "meta-compare"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    if args.action == "deep-meta":
        return cmd_deep_meta()
    if args.action == "meta-score":
        return cmd_meta_score()
    if args.action == "meta-compare":
        return cmd_meta_compare()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
