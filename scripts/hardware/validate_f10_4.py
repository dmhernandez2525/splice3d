#!/usr/bin/env python3
"""Validate F10.4 mfg ready acceptance metrics."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from postprocessor.mfg_ready_validation import generate_report, load_spec

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    spec = load_spec()
    report = generate_report(spec)
    if report["passed"]:
        logger.info("F10.4 mfg ready validation passed")
        return 0
    for error in report["errors"]:
        logger.error("Validation error: %s", error)
    return 1


if __name__ == "__main__":
    sys.exit(main())
