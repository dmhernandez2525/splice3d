"""Validation helpers for F9.2 web dashboard acceptance metrics."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SPEC_PATH = (
    Path(__file__).resolve().parent.parent
    / "hardware"
    / "f9_2"
    / "spec"
    / "web_dashboard_validation.json"
)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_http_methods(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['DELETE', 'GET', 'POST', 'PUT']
    declared = set(spec.get("http_methods", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing http methods item: {item}")
    return errors

def validate_api_routes(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['/config', '/materials', '/queue', '/recipe', '/status', '/telemetry']
    declared = set(spec.get("api_routes", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing api routes item: {item}")
    return errors

def validate_websocket_events(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['error_event', 'job_complete', 'splice_progress', 'status_update', 'temperature_change']
    declared = set(spec.get("websocket_events", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing websocket events item: {item}")
    return errors

def validate_page_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['authRequired', 'cacheable', 'contentType', 'path', 'title']
    declared = set(spec.get("page_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing page fields item: {item}")
    return errors

def validate_stats_fields(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['activeConnections', 'bytesServed', 'errorCount', 'totalRequests', 'uptimeMs', 'websocketClients']
    declared = set(spec.get("stats_fields", []))
    for item in sorted(set(required) - declared):
        errors.append(f"Missing stats fields item: {item}")
    return errors


def validate_features(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['connection_management', 'http_server', 'rest_api', 'serial_serialization', 'static_page_serving', 'websocket_streaming']
    declared = set(spec.get("features", []))
    for feat in sorted(set(required) - declared):
        errors.append(f"Missing feature: {feat}")
    return errors


def generate_report(spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "http_methods": validate_http_methods(spec),
        "api_routes": validate_api_routes(spec),
        "websocket_events": validate_websocket_events(spec),
        "page_fields": validate_page_fields(spec),
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
