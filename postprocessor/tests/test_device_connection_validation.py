"""Tests for F8.3 device connection acceptance validation."""

import unittest

from postprocessor.device_connection_validation import (
    generate_report,
    load_spec,
    validate_connection_states,
    validate_device_fields,
    validate_command_fields,
    validate_stats_fields,
    validate_features,
)


class TestDeviceConnectionValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_connection_states_complete(self) -> None:
        errors = validate_connection_states(self.spec)
        self.assertEqual(errors, [])

    def test_device_fields_complete(self) -> None:
        errors = validate_device_fields(self.spec)
        self.assertEqual(errors, [])

    def test_command_fields_complete(self) -> None:
        errors = validate_command_fields(self.spec)
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

    def test_missing_connection_states_item_detected(self) -> None:
        bad_spec = {"connection_states": ["DISCONNECTED"]}
        errors = validate_connection_states(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_device_fields_item_detected(self) -> None:
        bad_spec = {"device_fields": []}
        errors = validate_device_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_command_fields_item_detected(self) -> None:
        bad_spec = {"command_fields": []}
        errors = validate_command_fields(bad_spec)
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
