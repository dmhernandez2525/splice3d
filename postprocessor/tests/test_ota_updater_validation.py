"""Tests for F9.3 ota updater acceptance validation."""

import unittest

from postprocessor.ota_updater_validation import (
    generate_report,
    load_spec,
    validate_update_states,
    validate_chunk_fields,
    validate_firmware_fields,
    validate_progress_fields,
    validate_stats_fields,
    validate_features,
)


class TestOtaUpdaterValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_update_states_complete(self) -> None:
        errors = validate_update_states(self.spec)
        self.assertEqual(errors, [])

    def test_chunk_fields_complete(self) -> None:
        errors = validate_chunk_fields(self.spec)
        self.assertEqual(errors, [])

    def test_firmware_fields_complete(self) -> None:
        errors = validate_firmware_fields(self.spec)
        self.assertEqual(errors, [])

    def test_progress_fields_complete(self) -> None:
        errors = validate_progress_fields(self.spec)
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

    def test_missing_update_states_item_detected(self) -> None:
        bad_spec = {"update_states": ["IDLE"]}
        errors = validate_update_states(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
