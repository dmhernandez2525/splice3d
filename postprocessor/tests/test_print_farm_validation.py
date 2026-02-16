"""Tests for F10.3 print farm acceptance validation."""

import unittest

from postprocessor.print_farm_validation import (
    generate_report,
    load_spec,
    validate_printer_states,
    validate_printer_fields,
    validate_farm_job_fields,
    validate_pool_fields,
    validate_stats_fields,
    validate_features,
)


class TestPrintFarmValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_printer_states_complete(self) -> None:
        errors = validate_printer_states(self.spec)
        self.assertEqual(errors, [])

    def test_printer_fields_complete(self) -> None:
        errors = validate_printer_fields(self.spec)
        self.assertEqual(errors, [])

    def test_farm_job_fields_complete(self) -> None:
        errors = validate_farm_job_fields(self.spec)
        self.assertEqual(errors, [])

    def test_pool_fields_complete(self) -> None:
        errors = validate_pool_fields(self.spec)
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

    def test_missing_printer_states_item_detected(self) -> None:
        bad_spec = {"printer_states": ["OFFLINE"]}
        errors = validate_printer_states(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
