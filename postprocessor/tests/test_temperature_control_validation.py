"""Tests for F2.3 temperature control acceptance validation."""

import unittest
from pathlib import Path

from postprocessor.temperature_control_validation import (
    generate_report,
    load_spec,
    validate_acceptance_limits,
    validate_heating_stages,
    validate_material_profiles,
    validate_safety_features,
)


class TestTemperatureControlValidation(unittest.TestCase):
    """Verify the temperature control spec passes all checks."""

    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("acceptance_limits", self.spec)
        self.assertIn("material_profiles", self.spec)
        self.assertIn("safety_features", self.spec)
        self.assertIn("heating_stages", self.spec)

    def test_acceptance_limits_valid(self) -> None:
        errors = validate_acceptance_limits(self.spec)
        self.assertEqual(errors, [], f"Acceptance limit errors: {errors}")

    def test_material_profiles_valid(self) -> None:
        errors = validate_material_profiles(self.spec)
        self.assertEqual(errors, [], f"Material profile errors: {errors}")

    def test_safety_features_complete(self) -> None:
        errors = validate_safety_features(self.spec)
        self.assertEqual(errors, [], f"Safety feature errors: {errors}")

    def test_heating_stages_complete(self) -> None:
        errors = validate_heating_stages(self.spec)
        self.assertEqual(errors, [], f"Heating stage errors: {errors}")

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"], f"Report errors: {report['errors']}")
        self.assertEqual(report["error_count"], 0)

    def test_pla_profile_values(self) -> None:
        pla = self.spec["material_profiles"]["PLA"]
        self.assertEqual(pla["splice_target_c"], 210)
        self.assertEqual(pla["min_motion_c"], 180)
        self.assertAlmostEqual(pla["ramp_rate_c_per_s"], 2.0)

    def test_abs_profile_values(self) -> None:
        abs_profile = self.spec["material_profiles"]["ABS"]
        self.assertEqual(abs_profile["splice_target_c"], 250)
        self.assertGreater(abs_profile["soak_time_ms"], 2000)


if __name__ == "__main__":
    unittest.main()
