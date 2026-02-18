"""Tests for F5.3 custom profile editor acceptance validation."""

import unittest

from postprocessor.custom_profile_validation import (
    generate_report,
    load_spec,
    validate_checksum,
    validate_features,
    validate_operations,
    validate_persistence_fields,
    validate_slot_fields,
    validate_stats_fields,
)


class TestCustomProfileValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("operations", self.spec)
        self.assertIn("features", self.spec)

    def test_operations_complete(self) -> None:
        errors = validate_operations(self.spec)
        self.assertEqual(errors, [])

    def test_persistence_fields_complete(self) -> None:
        errors = validate_persistence_fields(self.spec)
        self.assertEqual(errors, [])

    def test_slot_fields_complete(self) -> None:
        errors = validate_slot_fields(self.spec)
        self.assertEqual(errors, [])

    def test_stats_fields_complete(self) -> None:
        errors = validate_stats_fields(self.spec)
        self.assertEqual(errors, [])

    def test_checksum_valid(self) -> None:
        errors = validate_checksum(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_operation_detected(self) -> None:
        bad_spec = {"operations": ["create", "read"]}
        errors = validate_operations(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_bad_magic_detected(self) -> None:
        bad_spec = {"profile_magic": 0, "checksum_algorithm": "xor"}
        errors = validate_checksum(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_profiles_reasonable(self) -> None:
        size = self.spec.get("max_custom_profiles", 0)
        self.assertGreaterEqual(size, 4)
        self.assertLessEqual(size, 32)

    def test_eeprom_base_address_positive(self) -> None:
        addr = self.spec.get("eeprom_base_address", 0)
        self.assertGreater(addr, 0)

    def test_missing_feature_detected(self) -> None:
        bad_spec = {"features": ["create_custom_profile"]}
        errors = validate_features(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
