"""Validation helpers for F3.4 error recovery acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f3_4"
    / "spec"
    / "error_recovery_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_recovery_phases(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "IDLE", "ASSESSING", "COOLDOWN_WAIT", "RETRYING",
        "AWAITING_USER", "RESOLVED", "UNRECOVERABLE",
    }
    declared = set(spec.get("recovery_phases", []))
    for phase in sorted(required - declared):
        errors.append(f"Missing recovery phase: {phase}")
    return errors


def validate_error_categories(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_cats = {"temperature", "motor", "filament", "cutter", "critical"}
    categories = spec.get("error_categories", {})
    for cat in sorted(required_cats - set(categories.keys())):
        errors.append(f"Missing error category: {cat}")
    for cat, codes in categories.items():
        if not codes:
            errors.append(f"Empty error category: {cat}")
    return errors


def validate_config_defaults(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cfg = spec.get("config_defaults", {})
    retries = cfg.get("max_retries", 0)
    if retries < 1 or retries > 10:
        errors.append(f"max_retries out of range: {retries}")
    cd_ms = cfg.get("cooldown_timeout_ms", 0)
    if cd_ms < 5000 or cd_ms > 300000:
        errors.append(f"cooldown_timeout_ms out of range: {cd_ms}")
    cd_c = cfg.get("cooldown_target_c", 0)
    if cd_c < 30 or cd_c > 100:
        errors.append(f"cooldown_target_c out of range: {cd_c}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "automatic_retry", "cooldown_recovery",
        "user_guided_recovery", "recovery_statistics",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "recovery_phases": validate_recovery_phases(spec),
        "error_categories": validate_error_categories(spec),
        "config_defaults": validate_config_defaults(spec),
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
