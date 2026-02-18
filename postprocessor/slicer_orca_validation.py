"""Validation helpers for F7.1 OrcaSlicer plugin acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f7_1"
    / "spec"
    / "slicer_orca_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_parse_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "IDLE", "HEADER", "BODY",
        "TOOL_CHANGE", "COMPLETE", "PARSE_ERROR",
    }
    declared = set(spec.get("parse_states", []))
    for state in sorted(required - declared):
        errors.append(f"Missing parse state: {state}")
    return errors


def validate_tool_change_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "lineNumber", "layerNumber", "fromTool",
        "toTool", "positionMm", "valid",
    }
    declared = set(spec.get("tool_change_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing tool change field: {field}")
    return errors


def validate_color_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"toolIndex", "colorHex", "name", "active"}
    declared = set(spec.get("color_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing color field: {field}")
    return errors


def validate_recipe_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "toolChangeCount", "colorCount", "totalLayers",
        "totalLengthMm", "generated",
    }
    declared = set(spec.get("recipe_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing recipe field: {field}")
    return errors


def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "parsedLines", "toolChangesFound", "colorsExtracted",
        "errorsEncountered", "state", "projectLoaded",
    }
    declared = set(spec.get("stats_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing stats field: {field}")
    return errors


def validate_orca_patterns(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "tool_change_Tn", "layer_comment",
        "color_comment", "filament_metadata",
    }
    declared = set(spec.get("orca_patterns", []))
    for pat in sorted(required - declared):
        errors.append(f"Missing OrcaSlicer pattern: {pat}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "gcode_line_parsing",
        "tool_change_detection",
        "color_extraction",
        "recipe_generation",
        "project_file_support",
        "serial_serialization",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "parse_states": validate_parse_states(spec),
        "tool_change_fields": validate_tool_change_fields(spec),
        "color_fields": validate_color_fields(spec),
        "recipe_fields": validate_recipe_fields(spec),
        "stats_fields": validate_stats_fields(spec),
        "orca_patterns": validate_orca_patterns(spec),
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
