"""Tests for F4.4 batch processor acceptance validation."""

import unittest

from postprocessor.batch_processor_validation import (
    generate_report,
    load_spec,
    validate_batch_modes,
    validate_features,
    validate_session_fields,
)


class TestBatchProcessorValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("batch_modes", self.spec)
        self.assertIn("features", self.spec)

    def test_batch_modes_complete(self) -> None:
        errors = validate_batch_modes(self.spec)
        self.assertEqual(errors, [])

    def test_session_fields_complete(self) -> None:
        errors = validate_session_fields(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_mode_detected(self) -> None:
        bad_spec = {"batch_modes": ["SINGLE"]}
        errors = validate_batch_modes(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_history_size_reasonable(self) -> None:
        size = self.spec.get("max_batch_history", 0)
        self.assertGreaterEqual(size, 8)
        self.assertLessEqual(size, 64)


if __name__ == "__main__":
    unittest.main()
