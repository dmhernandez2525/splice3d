"""Tests for F6.3 waste reduction acceptance validation."""

import unittest

from postprocessor.waste_tracker_validation import (
    generate_report,
    load_spec,
    validate_analytics_fields,
    validate_features,
    validate_recommendation_fields,
    validate_record_fields,
    validate_waste_categories,
)


class TestWasteTrackerValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("waste_categories", self.spec)
        self.assertIn("record_fields", self.spec)

    def test_waste_categories_complete(self) -> None:
        errors = validate_waste_categories(self.spec)
        self.assertEqual(errors, [])

    def test_record_fields_complete(self) -> None:
        errors = validate_record_fields(self.spec)
        self.assertEqual(errors, [])

    def test_analytics_fields_complete(self) -> None:
        errors = validate_analytics_fields(self.spec)
        self.assertEqual(errors, [])

    def test_recommendation_fields_complete(self) -> None:
        errors = validate_recommendation_fields(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_category_detected(self) -> None:
        bad_spec = {"waste_categories": ["PURGE"]}
        errors = validate_waste_categories(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_record_field_detected(self) -> None:
        bad_spec = {"record_fields": ["spliceId"]}
        errors = validate_record_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_analytics_field_detected(self) -> None:
        bad_spec = {"analytics_fields": ["totalWasteMm"]}
        errors = validate_analytics_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_waste_records_defined(self) -> None:
        self.assertEqual(self.spec.get("max_waste_records"), 32)

    def test_default_baseline_defined(self) -> None:
        self.assertEqual(self.spec.get("default_baseline_mm"), 25.0)

    def test_four_waste_categories_defined(self) -> None:
        categories = self.spec.get("waste_categories", [])
        self.assertEqual(len(categories), 4)


if __name__ == "__main__":
    unittest.main()
