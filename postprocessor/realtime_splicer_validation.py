"""Validation helpers for F10.1 realtime splicer acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f10_1"
    / "spec"
    / "realtime_splicer_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_sync_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['AHEAD', 'BEHIND', 'CRITICAL', 'ERROR', 'IDLE', 'PAUSED', 'SYNCING']
    declared = set(spec.get("sync_states", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing sync states item: {item}")
    return errors

def validate_buffer_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['consumed', 'lengthMm', 'materialIndex', 'readyAt', 'segmentIndex', 'spliceAt']
    declared = set(spec.get("buffer_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing buffer fields item: {item}")
    return errors

def validate_timing_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['met', 'targetLayer', 'toleranceMs', 'windowEnd', 'windowStart']
    declared = set(spec.get("timing_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing timing fields item: {item}")
    return errors

def validate_printer_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['currentLayer', 'extruderTemp', 'filamentRemaining', 'positionMm', 'printSpeed']
    declared = set(spec.get("printer_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing printer fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['avgLeadTimeMs', 'bufferUnderruns', 'maxLeadTimeMs', 'missedWindows', 'syncAccuracy', 'totalSyncs']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['buffer_management', 'position_tracking', 'printer_sync', 'serial_serialization', 'timing_windows', 'underrun_detection']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "sync_states": validate_sync_states(spec),
        "buffer_fields": validate_buffer_fields(spec),
        "timing_fields": validate_timing_fields(spec),
        "printer_fields": validate_printer_fields(spec),
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
