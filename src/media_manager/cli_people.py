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
from .core.people_review_assets import build_people_review_assets, write_people_review_asset_manifest
from .core.people_review_bundle import build_people_review_bundle_summary_text, write_people_review_bundle
from .core.people_review_ui import build_people_review_workspace, build_people_review_workspace_summary_text
from .core.people_review_workflow import (
    apply_people_review_workflow,
    build_people_review_workflow,
    write_people_review_workflow,
)
from .core.report_export import write_json_report


def _read_json_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


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
    scan_parser.add_argument("--backend", choices=BACKEND_CHOICES, default=DEFAULT_BACKEND, help="People backend. auto uses the strong dlib wheel backend when available and falls back to OpenCV detection.")
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

    review_export = subparsers.add_parser("review-export", help="Build an editable people review workflow from a people scan report.")
    review_export.add_argument("--report-json", type=Path, required=True, help="People scan report JSON, ideally created with --include-encodings before apply.")
    review_export.add_argument("--out", type=Path, required=True, help="Output people review workflow JSON path.")
    review_export.add_argument("--group-limit", type=int, help="Optional maximum number of groups to export.")
    review_export.add_argument("--face-limit-per-group", type=int, help="Optional maximum number of faces per group.")
    review_export.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    review_apply = subparsers.add_parser("review-apply", help="Apply a reviewed people workflow to a local people catalog.")
    review_apply.add_argument("--catalog", type=Path, required=True, help="People catalog JSON path to update.")
    review_apply.add_argument("--workflow-json", type=Path, required=True, help="Edited people review workflow JSON.")
    review_apply.add_argument("--report-json", type=Path, required=True, help="Original people scan report JSON containing face encodings.")
    review_apply.add_argument("--out-catalog", type=Path, help="Optional output catalog path. Defaults to updating --catalog.")
    review_apply.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing the catalog.")
    review_apply.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    review_state = subparsers.add_parser("review-state", help="Build a GUI-ready people review workspace from report/workflow JSON.")
    review_state.add_argument("--report-json", type=Path, required=True, help="People scan report JSON.")
    review_state.add_argument("--workflow-json", type=Path, help="Optional edited people review workflow JSON. If omitted, one is built from the report.")
    review_state.add_argument("--group-limit", type=int, help="Optional maximum number of groups to include.")
    review_state.add_argument("--face-limit-per-group", type=int, help="Optional maximum number of faces per group.")
    review_state.add_argument("--include-encodings", action="store_true", help="Include encodings in the workspace JSON. Sensitive biometric metadata; keep private.")
    review_state.add_argument("--out", type=Path, help="Optional output workspace JSON path.")
    review_state.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    review_assets = subparsers.add_parser("review-assets", help="Build local face crop assets for a GUI people review workspace.")
    review_assets.add_argument("--report-json", type=Path, required=True, help="People scan report JSON.")
    review_assets.add_argument("--workflow-json", type=Path, help="Optional people review workflow JSON. If provided, only referenced faces are exported.")
    review_assets.add_argument("--asset-dir", type=Path, required=True, help="Directory where face crop assets should be written.")
    review_assets.add_argument("--out", type=Path, help="Output asset manifest JSON path. Defaults to <asset-dir>/people_review_assets.json.")
    review_assets.add_argument("--crop-padding", type=float, default=0.25, help="Face crop padding ratio. Default: 0.25.")
    review_assets.add_argument("--thumbnail-size", type=int, default=256, help="Maximum crop image size. Default: 256.")
    review_assets.add_argument("--quality", type=int, default=90, help="JPEG quality from 1 to 100. Default: 90.")
    review_assets.add_argument("--no-overwrite", action="store_true", help="Do not overwrite existing crop files.")
    review_assets.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    review_bundle = subparsers.add_parser("review-bundle", help="Build a complete GUI-ready people review bundle directory.")
    review_bundle.add_argument("--report-json", type=Path, required=True, help="People scan report JSON.")
    review_bundle.add_argument("--workflow-json", type=Path, help="Optional edited people review workflow JSON. If omitted, one is built from the report.")
    review_bundle.add_argument("--bundle-dir", type=Path, required=True, help="Directory where the people review bundle should be written.")
    review_bundle.add_argument("--catalog", type=Path, help="Optional people catalog path to reference in the bundle manifest.")
    review_bundle.add_argument("--no-assets", action="store_true", help="Do not generate face crop assets.")
    review_bundle.add_argument("--include-encodings-in-workspace", action="store_true", help="Also include encodings in workspace JSON. Sensitive biometric metadata; keep private.")
    review_bundle.add_argument("--crop-padding", type=float, default=0.25, help="Face crop padding ratio. Default: 0.25.")
    review_bundle.add_argument("--thumbnail-size", type=int, default=256, help="Maximum crop image size. Default: 256.")
    review_bundle.add_argument("--quality", type=int, default=90, help="JPEG quality from 1 to 100. Default: 90.")
    review_bundle.add_argument("--no-overwrite", action="store_true", help="Do not overwrite existing crop files.")
    review_bundle.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

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


