#!/usr/bin/env python3
"""Validate F2.2 encoder system acceptance metrics."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from postprocessor.encoder_system_validation import (
    load_encoder_system_spec,
    validate_encoder_system_spec,
)

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run() -> int:
    spec_path = PROJECT_ROOT / "hardware" / "f2_2" / "spec" / "encoder_system_validation.json"
    if not spec_path.exists():
        logger.error("Encoder system validation spec missing: %s", spec_path)
        return 2

    spec = load_encoder_system_spec(spec_path)
    report = validate_encoder_system_spec(spec)
    if report.valid:
        logger.info("F2.2 encoder system validation passed")
        return 0

    for issue in report.position_violations:
        logger.error("Position violation: %s", issue)
    for issue in report.slip_violations:
        logger.error("Slip violation: %s", issue)
    for issue in report.calibration_violations:
        logger.error("Calibration violation: %s", issue)
    for issue in report.health_violations:
        logger.error("Health violation: %s", issue)
    return 1


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(run())
