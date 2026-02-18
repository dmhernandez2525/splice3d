"""Validation helpers for F8.3 device connection acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f8_3"
    / "spec"
    / "device_connection_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_connection_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['CONNECTED', 'CONNECTING', 'DISCONNECTED', 'ERROR', 'RECONNECTING', 'SCANNING']
    declared = set(spec.get("connection_states", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing connection states item: {item}")
    return errors

def validate_device_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['baudRate', 'connectionState', 'firmwareVersion', 'lastSeenMs', 'portName', 'serialNumber']
    declared = set(spec.get("device_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing device fields item: {item}")
    return errors

def validate_command_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['commandId', 'payload', 'responseMs', 'sentMs', 'success']
    declared = set(spec.get("command_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing command fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['avgLatencyMs', 'connectedDevices', 'failedCommands', 'reconnectCount', 'scanCount', 'totalCommands']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['auto_detection', 'command_tracking', 'connection_management', 'multi_device_support', 'reconnection_handling', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "connection_states": validate_connection_states(spec),
        "device_fields": validate_device_fields(spec),
        "command_fields": validate_command_fields(spec),
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
