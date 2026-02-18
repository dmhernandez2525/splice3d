"""Validation helpers for F5.3 custom profile editor acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f5_3"
    / "spec"
    / "custom_profile_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_operations(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"create", "modify", "delete", "read"}
    declared = set(spec.get("operations", []))
    for op in sorted(required - declared):
        errors.append(f"Missing operation: {op}")
    return errors


def validate_persistence_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"magic", "index", "checksum", "profile_data"}
    declared = set(spec.get("persistence_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing persistence field: {f}")
    return errors


def validate_slot_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"header", "profile", "occupied"}
    declared = set(spec.get("slot_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing slot field: {f}")
    return errors


def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"totalSlots", "usedSlots", "freeSlots", "corruptSlots"}
    declared = set(spec.get("stats_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing stats field: {f}")
    return errors


def validate_checksum(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    algo = spec.get("checksum_algorithm", "")
    if not algo:
        errors.append("Checksum algorithm not specified")
    magic = spec.get("profile_magic", 0)
    if magic < 1 or magic > 255:
        errors.append(f"Profile magic byte out of range: {magic}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "create_custom_profile",
        "modify_custom_profile",
        "delete_custom_profile",
        "eeprom_persistence",
        "checksum_validation",
        "corruption_detection",
        "slot_management",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "operations": validate_operations(spec),
        "persistence_fields": validate_persistence_fields(spec),
        "slot_fields": validate_slot_fields(spec),
        "stats_fields": validate_stats_fields(spec),
        "checksum": validate_checksum(spec),
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
