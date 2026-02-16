"""Validation helpers for F10.4 mfg ready acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f10_4"
    / "spec"
    / "mfg_ready_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_test_categories(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['CALIBRATION', 'COMMUNICATION', 'ELECTRICAL', 'MECHANICAL', 'SAFETY', 'THERMAL']
    declared = set(spec.get("test_categories", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing test categories item: {item}")
    return errors

def validate_test_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['category', 'durationMs', 'errorMessage', 'name', 'passed', 'testId']
    declared = set(spec.get("test_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing test fields item: {item}")
    return errors

def validate_cert_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['allPassed', 'failedTests', 'operatorId', 'serialNumber', 'testDate', 'totalTests', 'version']
    declared = set(spec.get("cert_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing cert fields item: {item}")
    return errors

def validate_uptime_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['bootCount', 'lastBootMs', 'mtbfMs', 'totalDowntimeMs', 'totalUptimeMs']
    declared = set(spec.get("uptime_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing uptime fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['avgTestDurationMs', 'certValid', 'failureRate', 'lastCertDate', 'passRate', 'totalTestRuns']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['calibration_verification', 'certification_generation', 'failure_monitoring', 'self_test_sequence', 'serial_serialization', 'uptime_tracking']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "test_categories": validate_test_categories(spec),
        "test_fields": validate_test_fields(spec),
        "cert_fields": validate_cert_fields(spec),
        "uptime_fields": validate_uptime_fields(spec),
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
