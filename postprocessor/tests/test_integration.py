"""
Integration tests for Splice3D post-processor.

Tests the full pipeline from G-code to recipe.
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from gcode_parser import GCodeParser
from recipe_generator import RecipeGenerator
from gcode_modifier import GCodeModifier
from recipe_validator import RecipeValidator


class TestFullPipeline(unittest.TestCase):
    """Integration tests for the full G-code processing pipeline."""
    
    def test_simple_two_color(self):
        """Test processing a simple two-color G-code."""
        gcode = """
        G28
        T0
        G1 X10 Y10 E50.0 F1200
        G1 X20 Y20 E100.0
        T1
        G1 X30 Y30 E150.0
        G1 X40 Y40 E200.0
        M104 S0
        """
        
        lines = gcode.strip().split('\n')
        
        # Parse
        parser = GCodeParser()
        result = parser.parse_lines(lines)
        
        self.assertEqual(len(result.segments), 2)
        self.assertEqual(result.color_count, 2)
        
        # Generate recipe
        generator = RecipeGenerator()
        recipe = generator.generate(result)
        
        self.assertEqual(len(recipe.segments), 2)
        self.assertGreater(recipe.total_length_mm, 0)
        
        # Modify G-code
        modifier = GCodeModifier()
        modified, stats = modifier.modify_lines(lines)
        
        self.assertEqual(stats['tool_changes_removed'], 2)
    
    def test_m600_color_changes(self):
        """Test M600 color change detection."""
        gcode = """
        G28
        G1 X10 Y10 E50.0 F1200
        M600
        G1 X20 Y20 E100.0
        M600
        G1 X30 Y30 E150.0
        """
        
        lines = gcode.strip().split('\n')
        
        parser = GCodeParser()
        result = parser.parse_lines(lines)
        
        # Should detect 3 segments from 2 M600 commands
        self.assertEqual(len(result.segments), 3)
        self.assertEqual(result.color_count, 2)  # Toggles between 0 and 1
    
    def test_recipe_validation(self):
        """Test recipe validation catches errors."""
        # Valid recipe
        valid_recipe = {
            "version": "1.0",
            "segments": [
                {"color": 0, "length_mm": 50.0},
                {"color": 1, "length_mm": 50.0},
            ]
        }
        
        validator = RecipeValidator()
        result = validator.validate(valid_recipe)
        
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_recipe_validation_errors(self):
        """Test recipe validation catches errors."""
        # Invalid: Missing segments
        invalid_recipe = {"version": "1.0"}
        
        validator = RecipeValidator()
        result = validator.validate(invalid_recipe)
        
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_file_roundtrip(self):
        """Test writing and reading recipe file."""
        gcode = """
        T0
        G1 X10 Y10 E50.0 F1200
        T1
        G1 X20 Y20 E100.0
        """
        
        lines = gcode.strip().split('\n')
        
        parser = GCodeParser()
        result = parser.parse_lines(lines)
        
        generator = RecipeGenerator(color_names={0: "white", 1: "black"})
        recipe = generator.generate(result)
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(generator.to_json(recipe))
            temp_path = f.name
        
        try:
            # Read back and validate
            validator = RecipeValidator()
            result = validator.validate_file(temp_path)
            
            self.assertTrue(result.valid)
            
            # Read and check content
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            
            self.assertEqual(loaded['colors']['0'], 'white')
            self.assertEqual(loaded['colors']['1'], 'black')
            
        finally:
            Path(temp_path).unlink()
    
    def test_large_segment_count(self):
        """Test handling many segments (like Starry Night)."""
        # Simulate 100 rapid tool changes
        lines = []
        e_value = 0.0
        
        for i in range(100):
            lines.append(f"T{i % 2}")
            e_value += 10.0
            lines.append(f"G1 X{i} Y{i} E{e_value}")
        
        parser = GCodeParser()
        result = parser.parse_lines(lines)
        
        self.assertEqual(len(result.segments), 100)
        self.assertEqual(result.color_count, 2)
        self.assertAlmostEqual(result.total_length_mm, 1000.0, places=1)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and unusual inputs."""
    
    def test_empty_gcode(self):
        """Test handling empty G-code."""
        parser = GCodeParser()
        result = parser.parse_lines([])
        
        self.assertEqual(len(result.segments), 0)
        self.assertIn("No extrusion segments found", result.warnings)
    
    def test_no_tool_changes(self):
        """Test G-code with no tool changes."""
        gcode = """
        G28
        G1 X10 Y10 E50.0 F1200
        G1 X20 Y20 E100.0
        """
        
        parser = GCodeParser()
        result = parser.parse_lines(gcode.strip().split('\n'))
        
        # Should still capture the extrusion as one segment
        self.assertEqual(result.color_count, 1)
        self.assertIn("Single color detected", result.warnings)
    
    def test_relative_extrusion(self):
        """Test M83 relative extrusion mode."""
        gcode = """
        M83
        T0
        G1 X10 Y10 E10.0 F1200
        G1 X20 Y20 E10.0
        T1
        G1 X30 Y30 E10.0
        """
        
        parser = GCodeParser()
        result = parser.parse_lines(gcode.strip().split('\n'))
        
        # Relative mode: each E10 adds 10mm
        self.assertEqual(len(result.segments), 2)
        self.assertAlmostEqual(result.total_length_mm, 30.0, places=1)
    
    def test_e_reset(self):
        """Test G92 E0 reset handling."""
        gcode = """
        T0
        G1 X10 Y10 E100.0 F1200
        G92 E0
        G1 X20 Y20 E50.0
        T1
        G1 X30 Y30 E100.0
        """
        
        parser = GCodeParser()
        result = parser.parse_lines(gcode.strip().split('\n'))
        
        # Should handle reset correctly
        # T0 segment: 100 + 50 = 150mm
        # T1 segment: 50mm
        self.assertEqual(len(result.segments), 2)


if __name__ == "__main__":
    unittest.main()
