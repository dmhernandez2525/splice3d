"""Validation helpers for F3.2 splice execution acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f3_2"
    / "spec"
    / "splice_execution_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_acceptance_limits(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    limits = spec.get("acceptance_limits", {})
    for mat in ("pla", "petg", "abs"):
        strength = limits.get(f"{mat}_bond_strength_n", 0)
        if strength < 5 or strength > 100:
            errors.append(f"{mat}_bond_strength_n out of range: {strength}")
    max_time = limits.get("max_splice_time_ms", 0)
    if max_time < 5000 or max_time > 120000:
        errors.append(f"max_splice_time_ms out of range: {max_time}")
    return errors


def validate_splice_phases(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "IDLE", "RETRACT_A", "ADVANCE_B", "HEATING",
        "COMPRESSING", "HOLDING", "COOLING", "VERIFYING",
        "COMPLETE", "FAILED",
    }
    declared = set(spec.get("splice_phases", []))
    for phase in sorted(required - declared):
        errors.append(f"Missing splice phase: {phase}")
    return errors


def validate_material_profiles(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    profiles = spec.get("material_profiles", {})
    for mat in ("PLA", "PETG", "ABS"):
        if mat not in profiles:
            errors.append(f"Missing material profile: {mat}")
            continue
        p = profiles[mat]
        if p.get("temperature_c", 0) < 180 or p.get("temperature_c", 0) > 300:
            errors.append(f"{mat} temperature_c out of range")
        if p.get("hold_time_ms", 0) < 500:
            errors.append(f"{mat} hold_time_ms too short")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "acceptance_limits": validate_acceptance_limits(spec),
        "splice_phases": validate_splice_phases(spec),
        "material_profiles": validate_material_profiles(spec),
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
