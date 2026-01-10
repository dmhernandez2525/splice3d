"""
Tests for Splice3D Recipe Generator
"""

import unittest
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gcode_parser import GCodeParser, Segment
from recipe_generator import RecipeGenerator, SpliceRecipe, generate_recipe


class TestRecipeGenerator(unittest.TestCase):
    """Tests for RecipeGenerator class."""
    
    def setUp(self):
        self.generator = RecipeGenerator()
        self.parser = GCodeParser()
    
    def test_basic_recipe(self):
        """Test generating a basic recipe from segments."""
        lines = [
            "T0",
            "G1 X10 Y10 E50.0 F1200",
            "T1",
            "G1 X20 Y10 E80.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        recipe = self.generator.generate(result)
        
        self.assertEqual(len(recipe.segments), 2)
        self.assertEqual(recipe.segment_count, 2)
        self.assertEqual(recipe.color_count, 2)
    
    def test_segment_merging(self):
        """Test that small segments get merged."""
        # Create generator with 20mm minimum
        gen = RecipeGenerator(min_segment_length_mm=20.0)
        
        lines = [
            "T0",
            "G1 X10 Y10 E50.0 F1200",  # 50mm - keep
            "T1",
            "G1 X20 Y10 E55.0 F1200",  # 5mm - too small, merge
            "T0",
            "G1 X30 Y10 E105.0 F1200", # 50mm - keep
        ]
        result = self.parser.parse_lines(lines)
        recipe = gen.generate(result)
        
        # Small segment should be merged
        self.assertLess(len(recipe.segments), 3)
    
    def test_transition_length(self):
        """Test adding transition length for purging."""
        gen = RecipeGenerator(transition_length_mm=10.0)
        
        lines = [
            "T0",
            "G1 X10 Y10 E50.0 F1200",
            "T1",
            "G1 X20 Y10 E80.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        recipe = gen.generate(result)
        
        # First segment should have transition added
        self.assertEqual(recipe.segments[0]["length_mm"], 60.0)  # 50 + 10
        # Last segment should NOT have transition
        self.assertEqual(recipe.segments[1]["length_mm"], 30.0)  # unchanged
    
    def test_color_names(self):
        """Test custom color names."""
        gen = RecipeGenerator(color_names={0: "white", 1: "black"})
        
        lines = [
            "T0",
            "G1 X10 Y10 E50.0 F1200",
            "T1",
            "G1 X20 Y10 E80.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        recipe = gen.generate(result)
        
        self.assertEqual(recipe.colors["0"], "white")
        self.assertEqual(recipe.colors["1"], "black")
    
    def test_json_output(self):
        """Test JSON serialization."""
        lines = [
            "T0",
            "G1 X10 Y10 E50.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        recipe = self.generator.generate(result)
        
        json_str = self.generator.to_json(recipe)
        
        self.assertIn('"version"', json_str)
        self.assertIn('"segments"', json_str)
        self.assertIn('"total_length_mm"', json_str)
    
    def test_empty_result(self):
        """Test handling empty parse result."""
        lines = []
        result = self.parser.parse_lines(lines)
        recipe = self.generator.generate(result)
        
        self.assertEqual(len(recipe.segments), 0)
        self.assertEqual(recipe.total_length_mm, 0)
    
    def test_metadata(self):
        """Test metadata generation."""
        gen = RecipeGenerator(transition_length_mm=5.0)
        
        lines = [
            "T0",
            "G1 X10 Y10 E50.0 F1200",
            "T1",
            "G1 X20 Y10 E80.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        recipe = gen.generate(result, source_file="test.gcode")
        
        self.assertEqual(recipe.metadata["source_file"], "test.gcode")
        self.assertEqual(recipe.metadata["transition_length_mm"], 5.0)


class TestGCodeModifier(unittest.TestCase):
    """Tests for GCodeModifier class."""
    
    def setUp(self):
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from gcode_modifier import GCodeModifier
        self.modifier = GCodeModifier()
    
    def test_removes_tool_changes(self):
        """Test that T commands are removed."""
        lines = [
            "G28\n",
            "T0\n",
            "G1 X10 Y10 E5.0\n",
            "T1\n",
            "G1 X20 Y10 E10.0\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        
        # Check T commands replaced with comments
        modified_str = "".join(modified)
        self.assertIn("SPLICE3D: Removed T0", modified_str)
        self.assertIn("SPLICE3D: Removed T1", modified_str)
        self.assertEqual(stats["tool_changes_removed"], 2)
    
    def test_adds_header(self):
        """Test that header is added."""
        lines = ["G28\n"]
        modified, stats = self.modifier.modify_lines(lines)
        
        modified_str = "".join(modified)
        self.assertIn("Modified by Splice3D", modified_str)
    
    def test_preserves_geometry(self):
        """Test that move commands are preserved."""
        lines = [
            "G1 X10 Y10 E5.0\n",
            "G1 X20 Y20 E10.0\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        
        modified_str = "".join(modified)
        self.assertIn("G1 X10 Y10 E5.0", modified_str)
        self.assertIn("G1 X20 Y20 E10.0", modified_str)


if __name__ == "__main__":
    unittest.main()
