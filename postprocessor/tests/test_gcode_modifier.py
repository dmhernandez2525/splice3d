"""
Tests for the gcode modifier module.
"""

import unittest
import tempfile
import os
from postprocessor.gcode_modifier import GCodeModifier, modify_gcode


class TestGCodeModifier(unittest.TestCase):
    """Tests for the GCodeModifier class."""

    def setUp(self):
        self.modifier = GCodeModifier()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_initialization(self):
        """Test default initialization values."""
        modifier = GCodeModifier()
        self.assertTrue(modifier.add_pause_at_start)
        self.assertEqual(modifier.pause_command, "M0")

    def test_custom_initialization(self):
        """Test custom initialization values."""
        modifier = GCodeModifier(add_pause_at_start=False, pause_command="M600")
        self.assertFalse(modifier.add_pause_at_start)
        self.assertEqual(modifier.pause_command, "M600")

    def test_generate_header(self):
        """Test header generation."""
        header = self.modifier._generate_header()
        self.assertIsInstance(header, list)
        self.assertTrue(any("Splice3D" in line for line in header))
        self.assertTrue(any("Tool change" in line for line in header))

    def test_remove_tool_changes(self):
        """Test that tool change commands are removed."""
        lines = [
            "G28 ; Home\n",
            "T0 ; Select tool 0\n",
            "G1 X10 Y10\n",
            "T1 ; Select tool 1\n",
            "G1 X20 Y20\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)

        # Tool changes should be commented out
        self.assertEqual(stats["tool_changes_removed"], 2)
        modified_text = "".join(modified)
        self.assertIn("; SPLICE3D: Removed T0", modified_text)
        self.assertIn("; SPLICE3D: Removed T1", modified_text)

    def test_preserves_geometry_commands(self):
        """Test that G0/G1 commands are preserved."""
        lines = [
            "G28 ; Home\n",
            "G1 X10 Y10 E1.0\n",
            "G0 X20 Y20\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        modified_text = "".join(modified)

        self.assertIn("G28 ; Home", modified_text)
        self.assertIn("G1 X10 Y10 E1.0", modified_text)
        self.assertIn("G0 X20 Y20", modified_text)

    def test_adds_header(self):
        """Test that header is added to output."""
        lines = ["G28 ; Home\n"]
        modified, stats = self.modifier.modify_lines(lines)
        modified_text = "".join(modified)

        self.assertIn("Modified by Splice3D Post-Processor", modified_text)

    def test_adds_pause_after_start_gcode(self):
        """Test that pause is added after start G-code."""
        lines = [
            "; START_GCODE begins\n",
            "G28 ; Home\n",
            "; END_GCODE\n",
            "G1 X10 Y10 E1.0\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        modified_text = "".join(modified)

        self.assertIn("M0 ; Pause for spool loading", modified_text)
        self.assertIn("Load pre-spliced spool now", modified_text)

    def test_no_pause_when_disabled(self):
        """Test that pause is not added when disabled."""
        modifier = GCodeModifier(add_pause_at_start=False)
        lines = [
            "; START_GCODE begins\n",
            "G28 ; Home\n",
            "; END_GCODE\n",
            "G1 X10 Y10 E1.0\n",
        ]
        modified, stats = modifier.modify_lines(lines)
        modified_text = "".join(modified)

        self.assertNotIn("Pause for spool loading", modified_text)

    def test_custom_pause_command(self):
        """Test custom pause command."""
        modifier = GCodeModifier(pause_command="M600")
        lines = [
            "; START_GCODE begins\n",
            "; END_GCODE\n",
            "G0 X10 Y10\n",
        ]
        modified, stats = modifier.modify_lines(lines)
        modified_text = "".join(modified)

        self.assertIn("M600 ; Pause for spool loading", modified_text)

    def test_tool_change_case_insensitive(self):
        """Test that tool change detection is case insensitive."""
        lines = [
            "t0\n",
            "T1\n",
            "t2\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        self.assertEqual(stats["tool_changes_removed"], 3)

    def test_stats_tracking(self):
        """Test that statistics are tracked correctly."""
        lines = [
            "G28\n",
            "T0\n",
            "G1 X10\n",
            "T1\n",
            "G1 X20\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)

        self.assertEqual(stats["total_lines"], 5)
        self.assertEqual(stats["tool_changes_removed"], 2)
        self.assertEqual(stats["lines_modified"], 2)


class TestModifyFile(unittest.TestCase):
    """Tests for the modify_file method."""

    def setUp(self):
        self.modifier = GCodeModifier()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_modify_file_creates_output(self):
        """Test that modify_file creates an output file."""
        input_path = os.path.join(self.temp_dir, "input.gcode")
        output_path = os.path.join(self.temp_dir, "output.gcode")

        with open(input_path, 'w') as f:
            f.write("G28 ; Home\n")
            f.write("T0\n")
            f.write("G1 X10 Y10\n")

        stats = self.modifier.modify_file(input_path, output_path)

        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(stats["tool_changes_removed"], 1)

    def test_modify_file_content(self):
        """Test that modify_file produces correct content."""
        input_path = os.path.join(self.temp_dir, "input.gcode")
        output_path = os.path.join(self.temp_dir, "output.gcode")

        with open(input_path, 'w') as f:
            f.write("G28 ; Home\n")
            f.write("T0 ; Tool change\n")

        self.modifier.modify_file(input_path, output_path)

        with open(output_path, 'r') as f:
            content = f.read()

        self.assertIn("Splice3D", content)
        self.assertIn("; SPLICE3D: Removed T0", content)

    def test_modify_file_handles_encoding(self):
        """Test that modify_file handles various encodings."""
        input_path = os.path.join(self.temp_dir, "input.gcode")
        output_path = os.path.join(self.temp_dir, "output.gcode")

        # Write with some unicode characters
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write("; Comment with unicode: °C\n")
            f.write("G28\n")

        stats = self.modifier.modify_file(input_path, output_path)
        self.assertTrue(os.path.exists(output_path))


class TestModifyGcodeFunction(unittest.TestCase):
    """Tests for the modify_gcode convenience function."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_modify_gcode_convenience(self):
        """Test the modify_gcode convenience function."""
        input_path = os.path.join(self.temp_dir, "input.gcode")
        output_path = os.path.join(self.temp_dir, "output.gcode")

        with open(input_path, 'w') as f:
            f.write("G28\n")
            f.write("T0\n")
            f.write("T1\n")

        stats = modify_gcode(input_path, output_path)

        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(stats["tool_changes_removed"], 2)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases in G-code modification."""

    def setUp(self):
        self.modifier = GCodeModifier()

    def test_empty_input(self):
        """Test handling of empty input."""
        modified, stats = self.modifier.modify_lines([])
        # Should still have header
        self.assertTrue(len(modified) > 0)
        self.assertEqual(stats["total_lines"], 0)

    def test_only_comments(self):
        """Test file with only comments."""
        lines = [
            "; Comment 1\n",
            "; Comment 2\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        self.assertEqual(stats["tool_changes_removed"], 0)

    def test_tool_with_digits(self):
        """Test that multi-digit tool numbers are handled."""
        lines = [
            "T0\n",
            "T10\n",
            "T123\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        self.assertEqual(stats["tool_changes_removed"], 3)

    def test_t_not_at_line_start(self):
        """Test that T in middle of line is not removed."""
        lines = [
            "G1 X10 ; This is T shaped\n",
            "; Temperature: 200\n",
        ]
        modified, stats = self.modifier.modify_lines(lines)
        self.assertEqual(stats["tool_changes_removed"], 0)
        modified_text = "".join(modified)
        self.assertIn("This is T shaped", modified_text)


if __name__ == "__main__":
    unittest.main()
