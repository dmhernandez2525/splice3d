"""Validation helpers for F5.1 material database acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f5_1"
    / "spec"
    / "material_database_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_material_types(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"PLA", "PETG", "ABS", "TPU"}
    declared = set(spec.get("material_types", []))
    for t in sorted(required - declared):
        errors.append(f"Missing material type: {t}")
    return errors


def validate_profile_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "name", "brand", "type", "spliceTemp",
        "holdTimeMs", "compressionMm", "coolTimeMs",
        "pullTestForceN", "active",
    }
    declared = set(spec.get("profile_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing profile field: {f}")
    return errors


def validate_default_profiles(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    defaults = spec.get("default_profiles", [])
    if len(defaults) < 4:
        errors.append(
            f"Expected at least 4 default profiles, got {len(defaults)}"
        )
    # Each material type should have at least one default.
    types_covered = set()
    for name in defaults:
        prefix = name.split("-")[0] if "-" in name else ""
        if prefix in {"PLA", "PETG", "ABS", "TPU"}:
            types_covered.add(prefix)
    for t in {"PLA", "PETG", "ABS", "TPU"} - types_covered:
        errors.append(f"No default profile for material type: {t}")
    return errors


def validate_temperature_limits(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    limits = spec.get("temperature_limits", {})
    min_c = limits.get("min_celsius", 0)
    max_c = limits.get("max_celsius", 0)
    if min_c < 100:
        errors.append(f"Min temperature too low: {min_c}")
    if max_c > 350:
        errors.append(f"Max temperature too high: {max_c}")
    if min_c >= max_c:
        errors.append("Min temperature must be less than max temperature")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "brand_specific_profiles",
        "lookup_by_type_and_brand",
        "lookup_by_name",
        "add_update_remove",
        "serial_serialization",
        "default_material_loading",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "material_types": validate_material_types(spec),
        "profile_fields": validate_profile_fields(spec),
        "default_profiles": validate_default_profiles(spec),
        "temperature_limits": validate_temperature_limits(spec),
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
