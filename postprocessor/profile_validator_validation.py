"""Validation helpers for F5.4 profile validation acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f5_4"
    / "spec"
    / "profile_validator_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_severity_levels(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"INFO", "WARNING", "ERROR", "CRITICAL"}
    declared = set(spec.get("severity_levels", []))
    for lvl in sorted(required - declared):
        errors.append(f"Missing severity level: {lvl}")
    return errors


def validate_validation_codes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "TEMP_TOO_LOW", "TEMP_TOO_HIGH",
        "HOLD_TIME_TOO_SHORT", "HOLD_TIME_TOO_LONG",
        "COMPRESSION_OUT_OF_RANGE",
        "PULL_FORCE_TOO_LOW", "PULL_FORCE_TOO_HIGH",
    }
    declared = set(spec.get("validation_codes", []))
    for code in sorted(required - declared):
        errors.append(f"Missing validation code: {code}")
    return errors


def validate_safety_limits(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    limits = spec.get("safety_limits", {})
    required_keys = {
        "temperature", "hold_time_ms", "compression_mm",
        "cool_time_ms", "pull_force_n",
    }
    declared = set(limits.keys())
    for key in sorted(required_keys - declared):
        errors.append(f"Missing safety limit category: {key}")
    for key in required_keys & declared:
        entry = limits[key]
        if "min" not in entry or "max" not in entry:
            errors.append(f"Safety limit {key} must have min and max")
        elif entry["min"] >= entry["max"]:
            errors.append(
                f"Safety limit {key}: min ({entry['min']}) must be "
                f"less than max ({entry['max']})"
            )
    return errors


def validate_test_phases(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "IDLE", "HEATING", "HOLDING", "COMPRESSING",
        "COOLING", "PULL_TEST", "COMPLETE", "FAILED",
    }
    declared = set(spec.get("test_phases", []))
    for phase in sorted(required - declared):
        errors.append(f"Missing test phase: {phase}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "profile_validation_against_limits",
        "severity_based_error_reporting",
        "configurable_safety_limits",
        "test_sequence_execution",
        "test_sequence_abort",
        "validation_before_test",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "severity_levels": validate_severity_levels(spec),
        "validation_codes": validate_validation_codes(spec),
        "safety_limits": validate_safety_limits(spec),
        "test_phases": validate_test_phases(spec),
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
