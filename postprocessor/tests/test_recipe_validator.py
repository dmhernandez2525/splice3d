"""
Tests for the recipe validator module.
"""

import unittest
import tempfile
import json
import os
from postprocessor.recipe_validator import (
    ValidationResult,
    RecipeValidator,
    validate_recipe,
)


class TestValidationResult(unittest.TestCase):
    """Tests for the ValidationResult dataclass."""

    def test_str_valid_no_warnings(self):
        """Test string output for valid result with no warnings."""
        result = ValidationResult(valid=True, errors=[], warnings=[])
        output = str(result)
        self.assertIn("✓ Recipe valid", output)

    def test_str_invalid_with_errors(self):
        """Test string output for invalid result with errors."""
        result = ValidationResult(
            valid=False,
            errors=["Missing segments", "Invalid color"],
            warnings=[]
        )
        output = str(result)
        self.assertIn("✗ Recipe invalid", output)
        self.assertIn("ERROR: Missing segments", output)
        self.assertIn("ERROR: Invalid color", output)

    def test_str_with_warnings(self):
        """Test string output with warnings."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=["Only one color used", "Very short total length"]
        )
        output = str(result)
        self.assertIn("WARNING: Only one color used", output)
        self.assertIn("WARNING: Very short total length", output)

    def test_str_with_errors_and_warnings(self):
        """Test string output with both errors and warnings."""
        result = ValidationResult(
            valid=False,
            errors=["No segments in recipe"],
            warnings=["Missing 'version' field"]
        )
        output = str(result)
        self.assertIn("ERROR: No segments in recipe", output)
        self.assertIn("WARNING: Missing 'version' field", output)


class TestRecipeValidator(unittest.TestCase):
    """Tests for the RecipeValidator class."""

    def setUp(self):
        self.validator = RecipeValidator()

    def test_valid_recipe(self):
        """Test validation of a valid recipe."""
        recipe = {
            "version": "1.0",
            "segments": [
                {"length_mm": 100.0, "color": 0},
                {"length_mm": 200.0, "color": 1},
                {"length_mm": 150.0, "color": 0},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)

    def test_missing_segments_field(self):
        """Test recipe with missing segments field."""
        recipe = {"version": "1.0"}
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertIn("Missing 'segments' field", result.errors)

    def test_empty_segments(self):
        """Test recipe with empty segments list."""
        recipe = {"segments": []}
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertIn("No segments in recipe", result.errors)

    def test_too_many_segments(self):
        """Test recipe with too many segments."""
        recipe = {
            "segments": [
                {"length_mm": 10.0, "color": i % 4}
                for i in range(10001)
            ]
        }
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertTrue(any("Too many segments" in e for e in result.errors))

    def test_segment_missing_length(self):
        """Test segment missing length_mm field."""
        recipe = {
            "segments": [
                {"color": 0},
                {"length_mm": 100.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertTrue(any("missing 'length_mm'" in e for e in result.errors))

    def test_segment_missing_color(self):
        """Test segment missing color field."""
        recipe = {
            "segments": [
                {"length_mm": 100.0},
                {"length_mm": 100.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertTrue(any("missing 'color'" in e for e in result.errors))

    def test_negative_length(self):
        """Test segment with negative length."""
        recipe = {
            "segments": [
                {"length_mm": -10.0, "color": 0},
                {"length_mm": 100.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertTrue(any("invalid length" in e for e in result.errors))

    def test_zero_length(self):
        """Test segment with zero length."""
        recipe = {
            "segments": [
                {"length_mm": 0, "color": 0},
                {"length_mm": 100.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertTrue(any("invalid length" in e for e in result.errors))

    def test_very_short_segment_warning(self):
        """Test warning for very short segments."""
        recipe = {
            "segments": [
                {"length_mm": 1.0, "color": 0},  # Below MIN_SEGMENT_LENGTH_MM
                {"length_mm": 200.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertTrue(any("shorter than" in w for w in result.warnings))

    def test_segment_too_long(self):
        """Test segment exceeding max length."""
        recipe = {
            "segments": [
                {"length_mm": 60000.0, "color": 0},  # Above MAX_SEGMENT_LENGTH_MM
                {"length_mm": 100.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertTrue(any("exceeds max" in e for e in result.errors))

    def test_too_many_colors(self):
        """Test recipe with too many colors."""
        recipe = {
            "segments": [
                {"length_mm": 100.0, "color": i}
                for i in range(9)  # 9 colors, max is 8
            ]
        }
        result = self.validator.validate(recipe)
        self.assertFalse(result.valid)
        self.assertTrue(any("Too many colors" in e for e in result.errors))

    def test_single_color_warning(self):
        """Test warning for single color (no splicing needed)."""
        recipe = {
            "segments": [
                {"length_mm": 100.0, "color": 0},
                {"length_mm": 200.0, "color": 0},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertTrue(any("Only one color" in w for w in result.warnings))

    def test_very_short_total_length_warning(self):
        """Test warning for very short total length."""
        recipe = {
            "segments": [
                {"length_mm": 10.0, "color": 0},
                {"length_mm": 10.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertTrue(any("Very short total length" in w for w in result.warnings))

    def test_missing_version_warning(self):
        """Test warning for missing version field."""
        recipe = {
            "segments": [
                {"length_mm": 100.0, "color": 0},
                {"length_mm": 200.0, "color": 1},
            ]
        }
        result = self.validator.validate(recipe)
        self.assertTrue(any("Missing 'version'" in w for w in result.warnings))

    def test_long_splice_time_warning(self):
        """Test warning for very long estimated splice time."""
        # Need enough segments to exceed 24 hours (24 * 3600 / 45 = 1920 segments)
        recipe = {
            "version": "1.0",
            "segments": [
                {"length_mm": 100.0, "color": i % 4}
                for i in range(2000)
            ]
        }
        result = self.validator.validate(recipe)
        self.assertTrue(any("Long splice time" in w for w in result.warnings))


class TestValidateFile(unittest.TestCase):
    """Tests for validate_file method."""

    def setUp(self):
        self.validator = RecipeValidator()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_file(self):
        """Test validating a valid JSON file."""
        recipe = {
            "version": "1.0",
            "segments": [
                {"length_mm": 100.0, "color": 0},
                {"length_mm": 200.0, "color": 1},
            ]
        }
        filepath = os.path.join(self.temp_dir, "valid.json")
        with open(filepath, 'w') as f:
            json.dump(recipe, f)

        result = self.validator.validate_file(filepath)
        self.assertTrue(result.valid)

    def test_invalid_json_file(self):
        """Test validating an invalid JSON file."""
        filepath = os.path.join(self.temp_dir, "invalid.json")
        with open(filepath, 'w') as f:
            f.write("{ not valid json }")

        result = self.validator.validate_file(filepath)
        self.assertFalse(result.valid)
        self.assertTrue(any("Invalid JSON" in e for e in result.errors))

    def test_nonexistent_file(self):
        """Test validating a file that doesn't exist."""
        filepath = os.path.join(self.temp_dir, "nonexistent.json")
        result = self.validator.validate_file(filepath)
        self.assertFalse(result.valid)
        self.assertTrue(any("Could not read file" in e for e in result.errors))


class TestValidateRecipeFunction(unittest.TestCase):
    """Tests for the validate_recipe convenience function."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_recipe_returns_true(self):
        """Test that valid recipe returns True."""
        recipe = {
            "version": "1.0",
            "segments": [
                {"length_mm": 100.0, "color": 0},
                {"length_mm": 200.0, "color": 1},
            ]
        }
        filepath = os.path.join(self.temp_dir, "valid.json")
        with open(filepath, 'w') as f:
            json.dump(recipe, f)

        result = validate_recipe(filepath)
        self.assertTrue(result)

    def test_invalid_recipe_returns_false(self):
        """Test that invalid recipe returns False."""
        recipe = {"segments": []}
        filepath = os.path.join(self.temp_dir, "invalid.json")
        with open(filepath, 'w') as f:
            json.dump(recipe, f)

        result = validate_recipe(filepath)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
