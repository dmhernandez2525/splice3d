"""Tests for F3.4 error recovery acceptance validation."""

import unittest

from postprocessor.error_recovery_validation import (
    generate_report,
    load_spec,
    validate_config_defaults,
    validate_error_categories,
    validate_features,
    validate_recovery_phases,
)


class TestErrorRecoveryValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("recovery_phases", self.spec)
        self.assertIn("error_categories", self.spec)

    def test_recovery_phases_complete(self) -> None:
        errors = validate_recovery_phases(self.spec)
        self.assertEqual(errors, [])

    def test_error_categories_complete(self) -> None:
        errors = validate_error_categories(self.spec)
        self.assertEqual(errors, [])

    def test_config_defaults_valid(self) -> None:
        errors = validate_config_defaults(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_phase_detected(self) -> None:
        bad_spec = {"recovery_phases": ["IDLE"]}
        errors = validate_recovery_phases(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_invalid_retries_detected(self) -> None:
        bad_spec = {"config_defaults": {"max_retries": 0, "cooldown_timeout_ms": 60000, "cooldown_target_c": 60}}
        errors = validate_config_defaults(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_serial_commands_present(self) -> None:
        commands = self.spec.get("serial_commands", [])
        self.assertIn("RECOVER BEGIN", commands)
        self.assertIn("RECOVER CONFIRM", commands)
        self.assertIn("RECOVER STATS", commands)


if __name__ == "__main__":
    unittest.main()
