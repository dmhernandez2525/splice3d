"""Validation helpers for F5.2 cross-material splicing acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f5_2"
    / "spec"
    / "cross_material_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_compat_levels(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"INCOMPATIBLE", "POOR", "FAIR", "GOOD", "EXCELLENT"}
    declared = set(spec.get("compat_levels", []))
    for lvl in sorted(required - declared):
        errors.append(f"Missing compatibility level: {lvl}")
    return errors


def validate_material_pairs(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pairs = spec.get("material_pairs", [])
    valid_types = {"PLA", "PETG", "ABS", "TPU"}
    valid_levels = {"INCOMPATIBLE", "POOR", "FAIR", "GOOD", "EXCELLENT"}
    if len(pairs) < 6:
        errors.append(
            f"Expected at least 6 material pairs, got {len(pairs)}"
        )
    for pair in pairs:
        a = pair.get("a", "")
        b = pair.get("b", "")
        level = pair.get("level", "")
        if a not in valid_types:
            errors.append(f"Invalid material type in pair: {a}")
        if b not in valid_types:
            errors.append(f"Invalid material type in pair: {b}")
        if level not in valid_levels:
            errors.append(f"Invalid compat level for {a}+{b}: {level}")
    return errors


def validate_override_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"spliceTemp", "holdTimeMs", "compressionMm", "coolTimeMs"}
    declared = set(spec.get("override_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing override field: {f}")
    return errors


def validate_score_range(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    score = spec.get("score_range", {})
    if score.get("min", -1) != 0:
        errors.append("Score range min must be 0")
    if score.get("max", -1) != 100:
        errors.append("Score range max must be 100")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "compatibility_matrix",
        "compatibility_scoring",
        "temperature_time_overrides",
        "same_type_always_excellent",
        "bidirectional_lookup",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "compat_levels": validate_compat_levels(spec),
        "material_pairs": validate_material_pairs(spec),
        "override_fields": validate_override_fields(spec),
        "score_range": validate_score_range(spec),
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
