"""Tests for F7.4 slicer bambu acceptance validation."""

import unittest

from postprocessor.slicer_bambu_validation import (
    generate_report,
    load_spec,
    validate_ams_fields,
    validate_bambu_extensions,
    validate_plate_fields,
    validate_stats_fields,
    validate_features,
)


class TestSlicerBambuValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_ams_fields_complete(self) -> None:
        errors = validate_ams_fields(self.spec)
        self.assertEqual(errors, [])

    def test_bambu_extensions_complete(self) -> None:
        errors = validate_bambu_extensions(self.spec)
        self.assertEqual(errors, [])

    def test_plate_fields_complete(self) -> None:
        errors = validate_plate_fields(self.spec)
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

    def test_missing_ams_fields_item_detected(self) -> None:
        bad_spec = {"ams_fields": ["slotIndex"]}
        errors = validate_ams_fields(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_bambu_extensions_item_detected(self) -> None:
        bad_spec = {"bambu_extensions": []}
        errors = validate_bambu_extensions(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_plate_fields_item_detected(self) -> None:
        bad_spec = {"plate_fields": []}
        errors = validate_plate_fields(bad_spec)
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
