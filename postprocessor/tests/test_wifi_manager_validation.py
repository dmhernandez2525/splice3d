"""Tests for F9.1 wifi manager acceptance validation."""

import unittest

from postprocessor.wifi_manager_validation import (
    generate_report,
    load_spec,
    validate_wifi_modes,
    validate_connection_states,
    validate_network_fields,
    validate_config_fields,
    validate_stats_fields,
    validate_features,
)


class TestWifiManagerValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_wifi_modes_complete(self) -> None:
        errors = validate_wifi_modes(self.spec)
        self.assertEqual(errors, [])

    def test_connection_states_complete(self) -> None:
        errors = validate_connection_states(self.spec)
        self.assertEqual(errors, [])

    def test_network_fields_complete(self) -> None:
        errors = validate_network_fields(self.spec)
        self.assertEqual(errors, [])

    def test_config_fields_complete(self) -> None:
        errors = validate_config_fields(self.spec)
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

    def test_missing_wifi_modes_item_detected(self) -> None:
        bad_spec = {"wifi_modes": ["OFF"]}
        errors = validate_wifi_modes(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_connection_states_item_detected(self) -> None:
        bad_spec = {"connection_states": []}
        errors = validate_connection_states(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_network_fields_item_detected(self) -> None:
        bad_spec = {"network_fields": []}
        errors = validate_network_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_config_fields_item_detected(self) -> None:
        bad_spec = {"config_fields": []}
        errors = validate_config_fields(bad_spec)
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
