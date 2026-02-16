"""Validation helpers for F9.1 wifi manager acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f9_1"
    / "spec"
    / "wifi_manager_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_wifi_modes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['AP', 'OFF', 'STA', 'STA_AP']
    declared = set(spec.get("wifi_modes", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing wifi modes item: {item}")
    return errors

def validate_connection_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['AP_ACTIVE', 'CONNECTED', 'CONNECTING', 'DISCONNECTED', 'ERROR', 'IDLE', 'SCANNING']
    declared = set(spec.get("connection_states", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing connection states item: {item}")
    return errors

def validate_network_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['autoConnect', 'channel', 'connected', 'encryption', 'rssi', 'ssid']
    declared = set(spec.get("network_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing network fields item: {item}")
    return errors

def validate_config_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['apPassword', 'apSsid', 'backoffBaseMs', 'hostname', 'maxRetries', 'staTimeout']
    declared = set(spec.get("config_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing config fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['connected', 'currentMode', 'ipAddress', 'reconnectCount', 'rssi', 'storedNetworks', 'uptimeMs']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['ap_mode', 'auto_reconnect', 'exponential_backoff', 'network_scanning', 'nvs_credential_storage', 'serial_serialization', 'sta_mode']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "wifi_modes": validate_wifi_modes(spec),
        "connection_states": validate_connection_states(spec),
        "network_fields": validate_network_fields(spec),
        "config_fields": validate_config_fields(spec),
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
