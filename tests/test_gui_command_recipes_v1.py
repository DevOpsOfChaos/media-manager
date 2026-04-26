from media_manager.core.gui_command_recipes import people_review_apply_preview_recipe, people_review_bundle_recipe, people_scan_recipe


def test_people_scan_recipe_is_non_executing_and_sensitive_when_encodings() -> None:
    recipe = people_scan_recipe(sources=["D:/Photos"], catalog="people.json", report_json="report.json", include_encodings=True)

    assert recipe["argv"][:3] == ["media-manager", "people", "scan"]
    assert "--include-encodings" in recipe["argv"]
    assert recipe["sensitive"] is True
    assert recipe["executes_immediately"] is False
    assert recipe["requires_confirmation"] is True


def test_people_review_bundle_recipe_contains_paths() -> None:
    recipe = people_review_bundle_recipe(report_json="report.json", bundle_dir="bundle", workflow_json="workflow.json")

    assert recipe["recipe_id"] == "people_review_bundle"
    assert "--bundle-dir" in recipe["argv"]
    assert recipe["risk_level"] == "safe"


def test_apply_preview_recipe_uses_app_services() -> None:
    recipe = people_review_apply_preview_recipe(catalog="people.json", workflow_json="workflow.json", report_json="report.json")

    assert recipe["argv"][0] == "media-manager-app-services"
    assert recipe["risk_level"] == "medium"
    assert recipe["executes_immediately"] is False
