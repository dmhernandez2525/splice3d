"""Tests for F7.3 slicer cura acceptance validation."""

import unittest

from postprocessor.slicer_cura_validation import (
    generate_report,
    load_spec,
    validate_extruder_modes,
    validate_block_types,
    validate_plugin_fields,
    validate_gcode_patterns,
    validate_stats_fields,
    validate_features,
)


class TestSlicerCuraValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_extruder_modes_complete(self) -> None:
        errors = validate_extruder_modes(self.spec)
        self.assertEqual(errors, [])

    def test_block_types_complete(self) -> None:
        errors = validate_block_types(self.spec)
        self.assertEqual(errors, [])

    def test_plugin_fields_complete(self) -> None:
        errors = validate_plugin_fields(self.spec)
        self.assertEqual(errors, [])

    def test_gcode_patterns_complete(self) -> None:
        errors = validate_gcode_patterns(self.spec)
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

    def test_missing_extruder_modes_item_detected(self) -> None:
        bad_spec = {"extruder_modes": ["SINGLE"]}
        errors = validate_extruder_modes(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_block_types_item_detected(self) -> None:
        bad_spec = {"block_types": []}
        errors = validate_block_types(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_plugin_fields_item_detected(self) -> None:
        bad_spec = {"plugin_fields": []}
        errors = validate_plugin_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_gcode_patterns_item_detected(self) -> None:
        bad_spec = {"gcode_patterns": []}
        errors = validate_gcode_patterns(bad_spec)
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
