"""Tests for F10.2 multi color acceptance validation."""

import unittest

from postprocessor.multi_color_validation import (
    generate_report,
    load_spec,
    validate_channel_states,
    validate_channel_fields,
    validate_switch_fields,
    validate_mapping_fields,
    validate_stats_fields,
    validate_features,
)


class TestMultiColorValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_channel_states_complete(self) -> None:
        errors = validate_channel_states(self.spec)
        self.assertEqual(errors, [])

    def test_channel_fields_complete(self) -> None:
        errors = validate_channel_fields(self.spec)
        self.assertEqual(errors, [])

    def test_switch_fields_complete(self) -> None:
        errors = validate_switch_fields(self.spec)
        self.assertEqual(errors, [])

    def test_mapping_fields_complete(self) -> None:
        errors = validate_mapping_fields(self.spec)
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

    def test_missing_channel_states_item_detected(self) -> None:
        bad_spec = {"channel_states": ["EMPTY"]}
        errors = validate_channel_states(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_channel_fields_item_detected(self) -> None:
        bad_spec = {"channel_fields": []}
        errors = validate_channel_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_switch_fields_item_detected(self) -> None:
        bad_spec = {"switch_fields": []}
        errors = validate_switch_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_mapping_fields_item_detected(self) -> None:
        bad_spec = {"mapping_fields": []}
        errors = validate_mapping_fields(bad_spec)
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