def _print_review_export_text(payload: dict[str, object], out_path: Path) -> None:
    print("People review workflow")
    print(f"  Output: {out_path}")
    print(f"  Groups: {payload.get('group_count', 0)}")
    print(f"  Encodings in source report: {payload.get('encoding_count_in_source_report', 0)}")
    print("  Next action: Edit group names/include flags, then run people review-apply.")


def _print_review_apply_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("People review apply")
    print(f"  Status: {payload.get('status')}")
    if isinstance(summary, dict):
        print(f"  Groups applied: {summary.get('groups_applied', 0)}")
        print(f"  Persons created: {summary.get('persons_created', 0)}")
        print(f"  Embeddings added: {summary.get('embeddings_added', 0)}")
        print(f"  Problems: {summary.get('problem_count', 0)}")
    print(f"  Next action: {payload.get('next_action')}")


def _print_assets_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("People review assets")
    print(f"  Asset dir: {payload.get('asset_dir')}")
    if isinstance(summary, dict):
        print(f"  Assets: {summary.get('asset_count', 0)}")
        print(f"  Generated: {summary.get('generated_count', 0)}")
        print(f"  Existing: {summary.get('existing_count', 0)}")
        print(f"  Errors: {summary.get('error_count', 0)}")
    print("  Next action: Open the asset manifest from the future GUI review page.")


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
            print(f"  dlib available: {payload['dlib_available']}")
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

    if command == "review-export":
        try:
            report_payload = _read_json_object(args.report_json)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = build_people_review_workflow(
            report_payload,
            group_limit=args.group_limit,
            face_limit_per_group=args.face_limit_per_group,
        )
        write_people_review_workflow(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_review_export_text(payload, args.out)
        return 0

    if command == "review-apply":
        try:
            workflow_payload = _read_json_object(args.workflow_json)
            report_payload = _read_json_object(args.report_json)
            result = apply_people_review_workflow(
                catalog_path=args.catalog,
                workflow_payload=workflow_payload,
                report_payload=report_payload,
                output_catalog_path=args.out_catalog,
                dry_run=args.dry_run,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = result.to_dict()
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_review_apply_text(payload)
        return 0 if result.status == "ok" else 1

    if command == "review-state":
        try:
            report_payload = _read_json_object(args.report_json)
            workflow_payload = _read_json_object(args.workflow_json) if args.workflow_json is not None else None
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = build_people_review_workspace(
            report_payload=report_payload,
            workflow_payload=workflow_payload,
            group_limit=args.group_limit,
            face_limit_per_group=args.face_limit_per_group,
            include_encodings=args.include_encodings,
        )
        if args.out is not None:
            write_json_report(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(build_people_review_workspace_summary_text(payload))
        return 0

    if command == "review-assets":
        try:
            report_payload = _read_json_object(args.report_json)
            workflow_payload = _read_json_object(args.workflow_json) if args.workflow_json is not None else None
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = build_people_review_assets(
            report_payload=report_payload,
            workflow_payload=workflow_payload,
            asset_dir=args.asset_dir,
            crop_padding_ratio=args.crop_padding,
            thumbnail_size=args.thumbnail_size,
            quality=args.quality,
            overwrite=not args.no_overwrite,
        )
        manifest_path = args.out or (args.asset_dir / "people_review_assets.json")
        write_people_review_asset_manifest(manifest_path, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_assets_text(payload)
        summary = payload.get("summary", {})
        error_count = summary.get("error_count", 0) if isinstance(summary, dict) else 0
        return 0 if error_count == 0 else 1

    if command == "review-bundle":
        try:
            report_payload = _read_json_object(args.report_json)
            workflow_payload = _read_json_object(args.workflow_json) if args.workflow_json is not None else None
            payload = write_people_review_bundle(
                report_payload=report_payload,
                workflow_payload=workflow_payload,
                bundle_dir=args.bundle_dir,
                source_report_path=args.report_json,
                source_workflow_path=args.workflow_json,
                catalog_path=args.catalog,
                include_assets=not args.no_assets,
                include_encodings_in_workspace=args.include_encodings_in_workspace,
                crop_padding_ratio=args.crop_padding,
                thumbnail_size=args.thumbnail_size,
                quality=args.quality,
                overwrite_assets=not args.no_overwrite,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(build_people_review_bundle_summary_text(payload))
        summary = payload.get("summary", {})
        error_count = summary.get("asset_error_count", 0) if isinstance(summary, dict) else 0
        return 0 if error_count == 0 else 1

    parser.error(f"Unsupported people command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
