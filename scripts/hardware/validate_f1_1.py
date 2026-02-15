#!/usr/bin/env python3
"""Run local validation checks for the F1.1 mechanical design package."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from postprocessor.mechanical_validation import load_mechanical_layout, validate_layout

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )


def run() -> int:
    """Execute validation against the F1.1 layout manifest."""
    layout_path = PROJECT_ROOT / "hardware" / "f1_1" / "spec" / "mechanical_layout.json"

    if not layout_path.exists():
        logger.error("Layout manifest not found: %s", layout_path)
        return 2

    layout = load_mechanical_layout(layout_path)
    report = validate_layout(layout)

    if report.valid:
        logger.info("F1.1 mechanical validation passed")
        return 0

    for issue in report.path_violations:
        logger.error("Path violation: %s", issue)
    for issue in report.bed_fit_violations:
        logger.error("Bed fit violation: %s", issue)
    for issue in report.interface_violations:
        logger.error("Interface violation: %s", issue)
    for issue in report.layout_violations:
        logger.error("Layout violation: %s", issue)

    return 1


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(run())
