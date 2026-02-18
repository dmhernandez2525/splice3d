"""Tests for F3.2 splice execution acceptance validation."""

import unittest

from postprocessor.splice_execution_validation import (
    generate_report,
    load_spec,
    validate_acceptance_limits,
    validate_material_profiles,
    validate_splice_phases,
)


class TestSpliceExecutionValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("acceptance_limits", self.spec)
        self.assertIn("splice_phases", self.spec)
        self.assertIn("material_profiles", self.spec)

    def test_acceptance_limits_valid(self) -> None:
        errors = validate_acceptance_limits(self.spec)
        self.assertEqual(errors, [])

    def test_splice_phases_complete(self) -> None:
        errors = validate_splice_phases(self.spec)
        self.assertEqual(errors, [])

    def test_material_profiles_valid(self) -> None:
        errors = validate_material_profiles(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_quality_features_present(self) -> None:
        features = self.spec.get("quality_features", [])
        self.assertIn("pull_test_verification", features)
        self.assertIn("encoder_slip_quality_scoring", features)
        self.assertIn("timing_estimation", features)

    def test_missing_phase_detected(self) -> None:
        bad_spec = {"splice_phases": ["IDLE", "COMPLETE"]}
        errors = validate_splice_phases(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_out_of_range_bond_strength(self) -> None:
        bad_spec = {"acceptance_limits": {"pla_bond_strength_n": 0}}
        errors = validate_acceptance_limits(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
