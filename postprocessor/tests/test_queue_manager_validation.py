"""Tests for F8.4 queue manager acceptance validation."""

import unittest

from postprocessor.queue_manager_validation import (
    generate_report,
    load_spec,
    validate_queue_item_fields,
    validate_queue_states,
    validate_operations,
    validate_stats_fields,
    validate_features,
)


class TestQueueManagerValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_queue_item_fields_complete(self) -> None:
        errors = validate_queue_item_fields(self.spec)
        self.assertEqual(errors, [])

    def test_queue_states_complete(self) -> None:
        errors = validate_queue_states(self.spec)
        self.assertEqual(errors, [])

    def test_operations_complete(self) -> None:
        errors = validate_operations(self.spec)
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

    def test_missing_queue_item_fields_item_detected(self) -> None:
        bad_spec = {"queue_item_fields": ["jobId"]}
        errors = validate_queue_item_fields(bad_spec)
        self.assertGreater(len(errors), 0)


    def test_missing_queue_states_item_detected(self) -> None:
        bad_spec = {"queue_states": []}
        errors = validate_queue_states(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_operations_item_detected(self) -> None:
        bad_spec = {"operations": []}
        errors = validate_operations(bad_spec)
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
