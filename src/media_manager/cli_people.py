from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.people_recognition import (
    BACKEND_CHOICES,
    DEFAULT_BACKEND,
    DEFAULT_TOLERANCE,
    PeopleScanConfig,
    add_person_to_catalog,
    build_people_review_payload,
    inspect_people_backend,
    load_people_catalog,
    rename_person_in_catalog,
    scan_people,
    write_people_catalog,
)
from .core.report_export import write_json_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager people",
        description="Local people detection and named-person catalog tools.",
    )
    subparsers = parser.add_subparsers(dest="people_command")

    scan_parser = subparsers.add_parser("scan", help="Scan images for faces and match them against a local people catalog when the selected backend supports matching.")
    scan_parser.add_argument("--source", dest="sources", action="append", type=Path, required=True, help="Source directory. Repeat for multiple sources.")
    scan_parser.add_argument("--catalog", type=Path, help="Optional local people catalog JSON file.")
    scan_parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE, help=f"Face match tolerance. Default: {DEFAULT_TOLERANCE}.")
    scan_parser.add_argument("--backend", choices=BACKEND_CHOICES, default=DEFAULT_BACKEND, help="People backend. auto uses face-recognition when available and falls back to OpenCV detection.")
    scan_parser.add_argument("--include-pattern", action="append", default=[], help="Include paths matching a glob-style pattern. Repeat to add multiple patterns.")
    scan_parser.add_argument("--exclude-pattern", action="append", default=[], help="Exclude paths matching a glob-style pattern. Repeat to add multiple patterns.")
    scan_parser.add_argument("--include-extension", action="append", default=[], help="Limit scan to specific image extensions such as jpg or png. Repeat to add multiple extensions.")
    scan_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    scan_parser.add_argument("--report-json", type=Path, help="Write full people scan report JSON.")
    scan_parser.add_argument("--review-json", type=Path, help="Write compact review payload for unknown faces.")
    scan_parser.add_argument("--include-encodings", action="store_true", help="Include face encodings in the report. Sensitive biometric metadata; keep private. Only meaningful for embedding-capable backends.")
    scan_parser.add_argument("--require-backend", action="store_true", help="Return exit code 1 when the requested people backend is unavailable.")

    backend_parser = subparsers.add_parser("backend", help="Check local people backend availability and capabilities.")
    backend_parser.add_argument("--backend", choices=BACKEND_CHOICES, default=DEFAULT_BACKEND, help="Backend to inspect. Default: auto.")
    backend_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    init_parser = subparsers.add_parser("catalog-init", help="Create an empty local people catalog JSON file.")
    init_parser.add_argument("--catalog", type=Path, required=True, help="Catalog path to create.")
    init_parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing catalog file.")

    list_parser = subparsers.add_parser("catalog-list", help="List people in a local catalog.")
    list_parser.add_argument("--catalog", type=Path, required=True, help="Catalog path to read.")
    list_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    add_parser = subparsers.add_parser("person-add", help="Add a named person to a local catalog.")
    add_parser.add_argument("--catalog", type=Path, required=True, help="Catalog path to update.")
    add_parser.add_argument("--name", required=True, help="Person display name.")
    add_parser.add_argument("--person-id", help="Optional stable person ID. Defaults to a slug from the name.")
    add_parser.add_argument("--alias", action="append", default=[], help="Optional alias. Repeat to add multiple aliases.")
    add_parser.add_argument("--notes", default="", help="Optional private notes.")
    add_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    rename_parser = subparsers.add_parser("person-rename", help="Rename an existing person in a local catalog.")
    rename_parser.add_argument("--catalog", type=Path, required=True, help="Catalog path to update.")
    rename_parser.add_argument("--person-id", required=True, help="Person ID to rename.")
    rename_parser.add_argument("--name", required=True, help="New display name.")
    rename_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    return parser


