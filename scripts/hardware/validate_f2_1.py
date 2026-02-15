#!/usr/bin/env python3
"""Validate F2.1 motor control acceptance metrics."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from postprocessor.motor_control_validation import (
    load_motor_control_spec,
    validate_motor_control_spec,
)

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run() -> int:
    spec_path = PROJECT_ROOT / "hardware" / "f2_1" / "spec" / "motor_control_validation.json"
    if not spec_path.exists():
        logger.error("Motor control validation spec missing: %s", spec_path)
        return 2

    spec = load_motor_control_spec(spec_path)
    report = validate_motor_control_spec(spec)

    if report.valid:
        logger.info("F2.1 motor control validation passed")
        return 0

    for issue in report.position_violations:
        logger.error("Position violation: %s", issue)
    for issue in report.stop_violations:
        logger.error("Stop violation: %s", issue)
    for issue in report.stall_violations:
        logger.error("Stall violation: %s", issue)

    return 1


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(run())
