"""Validation helpers for F3.3 position tracking acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f3_3"
    / "spec"
    / "position_tracking_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_tracking_parameters(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    params = spec.get("tracking_parameters", {})
    interval = params.get("update_interval_ms", 0)
    if interval < 50 or interval > 5000:
        errors.append(f"update_interval_ms out of range: {interval}")
    max_wp = params.get("max_waypoints", 0)
    if max_wp < 1 or max_wp > 256:
        errors.append(f"max_waypoints out of range: {max_wp}")
    max_de = params.get("max_drift_events", 0)
    if max_de < 1 or max_de > 256:
        errors.append(f"max_drift_events out of range: {max_de}")
    return errors


def validate_drift_thresholds(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    thresholds = spec.get("drift_thresholds", {})
    minor = thresholds.get("minor_mm", 0)
    moderate = thresholds.get("moderate_mm", 0)
    severe = thresholds.get("severe_mm", 0)
    if minor <= 0:
        errors.append(f"minor_mm must be positive: {minor}")
    if moderate <= minor:
        errors.append("moderate_mm must exceed minor_mm")
    if severe <= moderate:
        errors.append("severe_mm must exceed moderate_mm")
    return errors


def validate_snapshot_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "encoderMm", "motorAMm", "motorBMm", "driftMm",
        "cumulativeDriftMm", "velocityMmPerSec", "elapsedMs",
    }
    declared = set(spec.get("required_snapshot_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing snapshot field: {field}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "job_level_tracking", "waypoint_management",
        "drift_event_logging", "motor_encoder_reconciliation",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "tracking_parameters": validate_tracking_parameters(spec),
        "drift_thresholds": validate_drift_thresholds(spec),
        "snapshot_fields": validate_snapshot_fields(spec),
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
