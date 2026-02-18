"""Validation helpers for F6.3 waste reduction acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f6_3"
    / "spec"
    / "waste_tracker_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_waste_categories(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"PURGE", "TRANSITION", "FAILED_SPLICE", "TIP_SHAPING"}
    declared = set(spec.get("waste_categories", []))
    for cat in sorted(required - declared):
        errors.append(f"Missing waste category: {cat}")
    return errors


def validate_record_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "spliceId", "material", "category", "wasteMm",
        "wasteGrams", "timestampMs", "active",
    }
    declared = set(spec.get("record_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing record field: {field}")
    return errors


def validate_analytics_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "totalWasteMm", "totalWasteGrams", "avgWastePerSpliceMm",
        "purgeWasteMm", "transitionWasteMm", "failedWasteMm",
        "tipShapingWasteMm", "totalRecords", "failedSplices",
        "wasteReductionPct",
    }
    declared = set(spec.get("analytics_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing analytics field: {field}")
    return errors


def validate_recommendation_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "worstCategory", "worstCategoryMm", "potentialSavingMm",
        "hasRecommendation",
    }
    declared = set(spec.get("recommendation_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing recommendation field: {field}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "per_splice_waste_tracking",
        "category_breakdown",
        "material_breakdown",
        "waste_analytics",
        "reduction_recommendations",
        "serial_serialization",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "waste_categories": validate_waste_categories(spec),
        "record_fields": validate_record_fields(spec),
        "analytics_fields": validate_analytics_fields(spec),
        "recommendation_fields": validate_recommendation_fields(spec),
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
