"""Tests for F2.2 encoder system acceptance validation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from postprocessor.encoder_system_validation import (
    load_encoder_system_spec,
    validate_calibration_repeatability,
    validate_encoder_system_spec,
    validate_health_monitoring,
    validate_position_accuracy,
    validate_slip_detection,
)


class TestEncoderSystemValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        spec_path = repo_root / "hardware" / "f2_2" / "spec" / "encoder_system_validation.json"
        cls.spec = load_encoder_system_spec(spec_path)

    def test_position_accuracy_limit(self) -> None:
        self.assertEqual(validate_position_accuracy(self.spec), [])

    def test_slip_detection_limit(self) -> None:
        self.assertEqual(validate_slip_detection(self.spec), [])

    def test_calibration_repeatability_limit(self) -> None:
        self.assertEqual(validate_calibration_repeatability(self.spec), [])

    def test_health_monitoring_flags(self) -> None:
        self.assertEqual(validate_health_monitoring(self.spec), [])

    def test_overall_report_valid(self) -> None:
        report = validate_encoder_system_spec(self.spec)
        self.assertTrue(report.valid)


if __name__ == "__main__":
    unittest.main()
