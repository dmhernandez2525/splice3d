"""Validation helpers for F10.3 print farm acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f10_3"
    / "spec"
    / "print_farm_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_printer_states(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['ERROR', 'IDLE', 'MAINTENANCE', 'OFFLINE', 'PRINTING', 'SPLICING']
    declared = set(spec.get("printer_states", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing printer states item: {item}")
    return errors

def validate_printer_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['currentJobId', 'jobsCompleted', 'name', 'printerId', 'progressPercent', 'state', 'uptimeMs']
    declared = set(spec.get("printer_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing printer fields item: {item}")
    return errors

def validate_farm_job_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['assignedPrinter', 'completedMs', 'jobId', 'priority', 'recipeName', 'startedMs', 'status']
    declared = set(spec.get("farm_job_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing farm job fields item: {item}")
    return errors

def validate_pool_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['availableLengthMm', 'colorHex', 'materialType', 'reservedLengthMm', 'totalLengthMm']
    declared = set(spec.get("pool_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing pool fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['activePrinters', 'avgJobMinutes', 'completedFarmJobs', 'farmUtilization', 'totalFarmJobs', 'totalPrinters']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['farm_statistics', 'job_distribution', 'load_balancing', 'material_pool_management', 'printer_registration', 'serial_serialization']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "printer_states": validate_printer_states(spec),
        "printer_fields": validate_printer_fields(spec),
        "farm_job_fields": validate_farm_job_fields(spec),
        "pool_fields": validate_pool_fields(spec),
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
