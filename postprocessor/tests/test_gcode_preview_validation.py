"""Tests for F8.2 gcode preview acceptance validation."""

import unittest

from postprocessor.gcode_preview_validation import (
    generate_report,
    load_spec,
    validate_layer_fields,
    validate_color_zone_fields,
    validate_view_modes,
    validate_stats_fields,
    validate_features,
)


class TestGcodePreviewValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_layer_fields_complete(self) -> None:
        errors = validate_layer_fields(self.spec)
        self.assertEqual(errors, [])

    def test_color_zone_fields_complete(self) -> None:
        errors = validate_color_zone_fields(self.spec)
        self.assertEqual(errors, [])

    def test_view_modes_complete(self) -> None:
        errors = validate_view_modes(self.spec)
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

    def test_missing_layer_fields_item_detected(self) -> None:
        bad_spec = {"layer_fields": ["layerNumber"]}
        errors = validate_layer_fields(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_color_zone_fields_item_detected(self) -> None:
        bad_spec = {"color_zone_fields": []}
        errors = validate_color_zone_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_view_modes_item_detected(self) -> None:
        bad_spec = {"view_modes": []}
        errors = validate_view_modes(bad_spec)
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
