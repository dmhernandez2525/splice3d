#!/usr/bin/env python3
"""Validate F2.4 cutting system acceptance metrics."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from postprocessor.cutting_system_validation import generate_report, load_spec

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    spec = load_spec()
    report = generate_report(spec)

    if report["passed"]:
        logger.info("F2.4 cutting system validation passed")
        limits = spec.get("acceptance_limits", {})
        logger.info(
            "  Maintenance interval: %d cuts", limits.get("maintenance_interval_cuts", 0)
        )
        logger.info("  Phases: %d declared", len(spec.get("cut_phases", [])))
        logger.info("  Safety features: %d declared", len(spec.get("safety_features", [])))
        return 0

    for error in report["errors"]:
        logger.error("Validation error: %s", error)
    return 1


if __name__ == "__main__":
    sys.exit(main())
