"""
Tests for the filament profiles module.
"""

import unittest
from postprocessor.filament_profiles import (
    FilamentProfile,
    get_profile,
    get_profile_for_material,
    list_profiles,
    are_compatible,
    get_splice_params,
    PROFILES,
)


class TestFilamentProfile(unittest.TestCase):
    """Tests for the FilamentProfile dataclass."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        profile = FilamentProfile(name="Test", material="PLA")
        self.assertEqual(profile.splice_temp, 210)
        self.assertEqual(profile.heat_time_ms, 3000)
        self.assertEqual(profile.cooling_time_ms, 5000)
        self.assertEqual(profile.compression_mm, 2.0)
        self.assertIsNone(profile.brand)

    def test_compatible_with_default(self):
        """Test that compatible_with defaults to same material."""
        profile = FilamentProfile(name="Test", material="PLA")
        self.assertEqual(profile.compatible_with, ["PLA"])

    def test_custom_compatible_with(self):
        """Test custom compatible_with list."""
        profile = FilamentProfile(
            name="Test",
            material="PLA",
            compatible_with=["PLA", "PLA+", "PLA Matte"]
        )
        self.assertEqual(len(profile.compatible_with), 3)
        self.assertIn("PLA+", profile.compatible_with)


class TestGetProfile(unittest.TestCase):
    """Tests for get_profile function."""

    def test_get_existing_profile(self):
        """Test getting an existing profile."""
        profile = get_profile("pla")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.material, "PLA")

    def test_get_profile_case_insensitive(self):
        """Test that profile lookup is case insensitive."""
        profile1 = get_profile("PLA")
        profile2 = get_profile("pla")
        profile3 = get_profile("Pla")
        self.assertEqual(profile1, profile2)
        self.assertEqual(profile2, profile3)

    def test_get_nonexistent_profile(self):
        """Test getting a profile that doesn't exist."""
        profile = get_profile("nonexistent_material")
        self.assertIsNone(profile)

    def test_get_branded_profile(self):
        """Test getting a branded profile."""
        profile = get_profile("pla_bambu_matte")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.brand, "Bambu Lab")


class TestGetProfileForMaterial(unittest.TestCase):
    """Tests for get_profile_for_material function."""

    def test_get_generic_pla(self):
        """Test getting generic PLA profile."""
        profile = get_profile_for_material("PLA")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "Generic PLA")
        self.assertIsNone(profile.brand)

    def test_get_generic_petg(self):
        """Test getting generic PETG profile."""
        profile = get_profile_for_material("PETG")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.material, "PETG")

    def test_get_generic_abs(self):
        """Test getting generic ABS profile."""
        profile = get_profile_for_material("ABS")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.material, "ABS")

    def test_case_insensitive(self):
        """Test that material lookup is case insensitive."""
        profile1 = get_profile_for_material("pla")
        profile2 = get_profile_for_material("PLA")
        self.assertEqual(profile1.name, profile2.name)

    def test_nonexistent_material(self):
        """Test getting a material that doesn't exist."""
        profile = get_profile_for_material("UNKNOWN_MATERIAL")
        self.assertIsNone(profile)


class TestListProfiles(unittest.TestCase):
    """Tests for list_profiles function."""

    def test_returns_list(self):
        """Test that list_profiles returns a list."""
        profiles = list_profiles()
        self.assertIsInstance(profiles, list)

    def test_contains_common_profiles(self):
        """Test that common profiles are in the list."""
        profiles = list_profiles()
        self.assertIn("pla", profiles)
        self.assertIn("petg", profiles)
        self.assertIn("abs", profiles)

    def test_count_matches_profiles_dict(self):
        """Test that count matches PROFILES dict."""
        profiles = list_profiles()
        self.assertEqual(len(profiles), len(PROFILES))


