"""Validation helpers for F6.1 segment batching acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f6_1"
    / "spec"
    / "segment_batching_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_strategies(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"NONE", "GROUP_BY_MATERIAL", "MINIMIZE_CHANGES", "MINIMIZE_HEATING"}
    declared = set(spec.get("strategies", []))
    for strat in sorted(required - declared):
        errors.append(f"Missing strategy: {strat}")
    return errors


def validate_segment_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "segmentId", "material", "lengthMm", "originalOrder",
        "batchedOrder", "processed", "active",
    }
    declared = set(spec.get("segment_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing segment field: {field}")
    return errors


def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "totalSegments", "reorderedSegments", "materialChanges",
        "materialChangesSaved", "heatingCyclesSaved", "reorderRatio",
    }
    declared = set(spec.get("stats_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing stats field: {field}")
    return errors


def validate_reorder_ratio_range(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ratio = spec.get("reorder_ratio_range", {})
    if ratio.get("min", -1) != 0.0:
        errors.append("Reorder ratio min must be 0.0")
    if ratio.get("max", -1) != 1.0:
        errors.append("Reorder ratio max must be 1.0")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "segment_queue",
        "material_grouping",
        "change_minimization",
        "heating_cycle_optimization",
        "reorder_statistics",
        "serial_serialization",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "strategies": validate_strategies(spec),
        "segment_fields": validate_segment_fields(spec),
        "stats_fields": validate_stats_fields(spec),
        "reorder_ratio_range": validate_reorder_ratio_range(spec),
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
