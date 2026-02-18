"""Validation helpers for F6.4 speed optimization acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f6_4"
    / "spec"
    / "speed_optimizer_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_op_types(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "HEATING", "FEEDING", "CUTTING",
        "SPLICING", "COOLING", "POSITIONING",
    }
    declared = set(spec.get("op_types", []))
    for op in sorted(required - declared):
        errors.append(f"Missing operation type: {op}")
    return errors


def validate_op_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"PENDING", "RUNNING", "COMPLETED", "CANCELLED"}
    declared = set(spec.get("op_states", []))
    for state in sorted(required - declared):
        errors.append(f"Missing operation state: {state}")
    return errors


def validate_overlap_pairs(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pairs = spec.get("overlap_pairs", [])
    valid_types = {"HEATING", "FEEDING", "CUTTING",
                   "SPLICING", "COOLING", "POSITIONING"}
    if len(pairs) < 2:
        errors.append(
            f"Expected at least 2 overlap pairs, got {len(pairs)}"
        )
    for pair in pairs:
        a = pair.get("a", "")
        b = pair.get("b", "")
        if a not in valid_types:
            errors.append(f"Invalid op type in overlap pair: {a}")
        if b not in valid_types:
            errors.append(f"Invalid op type in overlap pair: {b}")
        if a == b:
            errors.append(f"Overlap pair has same type on both sides: {a}")
    return errors


def validate_cycle_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "heatingMs", "feedingMs", "cuttingMs", "splicingMs",
        "coolingMs", "positioningMs", "totalMs", "overlapSavedMs",
        "cycleId", "complete",
    }
    declared = set(spec.get("cycle_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing cycle field: {field}")
    return errors


def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "totalCycles", "avgCycleMs", "bestCycleMs", "worstCycleMs",
        "totalOverlapSavedMs", "parallelOpsCount", "overlapRatio",
    }
    declared = set(spec.get("stats_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing stats field: {field}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "parallel_operation_scheduling",
        "overlap_detection",
        "cycle_time_breakdown",
        "cycle_history",
        "aggregate_statistics",
        "serial_serialization",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "op_types": validate_op_types(spec),
        "op_states": validate_op_states(spec),
        "overlap_pairs": validate_overlap_pairs(spec),
        "cycle_fields": validate_cycle_fields(spec),
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
