"""Tests for F4.2 quality metrics acceptance validation."""

import unittest

from postprocessor.quality_metrics_validation import (
    generate_report,
    load_spec,
    validate_config,
    validate_features,
    validate_per_material_fields,
    validate_snapshot_fields,
)


class TestQualityMetricsValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("per_material_fields", self.spec)
        self.assertIn("snapshot_fields", self.spec)

    def test_per_material_fields_complete(self) -> None:
        errors = validate_per_material_fields(self.spec)
        self.assertEqual(errors, [])

    def test_snapshot_fields_complete(self) -> None:
        errors = validate_snapshot_fields(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_config_valid(self) -> None:
        errors = validate_config(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_invalid_history_size_detected(self) -> None:
        bad_spec = {"max_materials": 4, "quality_history_size": 2}
        errors = validate_config(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_trend_fields_present(self) -> None:
        trend = self.spec.get("trend_fields", [])
        self.assertIn("movingAvg", trend)
        self.assertIn("trend", trend)


if __name__ == "__main__":
    unittest.main()
