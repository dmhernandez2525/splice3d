"""Validation helpers for F7.4 slicer bambu acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f7_4"
    / "spec"
    / "slicer_bambu_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_ams_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['brand', 'colorHex', 'filamentType', 'remaining', 'slotIndex', 'unitIndex']
    declared = set(spec.get("ams_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing ams fields item: {item}")
    return errors

def validate_bambu_extensions(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['AMS_MAPPING', 'FILAMENT_CHANGE', 'FLUSH_END', 'FLUSH_START', 'WIPE_TOWER']
    declared = set(spec.get("bambu_extensions", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing bambu extensions item: {item}")
    return errors

def validate_plate_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['boundingBox', 'estimatedTimeMin', 'filamentCount', 'objectCount', 'plateIndex']
    declared = set(spec.get("plate_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing plate fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['amsUnitsDetected', 'filamentChanges', 'flushVolumeMl', 'parsedLines', 'platesProcessed']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['ams_metadata_extraction', 'bambu_gcode_parsing', 'flush_volume_tracking', 'plate_detection', 'proprietary_extension_handling', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "ams_fields": validate_ams_fields(spec),
        "bambu_extensions": validate_bambu_extensions(spec),
        "plate_fields": validate_plate_fields(spec),
        "stats_fields": validate_stats_fields(spec),
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