class TestAreCompatible(unittest.TestCase):
    """Tests for are_compatible function."""

    def test_same_material_compatible(self):
        """Test that same material is compatible with itself."""
        self.assertTrue(are_compatible("PLA", "PLA"))
        self.assertTrue(are_compatible("PETG", "PETG"))
        self.assertTrue(are_compatible("ABS", "ABS"))

    def test_pla_variants_compatible(self):
        """Test that PLA variants are compatible."""
        self.assertTrue(are_compatible("PLA", "PLA+"))
        self.assertTrue(are_compatible("PLA", "PLA Matte"))

    def test_abs_asa_compatible(self):
        """Test that ABS and ASA are compatible."""
        self.assertTrue(are_compatible("ABS", "ASA"))
        self.assertTrue(are_compatible("ASA", "ABS"))

    def test_incompatible_materials(self):
        """Test that incompatible materials return False."""
        self.assertFalse(are_compatible("PLA", "PETG"))
        self.assertFalse(are_compatible("PLA", "ABS"))
        self.assertFalse(are_compatible("PETG", "ABS"))

    def test_unknown_material(self):
        """Test that unknown material returns False."""
        self.assertFalse(are_compatible("UNKNOWN", "PLA"))
        self.assertFalse(are_compatible("PLA", "UNKNOWN"))


class TestGetSpliceParams(unittest.TestCase):
    """Tests for get_splice_params function."""

    def test_same_material_params(self):
        """Test getting params for same material."""
        params = get_splice_params("PLA", "PLA")
        self.assertIsNotNone(params)
        self.assertIn("splice_temp", params)
        self.assertIn("heat_time_ms", params)
        self.assertIn("cooling_time_ms", params)
        self.assertIn("compression_mm", params)

    def test_compatible_materials_use_max(self):
        """Test that compatible materials use max values."""
        params = get_splice_params("ABS", "ASA")
        self.assertIsNotNone(params)
        # ASA has higher temp (255) than ABS (250)
        self.assertGreaterEqual(params["splice_temp"], 250)

    def test_incompatible_returns_none(self):
        """Test that incompatible materials return None."""
        params = get_splice_params("PLA", "PETG")
        self.assertIsNone(params)

    def test_unknown_material_returns_none(self):
        """Test that unknown material returns None."""
        params = get_splice_params("UNKNOWN", "PLA")
        self.assertIsNone(params)
        params = get_splice_params("PLA", "UNKNOWN")
        self.assertIsNone(params)


class TestProfilesData(unittest.TestCase):
    """Tests for the PROFILES data structure."""

    def test_all_profiles_have_required_fields(self):
        """Test that all profiles have required fields."""
        for name, profile in PROFILES.items():
            self.assertIsNotNone(profile.name, f"{name} missing name")
            self.assertIsNotNone(profile.material, f"{name} missing material")
            self.assertGreater(profile.splice_temp, 0, f"{name} invalid splice_temp")
            self.assertGreater(profile.heat_time_ms, 0, f"{name} invalid heat_time_ms")
            self.assertGreater(profile.cooling_time_ms, 0, f"{name} invalid cooling_time_ms")
            self.assertGreater(profile.compression_mm, 0, f"{name} invalid compression_mm")

    def test_temperatures_in_valid_range(self):
        """Test that temperatures are in valid printing range."""
        for name, profile in PROFILES.items():
            self.assertGreaterEqual(
                profile.splice_temp, 180,
                f"{name} temp too low: {profile.splice_temp}"
            )
            self.assertLessEqual(
                profile.splice_temp, 300,
                f"{name} temp too high: {profile.splice_temp}"
            )

    def test_pla_profiles_exist(self):
        """Test that PLA profiles exist."""
        self.assertIn("pla", PROFILES)
        self.assertEqual(PROFILES["pla"].material, "PLA")

    def test_petg_profiles_exist(self):
        """Test that PETG profiles exist."""
        self.assertIn("petg", PROFILES)
        self.assertEqual(PROFILES["petg"].material, "PETG")


if __name__ == "__main__":
    unittest.main()
