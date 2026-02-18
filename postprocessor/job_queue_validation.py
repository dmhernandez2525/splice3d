"""Validation helpers for F4.3 job queue acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f4_3"
    / "spec"
    / "job_queue_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_job_statuses(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"PENDING", "RUNNING", "PAUSED", "COMPLETE", "FAILED", "CANCELLED"}
    declared = set(spec.get("job_statuses", []))
    for s in sorted(required - declared):
        errors.append(f"Missing job status: {s}")
    return errors


def validate_job_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"jobId", "segmentCount", "status", "priority", "progressPercent"}
    declared = set(spec.get("job_fields", []))
    for f in sorted(required - declared):
        errors.append(f"Missing job field: {f}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"priority_ordering", "pause_resume", "auto_advance", "progress_tracking"}
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "job_statuses": validate_job_statuses(spec),
        "job_fields": validate_job_fields(spec),
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
