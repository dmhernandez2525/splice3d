"""Validation helpers for F8.2 gcode preview acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f8_2"
    / "spec"
    / "gcode_preview_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_layer_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['colorIndex', 'heightMm', 'layerNumber', 'lengthMm', 'toolChanges', 'zPosition']
    declared = set(spec.get("layer_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing layer fields item: {item}")
    return errors

def validate_color_zone_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['colorHex', 'endLayer', 'lengthMm', 'startLayer', 'toolIndex']
    declared = set(spec.get("color_zone_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing color zone fields item: {item}")
    return errors

def validate_view_modes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['COLOR_MAP', 'LAYER_BY_LAYER', 'SPLICE_POINTS', 'USAGE_CHART']
    declared = set(spec.get("view_modes", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing view modes item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['filamentUsedMm', 'previewReady', 'totalColorZones', 'totalLayers', 'totalSplicePoints']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['color_zone_detection', 'layer_parsing', 'serial_serialization', 'splice_point_highlighting', 'usage_statistics', 'view_mode_switching']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "layer_fields": validate_layer_fields(spec),
        "color_zone_fields": validate_color_zone_fields(spec),
        "view_modes": validate_view_modes(spec),
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
