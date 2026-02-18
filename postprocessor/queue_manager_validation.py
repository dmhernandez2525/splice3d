"""Validation helpers for F8.4 queue manager acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f8_4"
    / "spec"
    / "queue_manager_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_queue_item_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['actualMinutes', 'estimatedMinutes', 'jobId', 'position', 'priority', 'recipeName', 'status']
    declared = set(spec.get("queue_item_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing queue item fields item: {item}")
    return errors

def validate_queue_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['COMPLETED', 'EMPTY', 'ERROR', 'PAUSED', 'RUNNING']
    declared = set(spec.get("queue_states", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing queue states item: {item}")
    return errors

def validate_operations(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['cancel', 'clear', 'dequeue', 'enqueue', 'pause', 'reorder', 'resume']
    declared = set(spec.get("operations", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing operations item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['avgWaitMinutes', 'currentJobId', 'queueState', 'totalCompleted', 'totalFailed', 'totalQueued']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['drag_drop_reorder', 'estimated_completion', 'job_enqueue', 'priority_ordering', 'queue_state_management', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "queue_item_fields": validate_queue_item_fields(spec),
        "queue_states": validate_queue_states(spec),
        "operations": validate_operations(spec),
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
