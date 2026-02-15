"""Tests for F6.4 speed optimization acceptance validation."""

import unittest

from postprocessor.speed_optimizer_validation import (
    generate_report,
    load_spec,
    validate_cycle_fields,
    validate_features,
    validate_op_states,
    validate_op_types,
    validate_overlap_pairs,
    validate_stats_fields,
)


class TestSpeedOptimizerValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("op_types", self.spec)
        self.assertIn("cycle_fields", self.spec)

    def test_op_types_complete(self) -> None:
        errors = validate_op_types(self.spec)
        self.assertEqual(errors, [])

    def test_op_states_complete(self) -> None:
        errors = validate_op_states(self.spec)
        self.assertEqual(errors, [])

    def test_overlap_pairs_valid(self) -> None:
        errors = validate_overlap_pairs(self.spec)
        self.assertEqual(errors, [])

    def test_cycle_fields_complete(self) -> None:
        errors = validate_cycle_fields(self.spec)
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

    def test_missing_op_type_detected(self) -> None:
        bad_spec = {"op_types": ["HEATING"]}
        errors = validate_op_types(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_op_state_detected(self) -> None:
        bad_spec = {"op_states": ["RUNNING"]}
        errors = validate_op_states(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_invalid_overlap_pair_detected(self) -> None:
        bad_spec = {"overlap_pairs": [{"a": "INVALID", "b": "HEATING"}]}
        errors = validate_overlap_pairs(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_same_type_overlap_detected(self) -> None:
        bad_spec = {
            "overlap_pairs": [
                {"a": "HEATING", "b": "HEATING"},
                {"a": "COOLING", "b": "POSITIONING"},
            ]
        }
        errors = validate_overlap_pairs(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_parallel_ops_defined(self) -> None:
        self.assertEqual(self.spec.get("max_parallel_ops"), 8)

    def test_max_cycle_records_defined(self) -> None:
        self.assertEqual(self.spec.get("max_cycle_records"), 16)

    def test_six_op_types_defined(self) -> None:
        op_types = self.spec.get("op_types", [])
        self.assertEqual(len(op_types), 6)

    def test_at_least_two_overlap_pairs(self) -> None:
        pairs = self.spec.get("overlap_pairs", [])
        self.assertGreaterEqual(len(pairs), 2)


if __name__ == "__main__":
    unittest.main()
