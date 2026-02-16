"""Tests for F7.1 OrcaSlicer plugin acceptance validation."""

import unittest

from postprocessor.slicer_orca_validation import (
    generate_report,
    load_spec,
    validate_color_fields,
    validate_features,
    validate_orca_patterns,
    validate_parse_states,
    validate_recipe_fields,
    validate_stats_fields,
    validate_tool_change_fields,
)


class TestSlicerOrcaValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("parse_states", self.spec)
        self.assertIn("features", self.spec)

    def test_parse_states_complete(self) -> None:
        errors = validate_parse_states(self.spec)
        self.assertEqual(errors, [])

    def test_tool_change_fields_complete(self) -> None:
        errors = validate_tool_change_fields(self.spec)
        self.assertEqual(errors, [])

    def test_color_fields_complete(self) -> None:
        errors = validate_color_fields(self.spec)
        self.assertEqual(errors, [])

    def test_recipe_fields_complete(self) -> None:
        errors = validate_recipe_fields(self.spec)
        self.assertEqual(errors, [])

    def test_stats_fields_complete(self) -> None:
        errors = validate_stats_fields(self.spec)
        self.assertEqual(errors, [])

    def test_orca_patterns_complete(self) -> None:
        errors = validate_orca_patterns(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_parse_state_detected(self) -> None:
        bad_spec = {"parse_states": ["IDLE"]}
        errors = validate_parse_states(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_tool_change_field_detected(self) -> None:
        bad_spec = {"tool_change_fields": ["lineNumber"]}
        errors = validate_tool_change_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_color_field_detected(self) -> None:
        bad_spec = {"color_fields": ["toolIndex"]}
        errors = validate_color_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_pattern_detected(self) -> None:
        bad_spec = {"orca_patterns": ["tool_change_Tn"]}
        errors = validate_orca_patterns(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_tool_changes_defined(self) -> None:
        self.assertEqual(self.spec.get("max_tool_changes"), 64)

    def test_max_colors_defined(self) -> None:
        self.assertEqual(self.spec.get("max_colors"), 8)

    def test_six_parse_states_defined(self) -> None:
        states = self.spec.get("parse_states", [])
        self.assertEqual(len(states), 6)

    def test_four_orca_patterns_defined(self) -> None:
        patterns = self.spec.get("orca_patterns", [])
        self.assertEqual(len(patterns), 4)


if __name__ == "__main__":
    unittest.main()
