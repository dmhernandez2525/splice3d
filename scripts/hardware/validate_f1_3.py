#!/usr/bin/env python3
"""Validate F1.3 BOM specification data."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from postprocessor.bom_validation import compute_tier_totals, load_bom_spec, validate_bom_spec

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run() -> int:
    """Run BOM checks and print summary totals."""
    spec_path = PROJECT_ROOT / "hardware" / "f1_3" / "spec" / "bom_catalog.json"
    if not spec_path.exists():
        logger.error("BOM spec missing: %s", spec_path)
        return 2

    spec = load_bom_spec(spec_path)
    report = validate_bom_spec(spec)
    totals = compute_tier_totals(spec)

    if report.valid:
        logger.info("F1.3 BOM validation passed")
        logger.info("Budget total: %.2f", totals["budget_total"])
        logger.info("Standard total: %.2f", totals["standard_total"])
        logger.info("Premium total: %.2f", totals["premium_total"])
        return 0

    for issue in report.cost_violations:
        logger.error("Cost violation: %s", issue)
    for issue in report.sourcing_violations:
        logger.error("Sourcing violation: %s", issue)
    for issue in report.structure_violations:
        logger.error("Structure violation: %s", issue)

    return 1


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(run())
