#!/usr/bin/env python3
"""Validate F1.4 printed parts design package."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from postprocessor.printed_parts_validation import (
    load_printed_parts_spec,
    validate_printed_parts_spec,
)

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run() -> int:
    """Run validation against F1.4 printed parts manifest."""
    spec_path = PROJECT_ROOT / "hardware" / "f1_4" / "spec" / "printed_parts_design.json"
    if not spec_path.exists():
        logger.error("Printed-parts spec missing: %s", spec_path)
        return 2

    spec = load_printed_parts_spec(spec_path)
    report = validate_printed_parts_spec(spec, PROJECT_ROOT)

    if report.valid:
        logger.info("F1.4 printed-parts validation passed")
        return 0

    for issue in report.bed_fit_violations:
        logger.error("Bed fit violation: %s", issue)
    for issue in report.snap_fit_violations:
        logger.error("Snap-fit violation: %s", issue)
    for issue in report.support_violations:
        logger.error("Support violation: %s", issue)
    for issue in report.artifact_violations:
        logger.error("Artifact violation: %s", issue)
    for issue in report.spool_holder_violations:
        logger.error("Spool-holder violation: %s", issue)

    return 1


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(run())
