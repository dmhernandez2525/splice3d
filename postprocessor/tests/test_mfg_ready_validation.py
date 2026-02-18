"""Tests for F10.4 mfg ready acceptance validation."""

import unittest

from postprocessor.mfg_ready_validation import (
    generate_report,
    load_spec,
    validate_test_categories,
    validate_test_fields,
    validate_cert_fields,
    validate_uptime_fields,
    validate_stats_fields,
    validate_features,
)


class TestMfgReadyValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_test_categories_complete(self) -> None:
        errors = validate_test_categories(self.spec)
        self.assertEqual(errors, [])

    def test_test_fields_complete(self) -> None:
        errors = validate_test_fields(self.spec)
        self.assertEqual(errors, [])

    def test_cert_fields_complete(self) -> None:
        errors = validate_cert_fields(self.spec)
        self.assertEqual(errors, [])

    def test_uptime_fields_complete(self) -> None:
        errors = validate_uptime_fields(self.spec)
        self.assertEqual(errors, [])

    def test_stats_fields_complete(self) -> None:
        errors = validate_stats_fields(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_test_categories_item_detected(self) -> None:
        bad_spec = {"test_categories": ["MECHANICAL"]}
        errors = validate_test_categories(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_test_fields_item_detected(self) -> None:
        bad_spec = {"test_fields": []}
        errors = validate_test_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_cert_fields_item_detected(self) -> None:
        bad_spec = {"cert_fields": []}
        errors = validate_cert_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_uptime_fields_item_detected(self) -> None:
        bad_spec = {"uptime_fields": []}
        errors = validate_uptime_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_stats_fields_item_detected(self) -> None:
        bad_spec = {"stats_fields": []}
        errors = validate_stats_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_features_item_detected(self) -> None:
        bad_spec = {"features": []}
        errors = validate_features(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_empty_spec_fails(self) -> None:
        report = generate_report({})
        self.assertFalse(report["passed"])

if __name__ == "__main__":
    unittest.main()
