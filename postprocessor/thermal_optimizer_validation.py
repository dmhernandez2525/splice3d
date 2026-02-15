"""Validation helpers for F6.2 thermal optimization acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f6_2"
    / "spec"
    / "thermal_optimizer_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_thermal_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"IDLE", "PREHEATING", "AT_TEMP", "COOLING", "REUSING_HEAT"}
    declared = set(spec.get("thermal_states", []))
    for state in sorted(required - declared):
        errors.append(f"Missing thermal state: {state}")
    return errors


def validate_preheat_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "material", "targetTempC", "scheduledTimeMs",
        "started", "completed", "active",
    }
    declared = set(spec.get("preheat_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing preheat field: {field}")
    return errors


def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "totalPreheats", "successfulPreheats", "heatReuses",
        "totalSavedMs", "totalSavedDegrees", "thermalCyclesAvoided",
        "avgPreheatAccuracyC",
    }
    declared = set(spec.get("stats_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing stats field: {field}")
    return errors


def validate_thresholds(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if spec.get("heat_reuse_threshold_c", 0) <= 0:
        errors.append("Heat reuse threshold must be positive")
    if spec.get("preheat_lead_time_ms", 0) <= 0:
        errors.append("Preheat lead time must be positive")
    if spec.get("max_preheat_queue", 0) <= 0:
        errors.append("Max preheat queue must be positive")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "preheat_scheduling",
        "heat_reuse_detection",
        "thermal_cycle_minimization",
        "preheat_accuracy_tracking",
        "thermal_state_machine",
        "serial_serialization",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "thermal_states": validate_thermal_states(spec),
        "preheat_fields": validate_preheat_fields(spec),
        "stats_fields": validate_stats_fields(spec),
        "thresholds": validate_thresholds(spec),
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
