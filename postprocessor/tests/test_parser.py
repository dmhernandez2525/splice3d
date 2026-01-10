"""
Tests for Splice3D G-code Parser
"""

import unittest
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gcode_parser import GCodeParser, parse_gcode, Segment


class TestGCodeParser(unittest.TestCase):
    """Tests for GCodeParser class."""
    
    def setUp(self):
        self.parser = GCodeParser()
    
    def test_simple_extrusion(self):
        """Test parsing simple extrusion moves."""
        lines = [
            "G1 X10 Y10 E1.0 F1200",
            "G1 X20 Y10 E2.0",
            "G1 X20 Y20 E3.0",
        ]
        result = self.parser.parse_lines(lines)
        
        self.assertEqual(len(result.segments), 1)
        self.assertEqual(result.segments[0].length_mm, 3.0)
        self.assertEqual(result.segments[0].color_index, 0)
    
    def test_tool_changes(self):
        """Test detecting tool changes and creating segments."""
        lines = [
            "T0",
            "G1 X10 Y10 E5.0 F1200",
            "T1",
            "G1 X20 Y10 E8.0 F1200",
            "T0",
            "G1 X30 Y10 E10.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        
        self.assertEqual(len(result.segments), 3)
        self.assertEqual(result.segments[0].color_index, 0)
        self.assertEqual(result.segments[0].length_mm, 5.0)
        self.assertEqual(result.segments[1].color_index, 1)
        self.assertEqual(result.segments[1].length_mm, 3.0)
        self.assertEqual(result.segments[2].color_index, 0)
        self.assertEqual(result.segments[2].length_mm, 2.0)
    
    def test_relative_extrusion(self):
        """Test parsing relative extrusion mode (M83)."""
        lines = [
            "M83 ; Relative E",
            "G1 X10 Y10 E1.0 F1200",
            "G1 X20 Y10 E1.0",
            "G1 X20 Y20 E1.0",
        ]
        result = self.parser.parse_lines(lines)
        
        self.assertEqual(len(result.segments), 1)
        self.assertEqual(result.segments[0].length_mm, 3.0)
    
    def test_negative_extrusion_ignored(self):
        """Test that retractions (negative E) are ignored."""
        lines = [
            "G1 X10 Y10 E5.0 F1200",
            "G1 E4.5 F3000 ; Retract",
            "G1 X20 Y10 E5.5 F1200",
        ]
        result = self.parser.parse_lines(lines)
        
        # Should only count positive extrusion
        self.assertEqual(result.segments[0].length_mm, 5.5)
    
    def test_g92_reset(self):
        """Test handling G92 E reset."""
        lines = [
            "G1 X10 Y10 E100.0 F1200",
            "G92 E0 ; Reset E",
            "G1 X20 Y10 E5.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        
        # Total should be 100 + 5 = 105
        self.assertEqual(result.segments[0].length_mm, 105.0)
    
    def test_layer_tracking(self):
        """Test layer detection from comments."""
        lines = [
            "T0",
            ";LAYER:0",
            "G1 X10 Y10 E5.0 F1200",
            ";LAYER:1",
            "G1 X20 Y10 E10.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        
        self.assertEqual(result.layer_count, 2)
    
    def test_color_count(self):
        """Test color counting."""
        lines = [
            "T0",
            "G1 X10 Y10 E5.0 F1200",
            "T1",
            "G1 X20 Y10 E8.0 F1200",
            "T2",
            "G1 X30 Y10 E10.0 F1200",
        ]
        result = self.parser.parse_lines(lines)
        
        self.assertEqual(result.color_count, 3)
    
    def test_empty_input(self):
        """Test handling empty input."""
        result = self.parser.parse_lines([])
        
        self.assertEqual(len(result.segments), 0)
        self.assertEqual(result.total_length_mm, 0.0)
    
    def test_no_extrusion(self):
        """Test G-code with no extrusion."""
        lines = [
            "G1 X10 Y10 F1200",
            "G1 X20 Y10",
            "G1 X20 Y20",
        ]
        result = self.parser.parse_lines(lines)
        
        self.assertEqual(len(result.segments), 0)
        self.assertIn("No extrusion", result.warnings[0])


class TestParseGcodeFunction(unittest.TestCase):
    """Tests for the convenience parse_gcode function."""
    
    def test_parse_sample_file(self):
        """Test parsing the sample multi-color G-code file."""
        sample_path = Path(__file__).parent.parent.parent / "samples" / "test_multicolor.gcode"
        
        if not sample_path.exists():
            self.skipTest("Sample file not found")
        
        result = parse_gcode(str(sample_path))
        
        # Should have multiple segments (T0, T1, T0 at minimum)
        self.assertGreater(len(result.segments), 1)
        
        # Should have 2 colors
        self.assertEqual(result.color_count, 2)
        
        # Should have found tool changes
        colors_used = set(s.color_index for s in result.segments)
        self.assertIn(0, colors_used)
        self.assertIn(1, colors_used)


if __name__ == "__main__":
    unittest.main()
