from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

APP_PROFILE_SCHEMA_VERSION = 1

SUPPORTED_COMMANDS = {"organize", "rename", "duplicates", "cleanup", "doctor", "people"}


@dataclass(slots=True, frozen=True)
class AppProfileValidation:
    valid: bool
    profile_id: str
    command: str
    problems: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    command_argv: tuple[str, ...] = ()
    command_preview: str | None = None


@dataclass(slots=True, frozen=True)
class AppProfileRecord:
    path: Path
    profile_id: str
    title: str
    command: str
    description: str = ""
    tags: tuple[str, ...] = ()
    favorite: bool = False
    valid: bool = False
    problem_count: int = 0
    warning_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "profile_id": self.profile_id,
            "title": self.title,
            "command": self.command,
            "description": self.description,
            "tags": list(self.tags),
            "favorite": self.favorite,
            "valid": self.valid,
            "problem_count": self.problem_count,
            "warning_count": self.warning_count,
        }


def _normalize_profile_id(value: str) -> str:
    text = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-") or "profile"


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("App profile must be a JSON object.")
    return payload


def _profile_values(profile: dict[str, Any]) -> dict[str, Any]:
    values = profile.get("values", {})
    if not isinstance(values, dict):
        raise ValueError("App profile values must be a JSON object.")
    return values


def build_app_profile_payload(
    *,
    profile_id: str,
    title: str,
    command: str,
    values: dict[str, Any] | None = None,
    description: str = "",
    tags: Iterable[str] = (),
    favorite: bool = False,
) -> dict[str, Any]:
    normalized_command = str(command).strip().lower()
    normalized_id = _normalize_profile_id(profile_id or title or normalized_command)
    recommended_view = "People review" if normalized_command == "people" else "New run"
    return {
        "schema_version": APP_PROFILE_SCHEMA_VERSION,
        "profile_id": normalized_id,
        "title": title.strip() or normalized_id,
        "description": description.strip(),
        "command": normalized_command,
        "tags": [str(item).strip() for item in tags if str(item).strip()],
        "favorite": bool(favorite),
        "values": dict(values or {}),
        "gui": {
            "card_title": title.strip() or normalized_id,
            "recommended_view": recommended_view,
            "show_in_dashboard": bool(favorite),
        },
    }


