"""Validation helpers for F7.3 slicer cura acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f7_3"
    / "spec"
    / "slicer_cura_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_extruder_modes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['DUAL', 'MULTI', 'SINGLE']
    declared = set(spec.get("extruder_modes", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing extruder modes item: {item}")
    return errors

def validate_block_types(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['END_GCODE', 'PRIME_TOWER', 'PRINT_BODY', 'START_GCODE', 'TOOL_CHANGE']
    declared = set(spec.get("block_types", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing block types item: {item}")
    return errors

def validate_plugin_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['author', 'curaVersion', 'description', 'marketplaceId', 'pluginName', 'version']
    declared = set(spec.get("plugin_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing plugin fields item: {item}")
    return errors

def validate_gcode_patterns(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['T_command', 'extruder_switch', 'layer_comment', 'mesh_name']
    declared = set(spec.get("gcode_patterns", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing gcode patterns item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['blocksIdentified', 'errorsEncountered', 'parsedLines', 'pluginLoaded', 'toolChangesFound']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['block_detection', 'cura_gcode_parsing', 'marketplace_metadata', 'prime_tower_handling', 'recipe_generation', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "extruder_modes": validate_extruder_modes(spec),
        "block_types": validate_block_types(spec),
        "plugin_fields": validate_plugin_fields(spec),
        "gcode_patterns": validate_gcode_patterns(spec),
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
