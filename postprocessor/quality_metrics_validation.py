"""Validation helpers for F4.2 quality metrics acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f4_2"
    / "spec"
    / "quality_metrics_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_per_material_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"attempts", "successes", "avgQuality", "avgSpliceTimeMs"}
    declared = set(spec.get("per_material_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing per-material field: {f}")
    return errors


def validate_snapshot_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "totalSplices", "totalSuccesses", "totalFailures",
        "overallSuccessRate", "overallAvgQuality", "perMaterial", "trend",
    }
    declared = set(spec.get("snapshot_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing snapshot field: {f}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "per_material_tracking", "quality_trend_analysis",
        "success_rate_calculation", "running_averages",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def validate_config(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    max_mat = spec.get("max_materials", 0)
    if max_mat < 2 or max_mat > 16:
        errors.append(f"max_materials out of range: {max_mat}")
    hist = spec.get("quality_history_size", 0)
    if hist < 8 or hist > 256:
        errors.append(f"quality_history_size out of range: {hist}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "per_material_fields": validate_per_material_fields(spec),
        "snapshot_fields": validate_snapshot_fields(spec),
        "features": validate_features(spec),
        "config": validate_config(spec),
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
