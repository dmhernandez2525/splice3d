"""Tests for F8.1 recipe editor acceptance validation."""

import unittest

from postprocessor.recipe_editor_validation import (
    generate_report,
    load_spec,
    validate_segment_fields,
    validate_recipe_fields,
    validate_edit_operations,
    validate_stats_fields,
    validate_features,
)


class TestRecipeEditorValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_segment_fields_complete(self) -> None:
        errors = validate_segment_fields(self.spec)
        self.assertEqual(errors, [])

    def test_recipe_fields_complete(self) -> None:
        errors = validate_recipe_fields(self.spec)
        self.assertEqual(errors, [])

    def test_edit_operations_complete(self) -> None:
        errors = validate_edit_operations(self.spec)
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

    def test_missing_segment_fields_item_detected(self) -> None:
        bad_spec = {"segment_fields": ["index"]}
        errors = validate_segment_fields(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_recipe_fields_item_detected(self) -> None:
        bad_spec = {"recipe_fields": []}
        errors = validate_recipe_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_edit_operations_item_detected(self) -> None:
        bad_spec = {"edit_operations": []}
        errors = validate_edit_operations(bad_spec)
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
