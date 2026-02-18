"""Validation helpers for F9.3 ota updater acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f9_3"
    / "spec"
    / "ota_updater_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_update_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['ERROR', 'FLASHING', 'IDLE', 'REBOOTING', 'RECEIVING', 'ROLLBACK', 'VERIFYING']
    declared = set(spec.get("update_states", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing update states item: {item}")
    return errors

def validate_chunk_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['checksum', 'chunkIndex', 'received', 'size', 'totalChunks']
    declared = set(spec.get("chunk_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing chunk fields item: {item}")
    return errors

def validate_firmware_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['buildTimestamp', 'checksum', 'compatible', 'size', 'targetBoard', 'version']
    declared = set(spec.get("firmware_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing firmware fields item: {item}")
    return errors

def validate_progress_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['bytesReceived', 'bytesTotal', 'elapsedMs', 'estimatedRemainingMs', 'percentComplete', 'state']
    declared = set(spec.get("progress_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing progress fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['currentVersion', 'failedUpdates', 'lastUpdateMs', 'rollbackCount', 'successfulUpdates', 'totalUpdates']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['checksum_verification', 'chunked_upload', 'flash_management', 'progress_reporting', 'rollback_support', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "update_states": validate_update_states(spec),
        "chunk_fields": validate_chunk_fields(spec),
        "firmware_fields": validate_firmware_fields(spec),
        "progress_fields": validate_progress_fields(spec),
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
