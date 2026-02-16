"""Validation helpers for F7.2 slicer prusa acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f7_2"
    / "spec"
    / "slicer_prusa_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_parse_modes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['MMU', 'MULTI_MATERIAL', 'SINGLE_EXTRUDER']
    declared = set(spec.get("parse_modes", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing parse modes item: {item}")
    return errors

def validate_mmu_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['filamentType', 'loadDistance', 'nozzleDiameter', 'purgeVolume', 'toolIndex', 'unloadDistance']
    declared = set(spec.get("mmu_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing mmu fields item: {item}")
    return errors

def validate_gcode_markers(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['filament_settings', 'layer_change_comment', 'mmu_wipe_tower', 'tool_change_Tn']
    declared = set(spec.get("gcode_markers", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing gcode markers item: {item}")
    return errors

def validate_recipe_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['colorCount', 'purgeVolumeMl', 'toolChangeCount', 'totalLayers', 'wipeEnabled']
    declared = set(spec.get("recipe_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing recipe fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['errorsEncountered', 'mmuDetected', 'parseComplete', 'parsedLines', 'toolChangesFound']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['mmu_detection', 'multi_material_config', 'prusa_gcode_parsing', 'purge_volume_tracking', 'recipe_generation', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "parse_modes": validate_parse_modes(spec),
        "mmu_fields": validate_mmu_fields(spec),
        "gcode_markers": validate_gcode_markers(spec),
        "recipe_fields": validate_recipe_fields(spec),
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
