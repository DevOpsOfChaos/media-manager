from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.people_review_session import (
    build_people_review_session_state,
    load_people_review_workflow,
    merge_people_groups,
    set_people_face_decision,
    set_people_group_decision,
    split_people_group,
    write_people_review_workflow_session,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager-people-session",
        description="Edit people review workflow decisions for future GUI-style review sessions.",
    )
    subparsers = parser.add_subparsers(dest="command")

    summary = subparsers.add_parser("summary", help="Print a people review session summary.")
    summary.add_argument("--workflow-json", type=Path, required=True, help="People review workflow JSON file.")
    summary.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    group_set = subparsers.add_parser("group-set", help="Set a group name/person/apply decision.")
    group_set.add_argument("--workflow-json", type=Path, required=True, help="People review workflow JSON file.")
    group_set.add_argument("--out", type=Path, help="Output workflow JSON path. Defaults to updating --workflow-json.")
    group_set.add_argument("--group-id", required=True, help="Review group ID to update.")
    apply_group = group_set.add_mutually_exclusive_group()
    apply_group.add_argument("--apply", dest="apply_group", action="store_true", help="Mark group for applying to the catalog.")
    apply_group.add_argument("--no-apply", dest="no_apply_group", action="store_true", help="Do not apply this group to the catalog.")
    group_set.add_argument("--selected-name", help="Name to use for this group/person.")
    group_set.add_argument("--selected-person-id", help="Existing person ID to attach this group to.")
    group_set.add_argument("--review-note", help="Optional review note.")
    group_set.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    face_set = subparsers.add_parser("face-set", help="Include or reject one face in the workflow.")
    face_set.add_argument("--workflow-json", type=Path, required=True, help="People review workflow JSON file.")
    face_set.add_argument("--out", type=Path, help="Output workflow JSON path. Defaults to updating --workflow-json.")
    face_set.add_argument("--face-id", required=True, help="Face ID to update.")
    include_group = face_set.add_mutually_exclusive_group()
    include_group.add_argument("--include", dest="include", action="store_true", help="Include this face in the selected person/group.")
    include_group.add_argument("--exclude", dest="exclude", action="store_true", help="Reject this face from the selected person/group.")
    face_set.add_argument("--note", help="Optional face-level review note.")
    face_set.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    split = subparsers.add_parser("group-split", help="Move selected faces out of one group into a new manual group.")
    split.add_argument("--workflow-json", type=Path, required=True, help="People review workflow JSON file.")
    split.add_argument("--out", type=Path, help="Output workflow JSON path. Defaults to updating --workflow-json.")
    split.add_argument("--group-id", required=True, help="Source group ID.")
    split.add_argument("--face-id", action="append", required=True, help="Face ID to move. Repeat for multiple faces.")
    split.add_argument("--new-group-id", help="Optional new review group ID.")
    split.add_argument("--selected-name", default="", help="Optional name suggestion for the new group.")
    split.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    merge = subparsers.add_parser("group-merge", help="Merge multiple groups into a new manual group.")
    merge.add_argument("--workflow-json", type=Path, required=True, help="People review workflow JSON file.")
    merge.add_argument("--out", type=Path, help="Output workflow JSON path. Defaults to updating --workflow-json.")
    merge.add_argument("--group-id", action="append", required=True, help="Group ID to merge. Repeat for multiple groups.")
    merge.add_argument("--target-group-id", help="Optional new merged group ID.")
    merge.add_argument("--selected-name", help="Optional selected name for the merged group.")
    merge.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser


def _print_summary(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("People review session")
    if isinstance(summary, dict):
        print(f"  Groups: {summary.get('group_count', 0)}")
        print(f"  Faces: {summary.get('face_count', 0)}")
        print(f"  Ready groups: {summary.get('ready_group_count', 0)}")
        print(f"  Needs name: {summary.get('needs_name_group_count', 0)}")
        print(f"  Rejected faces: {summary.get('rejected_faces', 0)}")


def _write_result(args, result) -> dict[str, object]:
    out_path = getattr(args, "out", None) or args.workflow_json
    if result.changed:
        write_people_review_workflow_session(out_path, result.workflow_payload)
    payload = result.to_dict()
    payload["workflow_json"] = str(out_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "summary"

    try:
        workflow = load_people_review_workflow(args.workflow_json)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    if command == "summary":
        payload = build_people_review_session_state(workflow)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_summary(payload)
        return 0

    if command == "group-set":
        apply_group = None
        if args.apply_group:
            apply_group = True
        elif args.no_apply_group:
            apply_group = False
        result = set_people_group_decision(
            workflow,
            group_id=args.group_id,
            apply_group=apply_group,
            selected_name=args.selected_name,
            selected_person_id=args.selected_person_id,
            review_note=args.review_note,
        )
        payload = _write_result(args, result)
    elif command == "face-set":
        include = None
        if args.include:
            include = True
        elif args.exclude:
            include = False
        result = set_people_face_decision(workflow, face_id=args.face_id, include=include, note=args.note)
        payload = _write_result(args, result)
    elif command == "group-split":
        result = split_people_group(
            workflow,
            group_id=args.group_id,
            face_ids=args.face_id,
            new_group_id=args.new_group_id,
            selected_name=args.selected_name,
        )
        payload = _write_result(args, result)
    elif command == "group-merge":
        result = merge_people_groups(
            workflow,
            group_ids=args.group_id,
            target_group_id=args.target_group_id,
            selected_name=args.selected_name,
        )
        payload = _write_result(args, result)
    else:
        parser.error(f"Unsupported command: {command}")
        return 2

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _print_summary(payload)
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