def write_app_profile(path: str | Path, profile: dict[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def load_app_profile(path: str | Path) -> dict[str, Any]:
    profile = _read_json_object(Path(path))
    schema_version = int(profile.get("schema_version", 0))
    if schema_version != APP_PROFILE_SCHEMA_VERSION:
        raise ValueError(f"App profile schema_version must be {APP_PROFILE_SCHEMA_VERSION}.")
    _profile_values(profile)
    return profile


def _append_repeated(parts: list[str], flag: str, values: Iterable[str]) -> None:
    for value in values:
        text = str(value).strip()
        if text:
            parts.extend([flag, text])


def _append_value(parts: list[str], flag: str, value: Any) -> None:
    if value is None:
        return
    text = str(value).strip()
    if text:
        parts.extend([flag, text])


def _append_flag(parts: list[str], flag: str, value: Any) -> None:
    if _bool_value(value):
        parts.append(flag)


def _append_common(parts: list[str], values: dict[str, Any], *, target: bool = False, apply: bool = True) -> None:
    _append_repeated(parts, "--source", _string_list(values.get("source_dirs", values.get("sources", values.get("source")))))
    if target:
        _append_value(parts, "--target", values.get("target_root", values.get("target")))
    _append_repeated(parts, "--include-pattern", _string_list(values.get("include_patterns", values.get("include_pattern"))))
    _append_repeated(parts, "--exclude-pattern", _string_list(values.get("exclude_patterns", values.get("exclude_pattern"))))
    _append_flag(parts, "--non-recursive", values.get("non_recursive"))
    _append_flag(parts, "--include-hidden", values.get("include_hidden"))
    _append_value(parts, "--run-dir", values.get("run_dir"))
    _append_value(parts, "--report-json", values.get("report_json"))
    _append_value(parts, "--review-json", values.get("review_json"))
    _append_flag(parts, "--json", values.get("json_output", values.get("json")))
    if apply:
        _append_flag(parts, "--apply", values.get("apply"))
        _append_value(parts, "--journal", values.get("journal"))
    _append_value(parts, "--exiftool-path", values.get("exiftool_path"))


def _append_people_scan(parts: list[str], values: dict[str, Any]) -> None:
    _append_repeated(parts, "--source", _string_list(values.get("source_dirs", values.get("sources", values.get("source")))))
    _append_value(parts, "--catalog", values.get("catalog"))
    _append_value(parts, "--backend", values.get("backend"))
    _append_value(parts, "--tolerance", values.get("tolerance"))
    _append_repeated(parts, "--include-pattern", _string_list(values.get("include_patterns", values.get("include_pattern"))))
    _append_repeated(parts, "--exclude-pattern", _string_list(values.get("exclude_patterns", values.get("exclude_pattern"))))
    _append_repeated(parts, "--include-extension", _string_list(values.get("include_extensions", values.get("include_extension"))))
    _append_value(parts, "--report-json", values.get("report_json"))
    _append_value(parts, "--review-json", values.get("review_json"))
    _append_flag(parts, "--include-encodings", values.get("include_encodings"))
    _append_flag(parts, "--require-backend", values.get("require_backend"))
    _append_flag(parts, "--json", values.get("json_output", values.get("json")))


def build_app_profile_argv(profile: dict[str, Any]) -> list[str]:
    command = str(profile.get("command", "")).strip().lower()
    values = _profile_values(profile)
    parts = ["media-manager", command]

    if command == "organize":
        _append_common(parts, values, target=True, apply=True)
        _append_value(parts, "--pattern", values.get("pattern"))
        mode = str(values.get("operation_mode", values.get("mode", ""))).strip().lower()
        if mode == "move":
            parts.append("--move")
        elif mode == "copy":
            parts.append("--copy")
        _append_flag(parts, "--include-associated-files", values.get("include_associated_files"))
        _append_value(parts, "--conflict-policy", values.get("conflict_policy"))
        _append_flag(parts, "--show-files", values.get("show_files"))
        return parts

    if command == "rename":
        _append_common(parts, values, target=False, apply=True)
        _append_value(parts, "--template", values.get("template"))
        _append_flag(parts, "--include-associated-files", values.get("include_associated_files"))
        _append_value(parts, "--conflict-policy", values.get("conflict_policy"))
        _append_flag(parts, "--show-files", values.get("show_files"))
        return parts

    if command == "duplicates":
        _append_common(parts, values, target=False, apply=False)
        _append_repeated(parts, "--media-kind", _string_list(values.get("media_kinds", values.get("media_kind"))))
        _append_repeated(parts, "--include-extension", _string_list(values.get("include_extensions", values.get("include_extension"))))
        _append_repeated(parts, "--exclude-extension", _string_list(values.get("exclude_extensions", values.get("exclude_extension"))))
        _append_value(parts, "--policy", values.get("policy"))
        _append_value(parts, "--mode", values.get("mode"))
        _append_value(parts, "--export-decisions", values.get("export_decisions"))
        _append_value(parts, "--import-decisions", values.get("import_decisions"))
        _append_flag(parts, "--similar-images", values.get("similar_images"))
        _append_value(parts, "--similar-threshold", values.get("similar_threshold"))
        _append_value(parts, "--similar-policy", values.get("similar_policy"))
        _append_flag(parts, "--show-groups", values.get("show_groups"))
        _append_flag(parts, "--show-decisions", values.get("show_decisions"))
        _append_flag(parts, "--show-unresolved", values.get("show_unresolved"))
        _append_flag(parts, "--show-plan", values.get("show_plan"))
        _append_flag(parts, "--apply", values.get("apply"))
        _append_flag(parts, "--yes", values.get("yes"))
        _append_value(parts, "--journal", values.get("journal"))
        return parts

    if command == "cleanup":
        _append_common(parts, values, target=True, apply=False)
        _append_value(parts, "--organize-pattern", values.get("organize_pattern"))
        _append_value(parts, "--rename-template", values.get("rename_template"))
        _append_value(parts, "--duplicate-policy", values.get("duplicate_policy"))
        _append_value(parts, "--duplicate-mode", values.get("duplicate_mode"))
        _append_flag(parts, "--include-associated-files", values.get("include_associated_files"))
        _append_value(parts, "--leftover-mode", values.get("leftover_mode"))
        _append_value(parts, "--leftover-dir-name", values.get("leftover_dir_name"))
        _append_value(parts, "--conflict-policy", values.get("conflict_policy"))
        if _bool_value(values.get("apply_organize")):
            parts.append("--apply-organize")
        if _bool_value(values.get("apply_rename")):
            parts.append("--apply-rename")
        _append_value(parts, "--journal", values.get("journal"))
        _append_flag(parts, "--show-files", values.get("show_files"))
        return parts

    if command == "doctor":
        parts = ["media-manager", "doctor"]
        _append_value(parts, "--command", values.get("doctor_command", values.get("command_context")))
        _append_common(parts, values, target=bool(values.get("target_root") or values.get("target")), apply=False)
        _append_flag(parts, "--fail-on-warnings", values.get("fail_on_warnings"))
        _append_value(parts, "--max-scan-files", values.get("max_scan_files"))
        return parts

    if command == "people":
        people_mode = str(values.get("people_mode", values.get("mode", "scan"))).strip().lower().replace("_", "-")
        if people_mode == "scan":
            parts = ["media-manager", "people", "scan"]
            _append_people_scan(parts, values)
            return parts
        if people_mode in {"review-bundle", "bundle"}:
            parts = ["media-manager", "people", "review-bundle"]
            _append_value(parts, "--report-json", values.get("report_json"))
            _append_value(parts, "--workflow-json", values.get("workflow_json"))
            _append_value(parts, "--bundle-dir", values.get("bundle_dir"))
            _append_value(parts, "--catalog", values.get("catalog"))
            _append_flag(parts, "--no-assets", values.get("no_assets"))
            _append_flag(parts, "--include-encodings-in-workspace", values.get("include_encodings_in_workspace"))
            _append_flag(parts, "--json", values.get("json_output", values.get("json")))
            return parts
        if people_mode in {"review-apply", "apply-review"}:
            parts = ["media-manager", "people", "review-apply"]
            _append_value(parts, "--catalog", values.get("catalog"))
            _append_value(parts, "--workflow-json", values.get("workflow_json"))
            _append_value(parts, "--report-json", values.get("report_json"))
            _append_value(parts, "--out-catalog", values.get("out_catalog"))
            _append_flag(parts, "--dry-run", values.get("dry_run"))
            _append_flag(parts, "--json", values.get("json_output", values.get("json")))
            return parts
        return parts

    return parts


def _quote_if_needed(value: str) -> str:
    return f'"{value}"' if any(ch.isspace() for ch in value) else value


def render_app_profile_command(profile: dict[str, Any]) -> str:
    return " ".join(_quote_if_needed(part) for part in build_app_profile_argv(profile))


def validate_app_profile(profile: dict[str, Any]) -> AppProfileValidation:
    profile_id = str(profile.get("profile_id", "")).strip() or "profile"
    command = str(profile.get("command", "")).strip().lower()
    problems: list[str] = []
    warnings: list[str] = []

    try:
        schema_version = int(profile.get("schema_version", 0))
    except (TypeError, ValueError):
        schema_version = 0
    if schema_version != APP_PROFILE_SCHEMA_VERSION:
        problems.append(f"schema_version must be {APP_PROFILE_SCHEMA_VERSION}.")
    if command not in SUPPORTED_COMMANDS:
        problems.append(f"Unsupported command: {command or '<missing>'}.")

    try:
        values = _profile_values(profile)
    except ValueError as exc:
        values = {}
        problems.append(str(exc))

    source_values = _string_list(values.get("source_dirs", values.get("sources", values.get("source"))))
    if command in {"organize", "rename", "duplicates", "cleanup"} and not source_values:
        problems.append("At least one source directory is required.")
    if command in {"organize", "cleanup"} and not str(values.get("target_root", values.get("target", ""))).strip():
        problems.append("A target directory is required.")

    if command == "duplicates" and _bool_value(values.get("apply")):
        if not _bool_value(values.get("yes")):
            problems.append("Duplicate apply requires yes confirmation.")
        if not values.get("import_decisions") and not values.get("policy"):
            warnings.append("Duplicate apply is safer with imported decisions or an explicit policy.")

    if command == "cleanup" and _bool_value(values.get("apply_organize")) and _bool_value(values.get("apply_rename")):
        problems.append("Cleanup can apply organize or rename, not both in the same profile.")
    if command == "cleanup" and values.get("leftover_mode") == "consolidate" and not _bool_value(values.get("apply_organize")):
        problems.append("Leftover consolidation requires apply_organize.")

    if command == "people":
        people_mode = str(values.get("people_mode", values.get("mode", "scan"))).strip().lower().replace("_", "-")
        if people_mode == "scan" and not source_values:
            problems.append("At least one source directory is required for people scan profiles.")
        if people_mode in {"review-bundle", "bundle"}:
            if not str(values.get("report_json", "")).strip():
                problems.append("people review-bundle profiles require report_json.")
            if not str(values.get("bundle_dir", "")).strip():
                problems.append("people review-bundle profiles require bundle_dir.")
        if people_mode in {"review-apply", "apply-review"}:
            for key in ("catalog", "workflow_json", "report_json"):
                if not str(values.get(key, "")).strip():
                    problems.append(f"people review-apply profiles require {key}.")
        if _bool_value(values.get("include_encodings")):
            warnings.append("People reports with encodings contain sensitive biometric metadata and should stay local/private.")

    argv: tuple[str, ...] = ()
    preview: str | None = None
    if not problems:
        argv = tuple(build_app_profile_argv(profile))
        preview = render_app_profile_command(profile)
    return AppProfileValidation(
        valid=not problems,
        profile_id=profile_id,
        command=command,
        problems=tuple(problems),
        warnings=tuple(warnings),
        command_argv=argv,
        command_preview=preview,
    )


def build_app_profile_preview(profile: dict[str, Any]) -> dict[str, Any]:
    validation = validate_app_profile(profile)
    return {
        "schema_version": APP_PROFILE_SCHEMA_VERSION,
        "profile_id": validation.profile_id,
        "title": profile.get("title", validation.profile_id),
        "description": profile.get("description", ""),
        "command": validation.command,
        "valid": validation.valid,
        "problems": list(validation.problems),
        "warnings": list(validation.warnings),
        "command_argv": list(validation.command_argv),
        "command_preview": validation.command_preview,
        "values": _profile_values(profile),
        "gui": profile.get("gui", {}),
    }


def scan_app_profiles(profile_dir: str | Path) -> list[AppProfileRecord]:
    root = Path(profile_dir)
    records: list[AppProfileRecord] = []
    if not root.exists():
        return records
    for path in sorted(root.glob("*.json"), key=lambda item: item.name.lower()):
        try:
            profile = load_app_profile(path)
            validation = validate_app_profile(profile)
            records.append(
                AppProfileRecord(
                    path=path,
                    profile_id=str(profile.get("profile_id", path.stem)),
                    title=str(profile.get("title", path.stem)),
                    command=str(profile.get("command", "")),
                    description=str(profile.get("description", "")),
                    tags=tuple(_string_list(profile.get("tags"))),
                    favorite=_bool_value(profile.get("favorite")),
                    valid=validation.valid,
                    problem_count=len(validation.problems),
                    warning_count=len(validation.warnings),
                )
            )
        except Exception:
            records.append(AppProfileRecord(path=path, profile_id=path.stem, title=path.stem, command="", valid=False, problem_count=1))
    return records


def summarize_app_profiles(records: Iterable[AppProfileRecord]) -> dict[str, Any]:
    record_list = list(records)
    by_command: dict[str, int] = {}
    for item in record_list:
        if item.command:
            by_command[item.command] = by_command.get(item.command, 0) + 1
    return {
        "profile_count": len(record_list),
        "valid_count": sum(1 for item in record_list if item.valid),
        "invalid_count": sum(1 for item in record_list if not item.valid),
        "favorite_count": sum(1 for item in record_list if item.favorite),
        "command_summary": dict(sorted(by_command.items())),
    }


__all__ = [
    "APP_PROFILE_SCHEMA_VERSION",
    "SUPPORTED_COMMANDS",
    "AppProfileRecord",
    "AppProfileValidation",
    "build_app_profile_payload",
    "build_app_profile_preview",
    "build_app_profile_argv",
    "load_app_profile",
    "render_app_profile_command",
    "scan_app_profiles",
    "summarize_app_profiles",
    "validate_app_profile",
    "write_app_profile",
]
