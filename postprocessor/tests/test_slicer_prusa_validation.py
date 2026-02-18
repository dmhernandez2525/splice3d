"""Tests for F7.2 slicer prusa acceptance validation."""

import unittest

from postprocessor.slicer_prusa_validation import (
    generate_report,
    load_spec,
    validate_parse_modes,
    validate_mmu_fields,
    validate_gcode_markers,
    validate_recipe_fields,
    validate_stats_fields,
    validate_features,
)


class TestSlicerPrusaValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_parse_modes_complete(self) -> None:
        errors = validate_parse_modes(self.spec)
        self.assertEqual(errors, [])

    def test_mmu_fields_complete(self) -> None:
        errors = validate_mmu_fields(self.spec)
        self.assertEqual(errors, [])

    def test_gcode_markers_complete(self) -> None:
        errors = validate_gcode_markers(self.spec)
        self.assertEqual(errors, [])

    def test_recipe_fields_complete(self) -> None:
        errors = validate_recipe_fields(self.spec)
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

    def test_missing_parse_modes_item_detected(self) -> None:
        bad_spec = {"parse_modes": ["SINGLE_EXTRUDER"]}
        errors = validate_parse_modes(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_mmu_fields_item_detected(self) -> None:
        bad_spec = {"mmu_fields": []}
        errors = validate_mmu_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_gcode_markers_item_detected(self) -> None:
        bad_spec = {"gcode_markers": []}
        errors = validate_gcode_markers(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_recipe_fields_item_detected(self) -> None:
        bad_spec = {"recipe_fields": []}
        errors = validate_recipe_fields(bad_spec)
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
