from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


CONFIG_DIR = Path.home() / ".media-manager"
CONFIG_PATH = CONFIG_DIR / "config.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager config",
        description="Manage media-manager configuration.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Print the entire configuration.",
    )
    parser.add_argument(
        "--set",
        dest="set_key",
        metavar="KEY",
        help="Set a configuration key.",
    )
    parser.add_argument(
        "--value",
        dest="set_value",
        metavar="VALUE",
        help="Value for --set.",
    )
    parser.add_argument(
        "--get",
        dest="get_key",
        metavar="KEY",
        help="Get a configuration value.",
    )
    parser.add_argument(
        "--default",
        help="Default value when key is not found (for --get).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove the entire configuration file.",
    )
    parser.add_argument(
        "--unset",
        metavar="KEY",
        help="Remove a single configuration key.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    return parser


def _read_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _write_config(config: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    use_json = args.json or os.environ.get("MEDIA_MANAGER_JSON") == "1"
    use_quiet = os.environ.get("MEDIA_MANAGER_QUIET") == "1"

    if args.set_key:
        if args.set_value is None:
            print("Error: --value is required with --set", file=sys.stderr)
            return 1
        config = _read_config()
        config[args.set_key] = args.set_value
        _write_config(config)
        if use_json:
            print(json.dumps({"status": "ok", "key": args.set_key, "value": args.set_value}))
        elif not use_quiet:
            print(f"Set {args.set_key} = {args.set_value}")
        return 0

    if args.get_key:
        config = _read_config()
        value = config.get(args.get_key, args.default)
        if use_json:
            print(json.dumps({"key": args.get_key, "value": value, "found": args.get_key in config}))
        else:
            if value is not None:
                print(value)
        return 0

    if args.unset:
        config = _read_config()
        if args.unset in config:
            del config[args.unset]
            _write_config(config)
            if use_json:
                print(json.dumps({"status": "ok", "key": args.unset, "action": "removed"}))
            elif not use_quiet:
                print(f"Removed {args.unset}")
        else:
            if use_json:
                print(json.dumps({"status": "not_found", "key": args.unset}))
            elif not use_quiet:
                print(f"Key not found: {args.unset}")
        return 0

    if args.reset:
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()
            if use_json:
                print(json.dumps({"status": "ok", "action": "reset"}))
            elif not use_quiet:
                print("Config reset.")
        else:
            if use_json:
                print(json.dumps({"status": "ok", "action": "noop", "reason": "no config file"}))
            elif not use_quiet:
                print("No config file to reset.")
        return 0

    if args.show or (not args.set_key and not args.get_key and not args.unset and not args.reset):
        config = _read_config()
        if use_json:
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            if config:
                print(json.dumps(config, indent=2, ensure_ascii=False))
            else:
                print("No configuration found.")
        return 0
    return 0


cmd_config = main

