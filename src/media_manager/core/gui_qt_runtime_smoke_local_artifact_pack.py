from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .gui_qt_runtime_smoke_export import build_qt_runtime_smoke_export_bundle
from .gui_qt_runtime_smoke_result_payload import (
    build_qt_runtime_smoke_result_collector_template,
    summarize_qt_runtime_smoke_result_payload_report,
)

QT_RUNTIME_SMOKE_LOCAL_ARTIFACT_PACK_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _json_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(dict(payload), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _has_evidence_paths(report: Mapping[str, Any]) -> bool:
    session = _mapping(report.get("session"))
    return any(bool(_mapping(result).get("evidence_path")) for result in _list(session.get("results")))


def build_qt_runtime_smoke_local_summary_text(
    plan: Mapping[str, Any],
    *,
    result_payload_report: Mapping[str, Any] | None = None,
) -> str:
    summary = _mapping(plan.get("summary"))
    smoke_report = _mapping(plan.get("smoke_report"))
    smoke_summary = _mapping(smoke_report.get("summary"))
    manual_readiness = _mapping(plan.get("manual_readiness"))
    capabilities = _mapping(plan.get("capabilities"))
    lines = [
        "Qt Runtime Smoke local artifact pack",
        f"  Ready for shell route: {summary.get('ready_for_shell_route')}",
        f"  Ready to start manual smoke: {summary.get('ready_to_start_manual_smoke')}",
        f"  Accepted after results: {summary.get('accepted_after_results')}",
        f"  Evidence complete: {smoke_summary.get('evidence_complete')}",
        f"  Problem count: {summary.get('problem_count', 0)}",
        f"  Route resolved: {summary.get('route_resolved')}",
        f"  Opens window now: {capabilities.get('opens_window', False)}",
        f"  Executes commands now: {capabilities.get('executes_commands', False)}",
        f"  Local only: {capabilities.get('local_only', True)}",
        f"  Manual readiness status: {manual_readiness.get('status')}",
    ]
    if result_payload_report is not None:
        lines.extend(["", summarize_qt_runtime_smoke_result_payload_report(result_payload_report)])
    return "\n".join(lines).rstrip() + "\n"


def build_qt_runtime_smoke_local_readme_text() -> str:
    return "\n".join(
        [
            "Qt Runtime Smoke local artifact pack",
            "",
            "This folder is generated headlessly and is safe to inspect without PySide6.",
            "It does not open a window and does not execute Runtime Smoke commands.",
            "",
            "Files:",
            "- runtime-smoke-plan.json: local guarded plan for the current shell model.",
            "- runtime-smoke-results-template.json: fill this after a manual Qt smoke run.",
            "- runtime-smoke-shareable-export.json: metadata-only export with evidence paths redacted.",
            "- runtime-smoke-result-payload-report.json: normalized result-file report, when provided.",
            "- runtime-smoke-summary.txt: compact operator summary.",
            "- runtime-smoke-artifacts-manifest.json: file manifest for this pack.",
            "",
            "Verify this pack:",
            "- Run media-manager-gui --runtime-smoke-artifacts-verify <this-folder> to verify the manifest, files, JSON kinds, privacy redaction, and no-execution guardrails.",
            "- Add --runtime-smoke-artifacts-verify-json for a machine-readable verification report.",
            "- Add --runtime-smoke-artifacts-verify-report-dir <folder> to write local verification proof files.",
            "",
            "Privacy:",
            "- The shareable export redacts evidence paths.",
            "- The verifier never dereferences evidence paths or reads media files.",
            "- The local guarded plan may include local operator metadata only.",
            "- No media contents, face crops, embeddings, or telemetry are written by this pack.",
            "",
        ]
    )


def _artifact_record(
    artifact_id: str,
    *,
    filename: str,
    artifact_type: str,
    payload_kind: object = None,
    local_only: bool = True,
    metadata_only: bool = True,
    evidence_paths_redacted: bool | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "artifact_id": artifact_id,
        "filename": filename,
        "artifact_type": artifact_type,
        "payload_kind": payload_kind,
        "local_only": bool(local_only),
        "metadata_only": bool(metadata_only),
        "contains_sensitive_media": False,
        "contains_face_crops": False,
        "contains_embeddings": False,
        "contains_media_file_contents": False,
    }
    if evidence_paths_redacted is not None:
        record["evidence_paths_redacted"] = bool(evidence_paths_redacted)
    return record


def build_qt_runtime_smoke_local_artifact_pack(
    plan: Mapping[str, Any],
    *,
    result_payload_report: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    smoke_report = _mapping(plan.get("smoke_report"))
    shareable_export = build_qt_runtime_smoke_export_bundle(smoke_report, include_results=True)
    result_template = build_qt_runtime_smoke_result_collector_template(plan)
    summary_text = build_qt_runtime_smoke_local_summary_text(plan, result_payload_report=result_payload_report)
    readme_text = build_qt_runtime_smoke_local_readme_text()
    files: list[dict[str, object]] = [
        _artifact_record(
            "guarded-plan",
            filename="runtime-smoke-plan.json",
            artifact_type="json",
            payload_kind=plan.get("kind"),
            metadata_only=not _has_evidence_paths(smoke_report),
            evidence_paths_redacted=False,
        ),
        _artifact_record(
            "results-template",
            filename="runtime-smoke-results-template.json",
            artifact_type="json",
            payload_kind=result_template.get("kind"),
        ),
        _artifact_record(
            "shareable-export",
            filename="runtime-smoke-shareable-export.json",
            artifact_type="json",
            payload_kind=shareable_export.get("kind"),
            evidence_paths_redacted=True,
        ),
        _artifact_record(
            "summary",
            filename="runtime-smoke-summary.txt",
            artifact_type="text",
            payload_kind="qt_runtime_smoke_local_summary_text",
        ),
        _artifact_record(
            "readme",
            filename="README.txt",
            artifact_type="text",
            payload_kind="qt_runtime_smoke_local_readme_text",
        ),
    ]
    if result_payload_report is not None:
        files.append(
            _artifact_record(
                "result-payload-report",
                filename="runtime-smoke-result-payload-report.json",
                artifact_type="json",
                payload_kind=result_payload_report.get("kind"),
                metadata_only=True,
                evidence_paths_redacted=False,
            )
        )
    manifest = {
        "schema_version": QT_RUNTIME_SMOKE_LOCAL_ARTIFACT_PACK_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_local_artifact_pack_manifest",
        "files": files,
        "summary": {
            "file_count": len(files) + 1,
            "json_file_count": sum(1 for item in files if item.get("artifact_type") == "json") + 1,
            "text_file_count": sum(1 for item in files if item.get("artifact_type") == "text"),
            "has_result_payload_report": result_payload_report is not None,
            "ready_to_start_manual_smoke": _mapping(plan.get("summary")).get("ready_to_start_manual_smoke"),
            "accepted_after_results": _mapping(plan.get("summary")).get("accepted_after_results"),
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "privacy": {
            "metadata_only": all(bool(item.get("metadata_only")) for item in files if item.get("artifact_id") != "guarded-plan"),
            "contains_face_crops": False,
            "contains_embeddings": False,
            "contains_media_file_contents": False,
            "shareable_export_redacts_evidence_paths": True,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
            "writes_files": True,
        },
    }
    payloads: dict[str, object] = {
        "runtime-smoke-plan.json": dict(plan),
        "runtime-smoke-results-template.json": result_template,
        "runtime-smoke-shareable-export.json": shareable_export,
        "runtime-smoke-summary.txt": summary_text,
        "README.txt": readme_text,
        "runtime-smoke-artifacts-manifest.json": manifest,
    }
    if result_payload_report is not None:
        payloads["runtime-smoke-result-payload-report.json"] = dict(result_payload_report)
    return {
        "schema_version": QT_RUNTIME_SMOKE_LOCAL_ARTIFACT_PACK_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_local_artifact_pack",
        "manifest": manifest,
        "payloads": payloads,
        "summary_text": summary_text,
        "readme_text": readme_text,
        "summary": dict(_mapping(manifest.get("summary"))),
        "privacy": dict(_mapping(manifest.get("privacy"))),
        "capabilities": dict(_mapping(manifest.get("capabilities"))),
    }


def summarize_qt_runtime_smoke_local_artifact_pack(pack: Mapping[str, Any]) -> str:
    summary = _mapping(pack.get("summary"))
    return "\n".join(
        [
            "Qt Runtime Smoke local artifacts",
            f"  Files: {summary.get('file_count', 0)}",
            f"  JSON files: {summary.get('json_file_count', 0)}",
            f"  Text files: {summary.get('text_file_count', 0)}",
            f"  Has result payload report: {summary.get('has_result_payload_report')}",
            f"  Ready to start manual smoke: {summary.get('ready_to_start_manual_smoke')}",
            f"  Accepted after results: {summary.get('accepted_after_results')}",
            f"  Opens window now: {summary.get('opens_window')}",
            f"  Executes commands now: {summary.get('executes_commands')}",
        ]
    )


def write_qt_runtime_smoke_local_artifact_pack(
    plan: Mapping[str, Any],
    output_dir: str | Path,
    *,
    result_payload_report: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    target = Path(output_dir)
    if target.exists() and not target.is_dir():
        raise NotADirectoryError(f"Runtime Smoke artifact target is not a directory: {target}")
    target.mkdir(parents=True, exist_ok=True)
    pack = build_qt_runtime_smoke_local_artifact_pack(plan, result_payload_report=result_payload_report)
    payloads = _mapping(pack.get("payloads"))
    written: list[str] = []
    for filename, payload in sorted(payloads.items()):
        path = target / str(filename)
        if isinstance(payload, Mapping):
            path.write_text(_json_text(payload), encoding="utf-8")
        else:
            path.write_text(str(payload), encoding="utf-8")
        written.append(str(path))
    manifest = dict(_mapping(pack.get("manifest")))
    manifest["output_dir"] = str(target)
    manifest["written_files"] = written
    manifest["summary"] = {**dict(_mapping(manifest.get("summary"))), "written_file_count": len(written)}
    (target / "runtime-smoke-artifacts-manifest.json").write_text(_json_text(manifest), encoding="utf-8")
    return {**dict(pack), "manifest": manifest, "summary": dict(_mapping(manifest.get("summary"))), "written_files": written}


__all__ = [
    "QT_RUNTIME_SMOKE_LOCAL_ARTIFACT_PACK_SCHEMA_VERSION",
    "build_qt_runtime_smoke_local_artifact_pack",
    "build_qt_runtime_smoke_local_readme_text",
    "build_qt_runtime_smoke_local_summary_text",
    "summarize_qt_runtime_smoke_local_artifact_pack",
    "write_qt_runtime_smoke_local_artifact_pack",
]
