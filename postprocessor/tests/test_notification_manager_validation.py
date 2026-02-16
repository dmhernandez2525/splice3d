"""Tests for F9.4 notification manager acceptance validation."""

import unittest

from postprocessor.notification_manager_validation import (
    generate_report,
    load_spec,
    validate_priority_levels,
    validate_event_types,
    validate_channel_fields,
    validate_notification_fields,
    validate_stats_fields,
    validate_features,
)


class TestNotificationManagerValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_priority_levels_complete(self) -> None:
        errors = validate_priority_levels(self.spec)
        self.assertEqual(errors, [])

    def test_event_types_complete(self) -> None:
        errors = validate_event_types(self.spec)
        self.assertEqual(errors, [])

    def test_channel_fields_complete(self) -> None:
        errors = validate_channel_fields(self.spec)
        self.assertEqual(errors, [])

    def test_notification_fields_complete(self) -> None:
        errors = validate_notification_fields(self.spec)
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

    def test_missing_priority_levels_item_detected(self) -> None:
        bad_spec = {"priority_levels": ["LOW"]}
        errors = validate_priority_levels(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_event_types_item_detected(self) -> None:
        bad_spec = {"event_types": []}
        errors = validate_event_types(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_channel_fields_item_detected(self) -> None:
        bad_spec = {"channel_fields": []}
        errors = validate_channel_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_notification_fields_item_detected(self) -> None:
        bad_spec = {"notification_fields": []}
        errors = validate_notification_fields(bad_spec)
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
