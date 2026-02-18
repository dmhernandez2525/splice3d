"""Tests for F2.4 cutting system acceptance validation."""

import unittest

from postprocessor.cutting_system_validation import (
    generate_report,
    load_spec,
    validate_acceptance_limits,
    validate_cut_phases,
    validate_eeprom_persistence,
    validate_safety_features,
)


class TestCuttingSystemValidation(unittest.TestCase):
    """Verify the cutting system spec passes all checks."""

    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("acceptance_limits", self.spec)
        self.assertIn("cut_phases", self.spec)
        self.assertIn("safety_features", self.spec)

    def test_acceptance_limits_valid(self) -> None:
        errors = validate_acceptance_limits(self.spec)
        self.assertEqual(errors, [], f"Limit errors: {errors}")

    def test_cut_phases_complete(self) -> None:
        errors = validate_cut_phases(self.spec)
        self.assertEqual(errors, [], f"Phase errors: {errors}")

    def test_safety_features_complete(self) -> None:
        errors = validate_safety_features(self.spec)
        self.assertEqual(errors, [], f"Safety errors: {errors}")

    def test_eeprom_persistence_valid(self) -> None:
        errors = validate_eeprom_persistence(self.spec)
        self.assertEqual(errors, [], f"EEPROM errors: {errors}")

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"], f"Report errors: {report['errors']}")

    def test_maintenance_interval_reasonable(self) -> None:
        interval = self.spec["acceptance_limits"]["maintenance_interval_cuts"]
        self.assertGreaterEqual(interval, 100)
        self.assertLessEqual(interval, 5000)


if __name__ == "__main__":
    unittest.main()
