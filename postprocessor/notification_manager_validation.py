"""Validation helpers for F9.4 notification manager acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f9_4"
    / "spec"
    / "notification_manager_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_priority_levels(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['CRITICAL', 'HIGH', 'LOW', 'MEDIUM']
    declared = set(spec.get("priority_levels", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing priority levels item: {item}")
    return errors

def validate_event_types(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['ERROR', 'JOB_COMPLETE', 'QUEUE_EMPTY', 'SPLICE_COMPLETE', 'SPLICE_FAILED', 'TEMPERATURE_WARNING']
    declared = set(spec.get("event_types", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing event types item: {item}")
    return errors

def validate_channel_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['channelId', 'enabled', 'endpoint', 'filterMask', 'name', 'priority']
    declared = set(spec.get("channel_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing channel fields item: {item}")
    return errors

def validate_notification_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['acknowledged', 'delivered', 'eventType', 'message', 'notificationId', 'priority', 'timestamp']
    declared = set(spec.get("notification_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing notification fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['channelCount', 'lastSentMs', 'pendingCount', 'totalDelivered', 'totalFailed', 'totalSent']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['channel_management', 'delivery_queue', 'event_filtering', 'notification_creation', 'priority_filtering', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "priority_levels": validate_priority_levels(spec),
        "event_types": validate_event_types(spec),
        "channel_fields": validate_channel_fields(spec),
        "notification_fields": validate_notification_fields(spec),
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
