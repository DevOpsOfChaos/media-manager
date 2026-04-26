from __future__ import annotations

from collections.abc import Iterable

COMMAND_RECIPE_SCHEMA_VERSION = "1.0"


def _text(value: object, default: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _append_repeated(parts: list[str], flag: str, values: Iterable[object] | None) -> None:
    for value in values or ():
        text = _text(value)
        if text:
            parts.extend([flag, text])


def build_command_recipe(recipe_id: str, argv: list[str], *, title: str = "", risk_level: str = "safe", sensitive: bool = False) -> dict[str, object]:
    return {
        "schema_version": COMMAND_RECIPE_SCHEMA_VERSION,
        "kind": "command_recipe",
        "recipe_id": _text(recipe_id, "recipe"),
        "title": title or recipe_id.replace("_", " ").title(),
        "argv": list(argv),
        "command_preview": " ".join(f'"{part}"' if " " in part else part for part in argv),
        "risk_level": risk_level,
        "sensitive": bool(sensitive),
        "executes_immediately": False,
        "requires_confirmation": risk_level in {"high", "destructive"} or sensitive,
    }


def people_scan_recipe(*, sources: Iterable[object], catalog: object | None = None, backend: str = "auto", report_json: object | None = None, include_encodings: bool = False) -> dict[str, object]:
    argv = ["media-manager", "people", "scan"]
    _append_repeated(argv, "--source", sources)
    if catalog:
        argv.extend(["--catalog", _text(catalog)])
    if backend:
        argv.extend(["--backend", backend])
    if report_json:
        argv.extend(["--report-json", _text(report_json)])
    if include_encodings:
        argv.append("--include-encodings")
    return build_command_recipe("people_scan", argv, title="People scan preview", risk_level="safe", sensitive=include_encodings)


def people_review_bundle_recipe(*, report_json: object, bundle_dir: object, workflow_json: object | None = None, catalog: object | None = None) -> dict[str, object]:
    argv = ["media-manager", "people", "review-bundle", "--report-json", _text(report_json), "--bundle-dir", _text(bundle_dir)]
    if workflow_json:
        argv.extend(["--workflow-json", _text(workflow_json)])
    if catalog:
        argv.extend(["--catalog", _text(catalog)])
    return build_command_recipe("people_review_bundle", argv, title="Build people review bundle", risk_level="safe")


def people_review_apply_preview_recipe(*, catalog: object, workflow_json: object, report_json: object) -> dict[str, object]:
    argv = ["media-manager-app-services", "people-review-preview", "--catalog", _text(catalog), "--workflow-json", _text(workflow_json), "--report-json", _text(report_json)]
    return build_command_recipe("people_review_apply_preview", argv, title="Preview people catalog update", risk_level="medium")


__all__ = [
    "COMMAND_RECIPE_SCHEMA_VERSION",
    "build_command_recipe",
    "people_scan_recipe",
    "people_review_bundle_recipe",
    "people_review_apply_preview_recipe",
]
