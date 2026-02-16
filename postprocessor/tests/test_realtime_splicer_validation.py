"""Tests for F10.1 realtime splicer acceptance validation."""

import unittest

from postprocessor.realtime_splicer_validation import (
    generate_report,
    load_spec,
    validate_sync_states,
    validate_buffer_fields,
    validate_timing_fields,
    validate_printer_fields,
    validate_stats_fields,
    validate_features,
)


class TestRealtimeSplicerValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_sync_states_complete(self) -> None:
        errors = validate_sync_states(self.spec)
        self.assertEqual(errors, [])

    def test_buffer_fields_complete(self) -> None:
        errors = validate_buffer_fields(self.spec)
        self.assertEqual(errors, [])

    def test_timing_fields_complete(self) -> None:
        errors = validate_timing_fields(self.spec)
        self.assertEqual(errors, [])

    def test_printer_fields_complete(self) -> None:
        errors = validate_printer_fields(self.spec)
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

    def test_missing_sync_states_item_detected(self) -> None:
        bad_spec = {"sync_states": ["IDLE"]}
        errors = validate_sync_states(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
