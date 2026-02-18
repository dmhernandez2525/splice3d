"""Tests for F5.1 material database acceptance validation."""

import unittest

from postprocessor.material_database_validation import (
    generate_report,
    load_spec,
    validate_default_profiles,
    validate_features,
    validate_material_types,
    validate_profile_fields,
    validate_temperature_limits,
)


class TestMaterialDatabaseValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("material_types", self.spec)
        self.assertIn("features", self.spec)

    def test_material_types_complete(self) -> None:
        errors = validate_material_types(self.spec)
        self.assertEqual(errors, [])

    def test_profile_fields_complete(self) -> None:
        errors = validate_profile_fields(self.spec)
        self.assertEqual(errors, [])

    def test_default_profiles_present(self) -> None:
        errors = validate_default_profiles(self.spec)
        self.assertEqual(errors, [])

    def test_temperature_limits_valid(self) -> None:
        errors = validate_temperature_limits(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_type_detected(self) -> None:
        bad_spec = {"material_types": ["PLA", "PETG"]}
        errors = validate_material_types(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_bad_temp_limits_detected(self) -> None:
        bad_spec = {"temperature_limits": {"min_celsius": 300, "max_celsius": 200}}
        errors = validate_temperature_limits(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_profiles_reasonable(self) -> None:
        size = self.spec.get("max_profiles", 0)
        self.assertGreaterEqual(size, 8)
        self.assertLessEqual(size, 64)

    def test_default_profiles_cover_all_types(self) -> None:
        defaults = self.spec.get("default_profiles", [])
        prefixes = {n.split("-")[0] for n in defaults if "-" in n}
        for t in ["PLA", "PETG", "ABS", "TPU"]:
            self.assertIn(t, prefixes)

    def test_missing_feature_detected(self) -> None:
        bad_spec = {"features": ["brand_specific_profiles"]}
        errors = validate_features(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
