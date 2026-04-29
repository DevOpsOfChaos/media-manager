from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

QT_RUNTIME_SMOKE_ARTIFACT_VERIFICATION_SCHEMA_VERSION = "1.0"

_REQUIRED_FILENAMES = (
    "runtime-smoke-plan.json",
    "runtime-smoke-results-template.json",
    "runtime-smoke-shareable-export.json",
    "runtime-smoke-summary.txt",
    "README.txt",
    "runtime-smoke-artifacts-manifest.json",
)

_EXPECTED_JSON_KINDS = {
    "runtime-smoke-plan.json": "guarded_qt_runtime_smoke_integration",
    "runtime-smoke-results-template.json": "qt_runtime_smoke_result_payload_template",
    "runtime-smoke-shareable-export.json": "qt_runtime_smoke_export_bundle",
    "runtime-smoke-artifacts-manifest.json": "qt_runtime_smoke_local_artifact_pack_manifest",
    "runtime-smoke-result-payload-report.json": "qt_runtime_smoke_result_payload_report",
}


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_payload(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"{path.name} is not valid JSON: {exc.msg}"
    except OSError as exc:
        return None, f"{path.name} could not be read: {exc}"
    if not isinstance(payload, Mapping):
        return None, f"{path.name} must contain a JSON object"
    return dict(payload), None


def _contains_key(value: object, key: str) -> bool:
    if isinstance(value, Mapping):
        if key in value:
            return True
        return any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


def _manifest_filenames(manifest: Mapping[str, Any]) -> list[str]:
    files = []
    for raw in _list(manifest.get("files")):
        item = _mapping(raw)
        filename = _text(item.get("filename"))
        if filename:
            files.append(filename)
    return files


def _record_problem(problems: list[dict[str, object]], code: str, message: str, *, filename: str = "", severity: str = "error") -> None:
    problems.append({"code": code, "message": message, "filename": filename, "severity": severity})


def verify_qt_runtime_smoke_local_artifact_pack_dir(path: str | Path) -> dict[str, object]:
    target = Path(path)
    problems: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    files: list[dict[str, object]] = []
    json_payloads: dict[str, dict[str, object]] = {}

    if not target.exists():
        _record_problem(problems, "missing-directory", f"Runtime Smoke artifact directory does not exist: {target}")
        exists = False
        is_dir = False
    else:
        exists = True
        is_dir = target.is_dir()
        if not is_dir:
            _record_problem(problems, "not-a-directory", f"Runtime Smoke artifact path is not a directory: {target}")

    manifest: dict[str, object] = {}
    expected_filenames = set(_REQUIRED_FILENAMES)

    if exists and is_dir:
        manifest_path = target / "runtime-smoke-artifacts-manifest.json"
        if not manifest_path.is_file():
            _record_problem(problems, "missing-manifest", "runtime-smoke-artifacts-manifest.json is required for verification.", filename="runtime-smoke-artifacts-manifest.json")
        else:
            payload, error = _json_payload(manifest_path)
            if error:
                _record_problem(problems, "invalid-json", error, filename=manifest_path.name)
            else:
                manifest = payload or {}
                for filename in _manifest_filenames(manifest):
                    expected_filenames.add(filename)

        for filename in sorted(expected_filenames):
            file_path = target / filename
            record: dict[str, object] = {"filename": filename, "exists": file_path.is_file(), "byte_count": 0, "sha256": "", "json_kind": ""}
            if not file_path.is_file():
                _record_problem(problems, "missing-file", f"{filename} is listed or required but missing.", filename=filename)
                files.append(record)
                continue
            try:
                record["byte_count"] = file_path.stat().st_size
                record["sha256"] = _sha256(file_path)
            except OSError as exc:
                _record_problem(problems, "file-read-error", f"{filename} could not be inspected: {exc}", filename=filename)
                files.append(record)
                continue
            if filename.endswith(".json"):
                payload, error = _json_payload(file_path)
                if error:
                    _record_problem(problems, "invalid-json", error, filename=filename)
                else:
                    payload = payload or {}
                    json_payloads[filename] = payload
                    kind = _text(payload.get("kind"))
                    record["json_kind"] = kind
                    expected_kind = _EXPECTED_JSON_KINDS.get(filename)
                    if expected_kind and kind != expected_kind:
                        _record_problem(problems, "unexpected-kind", f"{filename} kind is {kind!r}, expected {expected_kind!r}.", filename=filename)
            files.append(record)

    if manifest:
        summary = _mapping(manifest.get("summary"))
        manifest_files = set(_manifest_filenames(manifest))
        for filename in sorted(set(_REQUIRED_FILENAMES) - {"runtime-smoke-artifacts-manifest.json"} - manifest_files):
            _record_problem(problems, "manifest-missing-required-file", f"{filename} is required but not listed in the manifest.", filename=filename)
        existing_count = sum(1 for item in files if item.get("exists"))
        manifest_count = int(summary.get("written_file_count") or summary.get("file_count") or 0)
        if manifest_count and manifest_count != existing_count:
            _record_problem(problems, "file-count-mismatch", f"Manifest file count is {manifest_count}, but {existing_count} artifact files were found.")
        capabilities = _mapping(manifest.get("capabilities"))
        if capabilities and capabilities.get("opens_window") is not False:
            _record_problem(problems, "manifest-opens-window", "Manifest must declare opens_window=False.")
        if capabilities and capabilities.get("executes_commands") is not False:
            _record_problem(problems, "manifest-executes-commands", "Manifest must declare executes_commands=False.")
        if capabilities and capabilities.get("requires_pyside6") is not False:
            _record_problem(problems, "manifest-requires-pyside6", "Manifest verification path must not require PySide6.")
        privacy = _mapping(manifest.get("privacy"))
        if privacy and privacy.get("shareable_export_redacts_evidence_paths") is not True:
            _record_problem(problems, "manifest-redaction-missing", "Manifest must declare shareable export evidence-path redaction.")

    shareable_export = json_payloads.get("runtime-smoke-shareable-export.json")
    if shareable_export is not None:
        privacy = _mapping(shareable_export.get("privacy"))
        if privacy.get("evidence_paths_redacted") is not True:
            _record_problem(problems, "export-redaction-missing", "Shareable export must declare evidence_paths_redacted=True.", filename="runtime-smoke-shareable-export.json")
        if _contains_key(shareable_export, "evidence_path"):
            _record_problem(problems, "export-evidence-path-leak", "Shareable export must not contain raw evidence_path keys.", filename="runtime-smoke-shareable-export.json")
        for key in ("contains_face_crops", "contains_embeddings", "contains_media_file_contents"):
            if privacy.get(key) not in (False, None):
                _record_problem(problems, "export-sensitive-media-flag", f"Shareable export privacy flag {key} must be False.", filename="runtime-smoke-shareable-export.json")

    plan = json_payloads.get("runtime-smoke-plan.json")
    if plan is not None:
        capabilities = _mapping(plan.get("capabilities"))
        if capabilities.get("opens_window") is not False:
            _record_problem(problems, "plan-opens-window", "Guarded plan must declare opens_window=False.", filename="runtime-smoke-plan.json")
        if capabilities.get("executes_commands") is not False:
            _record_problem(problems, "plan-executes-commands", "Guarded plan must declare executes_commands=False.", filename="runtime-smoke-plan.json")
        if capabilities.get("requires_pyside6") is not False:
            _record_problem(problems, "plan-requires-pyside6", "Guarded plan must declare requires_pyside6=False.", filename="runtime-smoke-plan.json")

    result_report = json_payloads.get("runtime-smoke-result-payload-report.json")
    if result_report is not None:
        summary = _mapping(result_report.get("summary"))
        if summary.get("opens_window") is not False:
            _record_problem(problems, "result-report-opens-window", "Result payload report must declare opens_window=False.", filename="runtime-smoke-result-payload-report.json")
        if summary.get("executes_commands") is not False:
            _record_problem(problems, "result-report-executes-commands", "Result payload report must declare executes_commands=False.", filename="runtime-smoke-result-payload-report.json")

    ok = not any(item.get("severity") == "error" for item in problems)
    return {
        "schema_version": QT_RUNTIME_SMOKE_ARTIFACT_VERIFICATION_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_local_artifact_pack_verification",
        "path": str(target),
        "ok": ok,
        "summary": {
            "exists": exists,
            "is_dir": is_dir,
            "file_count": len(files),
            "existing_file_count": sum(1 for item in files if item.get("exists")),
            "json_file_count": sum(1 for item in files if str(item.get("filename", "")).endswith(".json")),
            "problem_count": len(problems),
            "warning_count": len(warnings),
            "privacy_redaction_ok": shareable_export is not None and _mapping(shareable_export.get("privacy")).get("evidence_paths_redacted") is True and not _contains_key(shareable_export, "evidence_path"),
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "files": files,
        "problems": problems,
        "warnings": warnings,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
            "reads_evidence_files": False,
        },
    }


def summarize_qt_runtime_smoke_local_artifact_pack_verification(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    lines = [
        "Qt Runtime Smoke artifact verification",
        f"  Path: {_text(report.get('path'), '<unknown>')}",
        f"  OK: {report.get('ok')}",
        f"  Files: {summary.get('existing_file_count', 0)}/{summary.get('file_count', 0)}",
        f"  Problems: {summary.get('problem_count', 0)}",
        f"  Privacy redaction OK: {summary.get('privacy_redaction_ok')}",
        f"  Opens window now: {summary.get('opens_window')}",
        f"  Executes commands now: {summary.get('executes_commands')}",
    ]
    for problem in _list(report.get("problems"))[:5]:
        item = _mapping(problem)
        filename = _text(item.get("filename"))
        suffix = f" ({filename})" if filename else ""
        lines.append(f"  - {item.get('code')}: {item.get('message')}{suffix}")
    return "\n".join(lines)


def write_qt_runtime_smoke_local_artifact_pack_verification_report(
    path: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    report = verify_qt_runtime_smoke_local_artifact_pack_dir(path)
    target = Path(output_dir) if output_dir is not None else Path(path)
    if target.exists() and not target.is_dir():
        raise NotADirectoryError(f"Runtime Smoke verification report target is not a directory: {target}")
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "runtime-smoke-artifacts-verification.json"
    text_path = target / "runtime-smoke-artifacts-verification.txt"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    text_path.write_text(summarize_qt_runtime_smoke_local_artifact_pack_verification(report) + "\n", encoding="utf-8")
    return {
        **dict(report),
        "verification_report_files": [str(json_path), str(text_path)],
        "summary": {
            **dict(_mapping(report.get("summary"))),
            "verification_report_file_count": 2,
        },
    }


def load_qt_runtime_smoke_local_artifact_pack_verification(path: str | Path) -> dict[str, object]:
    return verify_qt_runtime_smoke_local_artifact_pack_dir(path)


__all__ = [
    "QT_RUNTIME_SMOKE_ARTIFACT_VERIFICATION_SCHEMA_VERSION",
    "load_qt_runtime_smoke_local_artifact_pack_verification",
    "summarize_qt_runtime_smoke_local_artifact_pack_verification",
    "verify_qt_runtime_smoke_local_artifact_pack_dir",
    "write_qt_runtime_smoke_local_artifact_pack_verification_report",
]
