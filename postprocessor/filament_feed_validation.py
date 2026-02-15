"""Validation helpers for F3.1 filament feeding acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f3_1"
    / "spec"
    / "filament_feed_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_acceptance_limits(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    limits = spec.get("acceptance_limits", {})
    variance = limits.get("feed_rate_variance_pct", 0)
    if variance <= 0 or variance > 20:
        errors.append(f"feed_rate_variance_pct out of range: {variance}")
    jam_dist = limits.get("jam_detection_distance_mm", 0)
    if jam_dist < 10 or jam_dist > 200:
        errors.append(f"jam_detection_distance_mm out of range: {jam_dist}")
    fast = limits.get("fast_speed_mm_s", 0)
    if fast < 5 or fast > 100:
        errors.append(f"fast_speed_mm_s out of range: {fast}")
    return errors


def validate_feed_modes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"IDLE", "FEED_A", "FEED_B", "RETRACT_A", "RETRACT_B", "DRY_RUN", "LOADING"}
    declared = set(spec.get("feed_modes", []))
    for mode in sorted(required - declared):
        errors.append(f"Missing feed mode: {mode}")
    return errors


def validate_safety_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "filament_runout_detection",
        "jam_detection",
        "cold_extrusion_prevention",
        "encoder_based_tension_monitoring",
        "emergency_abort",
    }
    declared = set(spec.get("safety_features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing safety feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "acceptance_limits": validate_acceptance_limits(spec),
        "feed_modes": validate_feed_modes(spec),
        "safety_features": validate_safety_features(spec),
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
