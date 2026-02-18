"""Tests for F6.1 segment batching acceptance validation."""

import unittest

from postprocessor.segment_batching_validation import (
    generate_report,
    load_spec,
    validate_features,
    validate_reorder_ratio_range,
    validate_segment_fields,
    validate_stats_fields,
    validate_strategies,
)


class TestSegmentBatchingValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("strategies", self.spec)
        self.assertIn("segment_fields", self.spec)

    def test_strategies_complete(self) -> None:
        errors = validate_strategies(self.spec)
        self.assertEqual(errors, [])

    def test_segment_fields_complete(self) -> None:
        errors = validate_segment_fields(self.spec)
        self.assertEqual(errors, [])

    def test_stats_fields_complete(self) -> None:
        errors = validate_stats_fields(self.spec)
        self.assertEqual(errors, [])

    def test_reorder_ratio_range_valid(self) -> None:
        errors = validate_reorder_ratio_range(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_strategy_detected(self) -> None:
        bad_spec = {"strategies": ["NONE", "GROUP_BY_MATERIAL"]}
        errors = validate_strategies(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_segment_field_detected(self) -> None:
        bad_spec = {"segment_fields": ["segmentId"]}
        errors = validate_segment_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_bad_ratio_range_detected(self) -> None:
        bad_spec = {"reorder_ratio_range": {"min": 0.5, "max": 2.0}}
        errors = validate_reorder_ratio_range(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_batch_segments_defined(self) -> None:
        self.assertEqual(self.spec.get("max_batch_segments"), 32)

    def test_material_types_present(self) -> None:
        types = self.spec.get("material_types", [])
        for t in ["PLA", "PETG", "ABS", "TPU"]:
            self.assertIn(t, types)

    def test_four_strategies_defined(self) -> None:
        strategies = self.spec.get("strategies", [])
        self.assertEqual(len(strategies), 4)


if __name__ == "__main__":
    unittest.main()
