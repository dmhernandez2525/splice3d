"""Validation helpers for F10.2 multi color acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f10_2"
    / "spec"
    / "multi_color_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_channel_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['ACTIVE', 'EMPTY', 'ERROR', 'LOADED', 'MAINTENANCE', 'SWITCHING']
    declared = set(spec.get("channel_states", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing channel states item: {item}")
    return errors

def validate_channel_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['channelIndex', 'colorHex', 'lengthRemainingMm', 'materialType', 'state', 'usageCount']
    declared = set(spec.get("channel_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing channel fields item: {item}")
    return errors

def validate_switch_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['completedMs', 'fromChannel', 'purgeUsedMm', 'requestedMs', 'success', 'toChannel']
    declared = set(spec.get("switch_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing switch fields item: {item}")
    return errors

def validate_mapping_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['channelIndex', 'colorName', 'priority', 'toolIndex']
    declared = set(spec.get("mapping_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing mapping fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['activeChannels', 'avgSwitchMs', 'channelUtilization', 'failedSwitches', 'totalPurgeMm', 'totalSwitches']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['channel_management', 'input_selection', 'purge_tracking', 'serial_serialization', 'switch_coordination', 'tool_mapping']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "channel_states": validate_channel_states(spec),
        "channel_fields": validate_channel_fields(spec),
        "switch_fields": validate_switch_fields(spec),
        "mapping_fields": validate_mapping_fields(spec),
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
