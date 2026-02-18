"""Tests for F3.3 position tracking acceptance validation."""

import unittest

from postprocessor.position_tracking_validation import (
    generate_report,
    load_spec,
    validate_drift_thresholds,
    validate_features,
    validate_snapshot_fields,
    validate_tracking_parameters,
)


class TestPositionTrackingValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("tracking_parameters", self.spec)
        self.assertIn("drift_thresholds", self.spec)

    def test_tracking_parameters_valid(self) -> None:
        errors = validate_tracking_parameters(self.spec)
        self.assertEqual(errors, [])

    def test_drift_thresholds_valid(self) -> None:
        errors = validate_drift_thresholds(self.spec)
        self.assertEqual(errors, [])

    def test_snapshot_fields_complete(self) -> None:
        errors = validate_snapshot_fields(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_invalid_thresholds_detected(self) -> None:
        bad_spec = {"drift_thresholds": {"minor_mm": 5.0, "moderate_mm": 3.0, "severe_mm": 1.0}}
        errors = validate_drift_thresholds(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_feature_detected(self) -> None:
        bad_spec = {"features": ["waypoint_management"]}
        errors = validate_features(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