def _print_scan_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    capabilities = payload.get("capabilities", {})
    print("People scan")
    print(f"  Status: {payload.get('status')}")
    print(f"  Backend: {payload.get('backend')}")
    print(f"  Backend available: {payload.get('backend_available')}")
    if isinstance(capabilities, dict):
        print(f"  Face detection: {capabilities.get('face_detection')}")
        print(f"  Named-person matching: {capabilities.get('named_person_matching')}")
    if isinstance(summary, dict):
        print(f"  Images: {summary.get('image_files', 0)}")
        print(f"  Faces: {summary.get('face_count', 0)}")
        print(f"  Matched faces: {summary.get('matched_faces', 0)}")
        print(f"  Unknown faces: {summary.get('unknown_faces', 0)}")
        print(f"  Unknown clusters: {summary.get('unknown_cluster_count', 0)}")
    print(f"  Next action: {payload.get('next_action')}")


def _catalog_summary(catalog_path: Path, catalog) -> dict[str, object]:
    return {
        "catalog": str(catalog_path),
        "schema_version": catalog.schema_version,
        "person_count": len(catalog.persons),
        "persons": [person.to_dict() for person in sorted(catalog.persons.values(), key=lambda item: item.person_id)],
        "privacy_notice": "This catalog can contain sensitive biometric metadata. Keep it local/private.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.people_command or "backend"

    if command == "backend":
        status = inspect_people_backend(args.backend)
        payload = status.to_dict()
        payload["requested_backend"] = args.backend
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print("People recognition backend")
            print(f"  Requested backend: {args.backend}")
            print(f"  Selected backend: {payload['selected_backend']}")
            print(f"  Available: {payload['available']}")
            print(f"  face_recognition available: {payload['face_recognition_available']}")
            print(f"  OpenCV available: {payload['opencv_available']}")
            capabilities = payload.get("capabilities", {})
            if isinstance(capabilities, dict):
                print(f"  Face detection: {capabilities.get('face_detection')}")
                print(f"  Named-person matching: {capabilities.get('named_person_matching')}")
            print(f"  Next action: {payload['next_action']}")
        return 0 if payload["available"] else 1

    if command == "catalog-init":
        if args.catalog.exists() and not args.overwrite:
            parser.error(f"Catalog already exists: {args.catalog}")
        catalog = load_people_catalog(None)
        write_people_catalog(args.catalog, catalog)
        print(f"Created people catalog: {args.catalog}")
        return 0

    if command == "catalog-list":
        try:
            catalog = load_people_catalog(args.catalog)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = _catalog_summary(args.catalog, catalog)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print("People catalog")
            print(f"  Catalog: {args.catalog}")
            print(f"  Persons: {payload['person_count']}")
            for person in payload["persons"]:
                print(f"  - {person['person_id']} | {person.get('name') or '-'} | faces={person.get('face_count', 0)}")
        return 0

    if command == "person-add":
        try:
            catalog = load_people_catalog(args.catalog)
            person = add_person_to_catalog(
                catalog,
                name=args.name,
                person_id=args.person_id,
                aliases=args.alias or (),
                notes=args.notes,
            )
            write_people_catalog(args.catalog, catalog)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = {"catalog": str(args.catalog), "person": person.to_dict()}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Added person: {person.person_id} | {person.name}")
        return 0

    if command == "person-rename":
        try:
            catalog = load_people_catalog(args.catalog)
            person = rename_person_in_catalog(catalog, person_id=args.person_id, name=args.name)
            write_people_catalog(args.catalog, catalog)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = {"catalog": str(args.catalog), "person": person.to_dict()}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Renamed person: {person.person_id} | {person.name}")
        return 0

    if command == "scan":
        media_extensions = frozenset(args.include_extension) if args.include_extension else None
        config = PeopleScanConfig(
            source_dirs=list(args.sources),
            catalog_path=args.catalog,
            tolerance=args.tolerance,
            backend=args.backend,
            include_patterns=tuple(args.include_pattern or ()),
            exclude_patterns=tuple(args.exclude_pattern or ()),
            media_extensions=media_extensions,
            include_encodings_in_report=args.include_encodings,
            require_backend=args.require_backend,
        )
        try:
            result = scan_people(config)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = result.to_dict(include_encoding=args.include_encodings)
        review_payload = build_people_review_payload(payload)
        if args.report_json is not None:
            write_json_report(args.report_json, payload)
        if args.review_json is not None:
            write_json_report(args.review_json, review_payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_scan_text(payload)
        if result.status == "backend_missing" and args.require_backend:
            return 1
        return 0

    parser.error(f"Unsupported people command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
