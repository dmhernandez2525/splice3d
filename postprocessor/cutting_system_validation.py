"""Validation helpers for F2.4 cutting system acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f2_4"
    / "spec"
    / "cutting_system_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    """Load the cutting system validation spec."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_acceptance_limits(spec: dict[str, Any]) -> list[str]:
    """Check acceptance limit values are within reasonable ranges."""
    errors: list[str] = []
    limits = spec.get("acceptance_limits", {})

    travel = limits.get("servo_travel_ms", 0)
    if travel < 50 or travel > 2000:
        errors.append(f"servo_travel_ms out of range: {travel}")

    response = limits.get("manual_override_response_ms", 0)
    if response < 100 or response > 5000:
        errors.append(f"manual_override_response_ms out of range: {response}")

    interval = limits.get("maintenance_interval_cuts", 0)
    if interval < 50 or interval > 10000:
        errors.append(f"maintenance_interval_cuts out of range: {interval}")

    force = limits.get("max_force_threshold", 0)
    if force < 50 or force > 1023:
        errors.append(f"max_force_threshold out of range: {force}")

    retract = limits.get("pre_cut_retract_mm", 0)
    if retract < 0 or retract > 10:
        errors.append(f"pre_cut_retract_mm out of range: {retract}")

    return errors


def validate_cut_phases(spec: dict[str, Any]) -> list[str]:
    """Verify all required cut phases are declared."""
    errors: list[str] = []
    required = {"IDLE", "RETRACTING", "CLOSING", "HOLDING", "OPENING", "VERIFYING", "DONE"}
    declared = set(spec.get("cut_phases", []))
    for phase in sorted(required - declared):
        errors.append(f"Missing cut phase: {phase}")
    return errors


def validate_safety_features(spec: dict[str, Any]) -> list[str]:
    """Verify all required safety features are declared."""
    errors: list[str] = []
    required = {
        "pre_cut_retraction",
        "cut_verification_advance",
        "blade_wear_detection",
        "maintenance_alerts",
        "force_monitoring",
    }
    declared = set(spec.get("safety_features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing safety feature: {feat}")
    return errors


def validate_eeprom_persistence(spec: dict[str, Any]) -> list[str]:
    """Verify EEPROM persistence configuration."""
    errors: list[str] = []
    eeprom = spec.get("eeprom_persistence", {})
    if "address" not in eeprom:
        errors.append("Missing EEPROM address")
    required_fields = {"totalCuts", "successfulCuts", "failedCuts", "lastMaintenanceCut"}
    declared_fields = set(eeprom.get("fields", []))
    for field in sorted(required_fields - declared_fields):
        errors.append(f"Missing EEPROM field: {field}")
    if not eeprom.get("checksum", False):
        errors.append("EEPROM checksum not enabled")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    """Run all validations and return a structured report."""
    checks = {
        "acceptance_limits": validate_acceptance_limits(spec),
        "cut_phases": validate_cut_phases(spec),
        "safety_features": validate_safety_features(spec),
        "eeprom_persistence": validate_eeprom_persistence(spec),
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
