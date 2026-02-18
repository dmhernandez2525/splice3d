#!/usr/bin/env python3
"""Validate F2.3 temperature control acceptance metrics."""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from postprocessor.temperature_control_validation import (
    generate_report,
    load_spec,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    spec = load_spec()
    report = generate_report(spec)

    if report["passed"]:
        logger.info("F2.3 temperature control validation passed")
        profiles = spec.get("material_profiles", {})
        for mat, profile in profiles.items():
            logger.info(
                "  %s: %d C, ramp %.1f C/s, soak %d ms",
                mat,
                profile["splice_target_c"],
                profile["ramp_rate_c_per_s"],
                profile["soak_time_ms"],
            )
        safety = spec.get("safety_features", [])
        logger.info("  Safety features: %d declared", len(safety))
        return 0

    for error in report["errors"]:
        logger.error("Validation error: %s", error)
    return 1


if __name__ == "__main__":
    sys.exit(main())
