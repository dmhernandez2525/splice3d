"""Validation helpers for F2.3 temperature control acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f2_3"
    / "spec"
    / "temperature_control_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    """Load the temperature control validation spec."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_acceptance_limits(spec: dict[str, Any]) -> list[str]:
    """Check acceptance limit values are within reasonable ranges."""
    errors: list[str] = []
    limits = spec.get("acceptance_limits", {})

    tolerance = limits.get("steady_state_tolerance_c", 0)
    if tolerance <= 0 or tolerance > 10:
        errors.append(f"steady_state_tolerance_c out of range: {tolerance}")

    runaway_s = limits.get("thermal_runaway_detection_s", 0)
    if runaway_s < 5 or runaway_s > 120:
        errors.append(f"thermal_runaway_detection_s out of range: {runaway_s}")

    max_temp = limits.get("max_temperature_c", 0)
    if max_temp < 250 or max_temp > 400:
        errors.append(f"max_temperature_c out of range: {max_temp}")

    cold_ext = limits.get("min_cold_extrusion_c", 0)
    if cold_ext < 100 or cold_ext > 200:
        errors.append(f"min_cold_extrusion_c out of range: {cold_ext}")

    return errors


def validate_material_profiles(spec: dict[str, Any]) -> list[str]:
    """Check all required material profiles exist with valid parameters."""
    errors: list[str] = []
    profiles = spec.get("material_profiles", {})
    required_materials = {"PLA", "PETG", "ABS"}

    for mat in required_materials:
        if mat not in profiles:
            errors.append(f"Missing material profile: {mat}")
            continue
        profile = profiles[mat]
        target = profile.get("splice_target_c", 0)
        if target < 180 or target > 300:
            errors.append(f"{mat} splice_target_c out of range: {target}")
        min_motion = profile.get("min_motion_c", 0)
        if min_motion < 150 or min_motion > target:
            errors.append(f"{mat} min_motion_c invalid: {min_motion}")
        ramp = profile.get("ramp_rate_c_per_s", 0)
        if ramp <= 0 or ramp > 10:
            errors.append(f"{mat} ramp_rate_c_per_s out of range: {ramp}")
        soak = profile.get("soak_time_ms", 0)
        if soak < 500 or soak > 10000:
            errors.append(f"{mat} soak_time_ms out of range: {soak}")

    return errors


def validate_safety_features(spec: dict[str, Any]) -> list[str]:
    """Verify all required safety features are declared."""
    errors: list[str] = []
    required = {
        "thermal_runaway_detection",
        "thermistor_disconnect_detection",
        "cold_extrusion_prevention",
        "overtemperature_shutoff",
        "pid_watchdog_timer",
        "cooling_fan_on_fault",
    }
    declared = set(spec.get("safety_features", []))
    missing = required - declared
    for feat in sorted(missing):
        errors.append(f"Missing safety feature: {feat}")
    return errors


def validate_heating_stages(spec: dict[str, Any]) -> list[str]:
    """Verify heating stage sequence is complete."""
    errors: list[str] = []
    required = {"OFF", "PREHEAT", "SOAK", "READY", "FAULT"}
    declared = set(spec.get("heating_stages", []))
    missing = required - declared
    for stage in sorted(missing):
        errors.append(f"Missing heating stage: {stage}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    """Run all validations and return a structured report."""
    checks = {
        "acceptance_limits": validate_acceptance_limits(spec),
        "material_profiles": validate_material_profiles(spec),
        "safety_features": validate_safety_features(spec),
        "heating_stages": validate_heating_stages(spec),
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
