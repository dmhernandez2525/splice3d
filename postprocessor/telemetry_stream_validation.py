"""Validation helpers for F4.1 telemetry stream acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f4_1"
    / "spec"
    / "telemetry_stream_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_stream_modes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"OFF", "SUMMARY", "VERBOSE"}
    declared = set(spec.get("stream_modes", []))
    for mode in sorted(required - declared):
        errors.append(f"Missing stream mode: {mode}")
    return errors


def validate_summary_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"type", "t", "state", "temp", "target", "pos_mm", "error"}
    declared = set(spec.get("summary_fields", []))
    for field in sorted(required - declared):
        errors.append(f"Missing summary field: {field}")
    return errors


def validate_verbose_sections(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"temp", "enc", "splice", "pos"}
    declared = set(spec.get("verbose_sections", []))
    for section in sorted(required - declared):
        errors.append(f"Missing verbose section: {section}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"json_telemetry", "heartbeat_keepalive", "configurable_interval"}
    declared = set(spec.get("features", []))
    for feat in sorted(required - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "stream_modes": validate_stream_modes(spec),
        "summary_fields": validate_summary_fields(spec),
        "verbose_sections": validate_verbose_sections(spec),
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
