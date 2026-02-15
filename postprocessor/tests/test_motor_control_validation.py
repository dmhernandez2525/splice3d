"""Tests for F2.1 motor control acceptance validation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from postprocessor.motor_control_validation import (
    load_motor_control_spec,
    validate_emergency_stop_latency,
    validate_motor_control_spec,
    validate_position_accuracy,
    validate_stall_detection,
)


class TestMotorControlValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        spec_path = repo_root / "hardware" / "f2_1" / "spec" / "motor_control_validation.json"
        cls.spec = load_motor_control_spec(spec_path)

    def test_position_accuracy_limit(self) -> None:
        self.assertEqual(validate_position_accuracy(self.spec), [])

    def test_emergency_stop_limit(self) -> None:
        self.assertEqual(validate_emergency_stop_latency(self.spec), [])

    def test_stall_detection_limit(self) -> None:
        self.assertEqual(validate_stall_detection(self.spec), [])

    def test_overall_report_valid(self) -> None:
        report = validate_motor_control_spec(self.spec)
        self.assertTrue(report.valid)


if __name__ == "__main__":
    unittest.main()
