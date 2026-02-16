"""Validation helpers for F8.1 recipe editor acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f8_1"
    / "spec"
    / "recipe_editor_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_segment_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['colorHex', 'holdTimeMs', 'index', 'lengthMm', 'materialIndex', 'spliceTemp', 'toolNumber']
    declared = set(spec.get("segment_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing segment fields item: {item}")
    return errors

def validate_recipe_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['createdAt', 'estimatedTimeMin', 'name', 'segmentCount', 'totalLengthMm', 'validated']
    declared = set(spec.get("recipe_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing recipe fields item: {item}")
    return errors

def validate_edit_operations(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['add_segment', 'duplicate_segment', 'modify_segment', 'remove_segment', 'reorder_segment']
    declared = set(spec.get("edit_operations", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing edit operations item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['activeRecipe', 'lastEditTimestamp', 'totalRecipes', 'totalSegments', 'validationErrors']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['material_assignment', 'recipe_creation', 'recipe_serialization', 'recipe_validation', 'segment_management', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "segment_fields": validate_segment_fields(spec),
        "recipe_fields": validate_recipe_fields(spec),
        "edit_operations": validate_edit_operations(spec),
        "stats_fields": validate_stats_fields(spec),
        "features": validate_features(spec),
    }
    all_errors: list[str] = []
    for errs in checks.values():
        all_errors.extend(errs)
    return {
        "passed": len(all_errors) == 0,
        "error_count": len(all_errors),
        "checks": checks,
        "errors": all_errors,
    }
