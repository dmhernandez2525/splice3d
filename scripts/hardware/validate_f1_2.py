#!/usr/bin/env python3
"""Validate F1.2 electronics design outputs."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from postprocessor.electronics_validation import (
    load_electronics_spec,
    summarize_power_budget,
    validate_electronics_spec,
)

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run() -> int:
    """Run validation checks against the F1.2 electronics spec."""
    spec_path = PROJECT_ROOT / "hardware" / "f1_2" / "spec" / "electronics_design.json"
    if not spec_path.exists():
        logger.error("Electronics design spec missing: %s", spec_path)
        return 2

    spec = load_electronics_spec(spec_path)
    report = validate_electronics_spec(spec)

    if report.valid:
        logger.info("F1.2 electronics validation passed")
        power_summary = summarize_power_budget(spec)
        for mode_name, rails in power_summary.items():
            logger.info("Power mode: %s", mode_name)
            for rail_name, current in sorted(rails.items()):
                logger.info("  %s: %.2fA", rail_name, current)
        return 0

    for issue in report.drc_violations:
        logger.error("DRC violation: %s", issue)
    for issue in report.sourcing_violations:
        logger.error("Sourcing violation: %s", issue)
    for issue in report.power_budget_violations:
        logger.error("Power violation: %s", issue)

    return 1


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(run())
