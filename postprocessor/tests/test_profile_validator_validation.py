"""Tests for F5.4 profile validation acceptance validation."""

import unittest

from postprocessor.profile_validator_validation import (
    generate_report,
    load_spec,
    validate_features,
    validate_safety_limits,
    validate_severity_levels,
    validate_test_phases,
    validate_validation_codes,
)


class TestProfileValidatorValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("severity_levels", self.spec)
        self.assertIn("features", self.spec)

    def test_severity_levels_complete(self) -> None:
        errors = validate_severity_levels(self.spec)
        self.assertEqual(errors, [])

    def test_validation_codes_complete(self) -> None:
        errors = validate_validation_codes(self.spec)
        self.assertEqual(errors, [])

    def test_safety_limits_valid(self) -> None:
        errors = validate_safety_limits(self.spec)
        self.assertEqual(errors, [])

    def test_test_phases_complete(self) -> None:
        errors = validate_test_phases(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_severity_detected(self) -> None:
        bad_spec = {"severity_levels": ["INFO", "WARNING"]}
        errors = validate_severity_levels(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_code_detected(self) -> None:
        bad_spec = {"validation_codes": ["OK", "TEMP_TOO_LOW"]}
        errors = validate_validation_codes(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_bad_safety_limits_detected(self) -> None:
        bad_spec = {
            "safety_limits": {
                "temperature": {"min": 300, "max": 100},
            }
        }
        errors = validate_safety_limits(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_phase_detected(self) -> None:
        bad_spec = {"test_phases": ["IDLE", "COMPLETE"]}
        errors = validate_test_phases(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_all_limit_categories_present(self) -> None:
        limits = self.spec.get("safety_limits", {})
        for key in ["temperature", "hold_time_ms", "compression_mm",
                     "cool_time_ms", "pull_force_n"]:
            self.assertIn(key, limits)

    def test_max_validation_errors_reasonable(self) -> None:
        size = self.spec.get("max_validation_errors", 0)
        self.assertGreaterEqual(size, 4)
        self.assertLessEqual(size, 32)


if __name__ == "__main__":
    unittest.main()
