"""Validation helpers for F4.4 batch processor acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f4_4"
    / "spec"
    / "batch_processor_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_batch_modes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"SINGLE", "SEQUENTIAL", "ROUND_ROBIN"}
    declared = set(spec.get("batch_modes", []))
    for m in sorted(required - declared):
        errors.append(f"Missing batch mode: {m}")
    return errors


def validate_session_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"totalJobs", "completedJobs", "avgQuality", "throughputJobsPerHour", "active"}
    declared = set(spec.get("session_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing session field: {f}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "batch_session_management", "job_history_ring_buffer",
        "throughput_calculation", "aggregate_quality_stats",
    }
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "batch_modes": validate_batch_modes(spec),
        "session_fields": validate_session_fields(spec),
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
