"""Tests for F3.1 filament feed acceptance validation."""

import unittest

from postprocessor.filament_feed_validation import (
    generate_report,
    load_spec,
    validate_acceptance_limits,
    validate_feed_modes,
    validate_safety_features,
)


class TestFilamentFeedValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("acceptance_limits", self.spec)
        self.assertIn("feed_modes", self.spec)

    def test_acceptance_limits_valid(self) -> None:
        errors = validate_acceptance_limits(self.spec)
        self.assertEqual(errors, [])

    def test_feed_modes_complete(self) -> None:
        errors = validate_feed_modes(self.spec)
        self.assertEqual(errors, [])

    def test_safety_features_complete(self) -> None:
        errors = validate_safety_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_statistics_tracked(self) -> None:
        stats = self.spec.get("statistics_tracked", [])
        self.assertIn("totalFedMmA", stats)
        self.assertIn("jamCount", stats)


    def test_bad_acceptance_limits_detected(self) -> None:
        bad_spec = {"acceptance_limits": {"feed_rate_variance_pct": 0}}
        errors = validate_acceptance_limits(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_feed_modes_detected(self) -> None:
        bad_spec = {"feed_modes": []}
        errors = validate_feed_modes(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_safety_features_detected(self) -> None:
        bad_spec = {"safety_features": []}
        errors = validate_safety_features(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_empty_spec_fails(self) -> None:
        report = generate_report({})
        self.assertFalse(report["passed"])

if __name__ == "__main__":
    unittest.main()
