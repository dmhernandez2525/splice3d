"""Tests for F5.2 cross-material splicing acceptance validation."""

import unittest

from postprocessor.cross_material_validation import (
    generate_report,
    load_spec,
    validate_compat_levels,
    validate_features,
    validate_material_pairs,
    validate_override_fields,
    validate_score_range,
)


class TestCrossMaterialValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("compat_levels", self.spec)
        self.assertIn("material_pairs", self.spec)

    def test_compat_levels_complete(self) -> None:
        errors = validate_compat_levels(self.spec)
        self.assertEqual(errors, [])

    def test_material_pairs_valid(self) -> None:
        errors = validate_material_pairs(self.spec)
        self.assertEqual(errors, [])

    def test_override_fields_complete(self) -> None:
        errors = validate_override_fields(self.spec)
        self.assertEqual(errors, [])

    def test_score_range_valid(self) -> None:
        errors = validate_score_range(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_level_detected(self) -> None:
        bad_spec = {"compat_levels": ["GOOD", "POOR"]}
        errors = validate_compat_levels(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_invalid_pair_type_detected(self) -> None:
        bad_spec = {
            "material_pairs": [
                {"a": "NYLON", "b": "PLA", "level": "GOOD"}
            ]
        }
        errors = validate_material_pairs(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_bad_score_range_detected(self) -> None:
        bad_spec = {"score_range": {"min": 10, "max": 50}}
        errors = validate_score_range(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_all_four_types_in_pairs(self) -> None:
        pairs = self.spec.get("material_pairs", [])
        types_seen = set()
        for pair in pairs:
            types_seen.add(pair["a"])
            types_seen.add(pair["b"])
        for t in ["PLA", "PETG", "ABS", "TPU"]:
            self.assertIn(t, types_seen)

    def test_at_least_six_pairs(self) -> None:
        pairs = self.spec.get("material_pairs", [])
        self.assertGreaterEqual(len(pairs), 6)


if __name__ == "__main__":
    unittest.main()
