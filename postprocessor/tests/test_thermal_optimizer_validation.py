"""Tests for F6.2 thermal optimization acceptance validation."""

import unittest

from postprocessor.thermal_optimizer_validation import (
    generate_report,
    load_spec,
    validate_features,
    validate_preheat_fields,
    validate_stats_fields,
    validate_thermal_states,
    validate_thresholds,
)


class TestThermalOptimizerValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("thermal_states", self.spec)
        self.assertIn("preheat_fields", self.spec)

    def test_thermal_states_complete(self) -> None:
        errors = validate_thermal_states(self.spec)
        self.assertEqual(errors, [])

    def test_preheat_fields_complete(self) -> None:
        errors = validate_preheat_fields(self.spec)
        self.assertEqual(errors, [])

    def test_stats_fields_complete(self) -> None:
        errors = validate_stats_fields(self.spec)
        self.assertEqual(errors, [])

    def test_thresholds_valid(self) -> None:
        errors = validate_thresholds(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_state_detected(self) -> None:
        bad_spec = {"thermal_states": ["IDLE", "COOLING"]}
        errors = validate_thermal_states(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_missing_preheat_field_detected(self) -> None:
        bad_spec = {"preheat_fields": ["material"]}
        errors = validate_preheat_fields(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_bad_threshold_detected(self) -> None:
        bad_spec = {
            "heat_reuse_threshold_c": 0,
            "preheat_lead_time_ms": -1,
            "max_preheat_queue": 0,
        }
        errors = validate_thresholds(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_preheat_queue_defined(self) -> None:
        self.assertEqual(self.spec.get("max_preheat_queue"), 8)

    def test_heat_reuse_threshold_defined(self) -> None:
        self.assertEqual(self.spec.get("heat_reuse_threshold_c"), 15)

    def test_five_thermal_states_defined(self) -> None:
        states = self.spec.get("thermal_states", [])
        self.assertEqual(len(states), 5)


if __name__ == "__main__":
    unittest.main()
