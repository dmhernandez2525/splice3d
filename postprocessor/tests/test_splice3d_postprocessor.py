"""
Tests for Splice3D Post-Processor CLI entry point.

Tests the main() function and argument parsing from splice3d_postprocessor.py.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gcode_parser import GCodeParser
from recipe_generator import RecipeGenerator
from gcode_modifier import GCodeModifier
from postprocessor.splice3d_postprocessor import main as splice3d_main


class TestSplice3DPostprocessorCLI(unittest.TestCase):
    """Tests for the CLI post-processor pipeline (mirrors splice3d_postprocessor.main)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sample_gcode = [
            "; START_GCODE\n",
            "G28\n",
            "T0\n",
            "G1 X10 Y10 E50.0 F1200\n",
            "G1 X20 Y20 E100.0\n",
            "T1\n",
            "G1 X30 Y30 E150.0\n",
            "G1 X40 Y40 E200.0\n",
            "M104 S0\n",
        ]
        self.input_path = os.path.join(self.tmpdir, "test_input.gcode")
        with open(self.input_path, "w") as f:
            f.writelines(self.sample_gcode)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_pipeline_parse_generate_modify(self):
        """Test the full pipeline: parse -> generate recipe -> modify gcode."""
        input_path = Path(self.input_path)
        output_dir = Path(self.tmpdir)
        base_name = input_path.stem
        recipe_path = output_dir / f"{base_name}_splice_recipe.json"
        modified_gcode_path = output_dir / f"{base_name}_modified.gcode"

        # Step 1: Parse
        parser = GCodeParser()
        parse_result = parser.parse_file(str(input_path))
        self.assertFalse(parse_result.errors)
        self.assertGreater(len(parse_result.segments), 0)
        self.assertEqual(parse_result.color_count, 2)

        # Step 2: Generate recipe
        recipe_gen = RecipeGenerator(
            transition_length_mm=0.0,
            min_segment_length_mm=10.0
        )
        recipe = recipe_gen.generate(parse_result, source_file=str(input_path))
        recipe_gen.save_recipe(recipe, str(recipe_path))
        self.assertTrue(recipe_path.exists())
        self.assertGreater(recipe.segment_count, 0)
        self.assertGreater(recipe.total_length_mm, 0)

        # Step 3: Modify gcode
        modifier = GCodeModifier(add_pause_at_start=True)
        stats = modifier.modify_file(str(input_path), str(modified_gcode_path))
        self.assertTrue(modified_gcode_path.exists())
        self.assertGreater(stats["tool_changes_removed"], 0)

    def test_pipeline_with_no_pause(self):
        """Test pipeline with --no-pause equivalent."""
        input_path = Path(self.input_path)
        modified_path = os.path.join(self.tmpdir, "no_pause.gcode")

        modifier = GCodeModifier(add_pause_at_start=False)
        stats = modifier.modify_file(str(input_path), modified_path)

        with open(modified_path) as f:
            content = f.read()
        self.assertNotIn("M0", content)
        self.assertGreater(stats["tool_changes_removed"], 0)

    def test_pipeline_with_transition_length(self):
        """Test pipeline with transition lengths added."""
        parser = GCodeParser()
        parse_result = parser.parse_lines(self.sample_gcode)

        recipe_gen = RecipeGenerator(transition_length_mm=20.0)
        recipe = recipe_gen.generate(parse_result)

        # With transitions, total should be greater than raw extrusion
        raw_total = sum(s.length_mm for s in parse_result.segments)
        self.assertGreater(recipe.total_length_mm, raw_total)

    def test_pipeline_with_custom_colors(self):
        """Test pipeline with --colors equivalent."""
        parser = GCodeParser()
        parse_result = parser.parse_lines(self.sample_gcode)

        color_names = {0: "crimson", 1: "navy"}
        recipe_gen = RecipeGenerator(color_names=color_names)
        recipe = recipe_gen.generate(parse_result)

        self.assertIn("crimson", recipe.colors.values())
        self.assertIn("navy", recipe.colors.values())

    def test_pipeline_with_min_segment_merge(self):
        """Test pipeline with minimum segment length merging."""
        gcode = [
            "T0\n",
            "G1 X10 Y10 E5.0 F1200\n",  # short segment
            "T1\n",
            "G1 X20 Y20 E105.0\n",  # long segment
        ]
        parser = GCodeParser()
        parse_result = parser.parse_lines(gcode)

        # With high min segment, small segments get merged
        recipe_gen = RecipeGenerator(min_segment_length_mm=10.0)
        recipe = recipe_gen.generate(parse_result)
        self.assertGreater(recipe.total_length_mm, 0)

    def test_pipeline_with_output_dir(self):
        """Test specifying an output directory."""
        sub_dir = os.path.join(self.tmpdir, "subdir", "nested")
        os.makedirs(sub_dir, exist_ok=True)

        input_path = Path(self.input_path)
        recipe_path = Path(sub_dir) / f"{input_path.stem}_splice_recipe.json"

        parser = GCodeParser()
        parse_result = parser.parse_file(str(input_path))
        recipe_gen = RecipeGenerator()
        recipe = recipe_gen.generate(parse_result)
        recipe_gen.save_recipe(recipe, str(recipe_path))

        self.assertTrue(recipe_path.exists())

    def test_pipeline_with_verbose_output(self):
        """Test verbose output path (segments listed)."""
        parser = GCodeParser()
        parse_result = parser.parse_lines(self.sample_gcode)

        # Verify segments have layer info for verbose display
        for seg in parse_result.segments:
            self.assertIsNotNone(seg.start_line)
            self.assertIsNotNone(seg.end_line)
            self.assertIsNotNone(seg.color_index)

    def test_pipeline_empty_gcode(self):
        """Test pipeline with empty gcode (no extrusion)."""
        empty_gcode = [
            "G28\n",
            "G1 X10 Y10 F1200\n",
            "M104 S0\n",
        ]
        parser = GCodeParser()
        parse_result = parser.parse_lines(empty_gcode)

        self.assertEqual(len(parse_result.segments), 0)
        self.assertGreater(len(parse_result.warnings), 0)

    def test_pipeline_single_color_warning(self):
        """Test pipeline warns when only single color detected."""
        single_color = [
            "G1 X10 Y10 E50.0 F1200\n",
            "G1 X20 Y20 E100.0\n",
        ]
        parser = GCodeParser()
        parse_result = parser.parse_lines(single_color)

        warnings = [w for w in parse_result.warnings if "Single color" in w]
        self.assertGreater(len(warnings), 0)

    def test_pipeline_parse_errors_on_bad_file(self):
        """Test pipeline handles file read errors."""
        parser = GCodeParser()
        parse_result = parser.parse_file("/nonexistent/path/test.gcode")
        self.assertGreater(len(parse_result.errors), 0)

    def test_output_path_construction(self):
        """Test that output paths are constructed correctly."""
        input_path = Path(self.input_path)
        output_dir = input_path.parent
        base_name = input_path.stem

        recipe_path = output_dir / f"{base_name}_splice_recipe.json"
        modified_gcode_path = output_dir / f"{base_name}_modified.gcode"

        self.assertEqual(recipe_path.suffix, ".json")
        self.assertEqual(modified_gcode_path.suffix, ".gcode")
        self.assertIn("splice_recipe", recipe_path.name)
        self.assertIn("modified", modified_gcode_path.name)


class TestRecipeGeneratorEdgeCases(unittest.TestCase):
    """Additional edge case tests for RecipeGenerator."""

    def test_generate_with_empty_segments(self):
        """Test recipe generation with no segments."""
        from gcode_parser import ParseResult
        parse_result = ParseResult(segments=[], total_length_mm=0.0, color_count=0)
        gen = RecipeGenerator()
        recipe = gen.generate(parse_result)
        self.assertEqual(recipe.segment_count, 0)
        self.assertEqual(recipe.total_length_mm, 0.0)

    def test_generate_with_zero_min_segment(self):
        """Test with min_segment_length_mm=0 (no merging)."""
        from gcode_parser import ParseResult, Segment
        segments = [
            Segment(color_index=0, length_mm=1.0, start_line=1, end_line=2),
            Segment(color_index=1, length_mm=2.0, start_line=3, end_line=4),
        ]
        parse_result = ParseResult(segments=segments, total_length_mm=3.0, color_count=2)
        gen = RecipeGenerator(min_segment_length_mm=0)
        recipe = gen.generate(parse_result)
        self.assertEqual(recipe.segment_count, 2)

    def test_to_json_compact(self):
        """Test compact JSON serialization."""
        from gcode_parser import ParseResult
        parse_result = ParseResult(segments=[], total_length_mm=0.0)
        gen = RecipeGenerator()
        recipe = gen.generate(parse_result)
        json_str = gen.to_json(recipe, pretty=False)
        self.assertNotIn("\n", json_str)

    def test_to_json_pretty(self):
        """Test pretty JSON serialization."""
        from gcode_parser import ParseResult
        parse_result = ParseResult(segments=[], total_length_mm=0.0)
        gen = RecipeGenerator()
        recipe = gen.generate(parse_result)
        json_str = gen.to_json(recipe, pretty=True)
        self.assertIn("\n", json_str)

    def test_merge_consecutive_same_color(self):
        """Test that consecutive same-color segments are merged."""
        from gcode_parser import ParseResult, Segment
        segments = [
            Segment(color_index=0, length_mm=50.0, start_line=1, end_line=10),
            Segment(color_index=0, length_mm=50.0, start_line=11, end_line=20),
            Segment(color_index=1, length_mm=100.0, start_line=21, end_line=40),
        ]
        parse_result = ParseResult(segments=segments, total_length_mm=200.0, color_count=2)
        gen = RecipeGenerator()
        recipe = gen.generate(parse_result)
        # First two should merge since same color
        self.assertEqual(recipe.segment_count, 2)

    def test_merge_small_segment_into_previous(self):
        """Test that small segments below threshold are merged."""
        from gcode_parser import ParseResult, Segment
        segments = [
            Segment(color_index=0, length_mm=100.0, start_line=1, end_line=10),
            Segment(color_index=1, length_mm=5.0, start_line=11, end_line=12),  # too small
            Segment(color_index=0, length_mm=100.0, start_line=13, end_line=20),
        ]
        parse_result = ParseResult(segments=segments, total_length_mm=205.0, color_count=2)
        gen = RecipeGenerator(min_segment_length_mm=10.0)
        recipe = gen.generate(parse_result)
        # The 5mm segment should be merged
        total = sum(s["length_mm"] for s in recipe.segments)
        self.assertAlmostEqual(total, 205.0, places=1)

    def test_default_color_names_for_unknown_tools(self):
        """Test fallback color names for tool indices beyond defaults."""
        from gcode_parser import ParseResult, Segment
        segments = [
            Segment(color_index=10, length_mm=100.0, start_line=1, end_line=10),
        ]
        parse_result = ParseResult(segments=segments, total_length_mm=100.0, color_count=1)
        gen = RecipeGenerator()
        recipe = gen.generate(parse_result)
        self.assertIn("color_10", recipe.colors.values())

    def test_transition_length_not_added_to_last_segment(self):
        """Test that transition length is only added to non-last segments."""
        from gcode_parser import ParseResult, Segment
        segments = [
            Segment(color_index=0, length_mm=100.0, start_line=1, end_line=10),
            Segment(color_index=1, length_mm=100.0, start_line=11, end_line=20),
        ]
        parse_result = ParseResult(segments=segments, total_length_mm=200.0, color_count=2)
        gen = RecipeGenerator(transition_length_mm=25.0)
        recipe = gen.generate(parse_result)
        # Only first segment gets transition
        self.assertEqual(recipe.segments[0]["length_mm"], 125.0)
        self.assertEqual(recipe.segments[1]["length_mm"], 100.0)


class TestGCodeParserEdgeCases(unittest.TestCase):
    """Additional edge case tests for GCodeParser."""

    def setUp(self):
        self.parser = GCodeParser()

    def test_relative_extrusion_mode(self):
        """Test M83 relative extrusion mode."""
        lines = [
            "M83",
            "G1 X10 E1.0",
            "G1 X20 E2.0",
            "G1 X30 E0.5",
        ]
        result = self.parser.parse_lines(lines)
        self.assertEqual(len(result.segments), 1)
        self.assertAlmostEqual(result.segments[0].length_mm, 3.5)

    def test_absolute_extrusion_mode(self):
        """Test M82 absolute extrusion mode."""
        lines = [
            "M82",
            "G1 X10 E1.0",
            "G1 X20 E3.0",
        ]
        result = self.parser.parse_lines(lines)
        self.assertEqual(len(result.segments), 1)
        self.assertAlmostEqual(result.segments[0].length_mm, 3.0)

    def test_g92_e_reset(self):
        """Test G92 E0 reset handling."""
        lines = [
            "T0",
            "G1 X10 E50.0",
            "G92 E0",
            "G1 X20 E50.0",
        ]
        result = self.parser.parse_lines(lines)
        total = sum(s.length_mm for s in result.segments)
        self.assertAlmostEqual(total, 100.0)

    def test_m600_color_change(self):
        """Test M600 color change command creates separate segments."""
        lines = [
            "G1 X10 E50.0",
            "M600",
            "G1 X20 E100.0",
        ]
        result = self.parser.parse_lines(lines)
        # M600 toggles tool and adds to seen_tools, but tool 0 was never
        # explicitly added via T command, so color_count depends on seen_tools
        self.assertEqual(len(result.segments), 2)
        self.assertAlmostEqual(result.segments[0].length_mm, 50.0)
        self.assertAlmostEqual(result.segments[1].length_mm, 50.0)

    def test_layer_detection_numbered(self):
        """Test numbered layer detection (;LAYER:N)."""
        lines = [
            ";LAYER:0",
            "G1 X10 E10.0",
            ";LAYER:1",
            "G1 X20 E20.0",
            ";LAYER:2",
            "G1 X30 E30.0",
        ]
        result = self.parser.parse_lines(lines)
        self.assertEqual(result.layer_count, 3)

    def test_layer_detection_change_comment(self):
        """Test LAYER_CHANGE style detection."""
        lines = [
            ";LAYER_CHANGE",
            "G1 X10 E10.0",
            ";LAYER_CHANGE",
            "G1 X20 E20.0",
        ]
        result = self.parser.parse_lines(lines)
        self.assertEqual(result.layer_count, 3)  # 0-indexed + 2 changes + 1

    def test_negative_extrusion_ignored_relative(self):
        """Test that retraction (negative E) is not counted in relative mode."""
        lines = [
            "M83",
            "G1 X10 E5.0",
            "G1 E-2.0",  # retraction
            "G1 X20 E5.0",
        ]
        result = self.parser.parse_lines(lines)
        self.assertAlmostEqual(result.segments[0].length_mm, 10.0)

    def test_empty_lines_and_comments_skipped(self):
        """Test empty lines and pure comments are skipped."""
        lines = [
            "",
            "; This is a comment",
            "",
            "G1 X10 E10.0",
            "; Another comment",
        ]
        result = self.parser.parse_lines(lines)
        self.assertEqual(len(result.segments), 1)

    def test_case_insensitive_commands(self):
        """Test case insensitivity of G-code commands."""
        lines = [
            "t0",
            "g1 X10 e50.0",
            "t1",
            "g1 X20 e100.0",
        ]
        result = self.parser.parse_lines(lines)
        self.assertEqual(result.color_count, 2)


class TestGCodeModifierEdgeCases(unittest.TestCase):
    """Additional edge case tests for GCodeModifier."""

    def test_pause_command_customization(self):
        """Test custom pause command (M600 instead of M0)."""
        lines = [
            "; START_GCODE\n",
            "G1 X10 Y10 E1.0\n",
        ]
        modifier = GCodeModifier(add_pause_at_start=True, pause_command="M600")
        modified, stats = modifier.modify_lines(lines)
        content = "".join(modified)
        self.assertIn("M600", content)
        self.assertNotIn("M0 ", content)

    def test_no_tool_changes_stats(self):
        """Test stats when no tool changes exist."""
        lines = [
            "G1 X10 E1.0\n",
            "G1 X20 E2.0\n",
        ]
        modifier = GCodeModifier()
        modified, stats = modifier.modify_lines(lines)
        self.assertEqual(stats["tool_changes_removed"], 0)

    def test_header_always_present(self):
        """Test that Splice3D header is always added."""
        lines = ["G1 X10 E1.0\n"]
        modifier = GCodeModifier(add_pause_at_start=False)
        modified, stats = modifier.modify_lines(lines)
        content = "".join(modified)
        self.assertIn("Splice3D Post-Processor", content)

    def test_tool_change_replaced_with_comment(self):
        """Test that tool changes become comments."""
        lines = [
            "T0\n",
            "G1 X10 E1.0\n",
            "T1\n",
            "G1 X20 E2.0\n",
        ]
        modifier = GCodeModifier(add_pause_at_start=False)
        modified, stats = modifier.modify_lines(lines)
        content = "".join(modified)
        self.assertIn("; SPLICE3D: Removed T0", content)
        self.assertIn("; SPLICE3D: Removed T1", content)
        self.assertEqual(stats["tool_changes_removed"], 2)

    def test_total_lines_stat(self):
        """Test total_lines stat is accurate."""
        lines = ["line1\n", "line2\n", "line3\n"]
        modifier = GCodeModifier(add_pause_at_start=False)
        _, stats = modifier.modify_lines(lines)
        self.assertEqual(stats["total_lines"], 3)


class TestRecipeValidatorEdgeCases(unittest.TestCase):
    """Additional edge case tests for RecipeValidator."""

    def test_validate_file_not_found(self):
        """Test validation with nonexistent file."""
        from recipe_validator import RecipeValidator
        validator = RecipeValidator()
        result = validator.validate_file("/nonexistent/recipe.json")
        self.assertFalse(result.valid)

    def test_validate_invalid_json(self):
        """Test validation with malformed JSON."""
        from recipe_validator import RecipeValidator
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ not valid json")
            f.flush()
            validator = RecipeValidator()
            result = validator.validate_file(f.name)
            self.assertFalse(result.valid)
        os.unlink(f.name)

    def test_validate_valid_recipe(self):
        """Test validation with a properly structured recipe."""
        import json
        from recipe_validator import RecipeValidator
        recipe = {
            "version": "1.0",
            "total_length_mm": 200.0,
            "segment_count": 2,
            "color_count": 2,
            "segments": [
                {"color": 0, "length_mm": 100.0},
                {"color": 1, "length_mm": 100.0},
            ],
            "colors": {"0": "white", "1": "black"},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(recipe, f)
            f.flush()
            validator = RecipeValidator()
            result = validator.validate_file(f.name)
            self.assertTrue(result.valid)
        os.unlink(f.name)


class TestSplice3DMainFunction(unittest.TestCase):
    """Tests that exercise the actual main() entry point."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.input_path = os.path.join(self.tmpdir, "test_main.gcode")
        with open(self.input_path, "w") as f:
            f.write("; START_GCODE\n")
            f.write("G28\n")
            f.write("T0\n")
            f.write("G1 X10 Y10 E50.0 F1200\n")
            f.write("T1\n")
            f.write("G1 X20 Y20 E100.0\n")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_main_success(self):
        """Test main() with valid arguments produces recipe and modified gcode."""
        with patch("sys.argv", ["splice3d", self.input_path, "-o", self.tmpdir]):
            result = splice3d_main()
        self.assertEqual(result, 0)
        # Verify output files created
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "test_main_splice_recipe.json")))
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "test_main_modified.gcode")))

    def test_main_with_verbose(self):
        """Test main() with --verbose flag."""
        with patch("sys.argv", ["splice3d", self.input_path, "-o", self.tmpdir, "-v"]):
            result = splice3d_main()
        self.assertEqual(result, 0)

    def test_main_with_colors(self):
        """Test main() with --colors flag."""
        with patch("sys.argv", ["splice3d", self.input_path, "-o", self.tmpdir, "--colors", "red", "blue"]):
            result = splice3d_main()
        self.assertEqual(result, 0)

    def test_main_with_transition(self):
        """Test main() with --transition flag."""
        with patch("sys.argv", ["splice3d", self.input_path, "-o", self.tmpdir, "-t", "15.0"]):
            result = splice3d_main()
        self.assertEqual(result, 0)

    def test_main_with_no_pause(self):
        """Test main() with --no-pause flag."""
        with patch("sys.argv", ["splice3d", self.input_path, "-o", self.tmpdir, "--no-pause"]):
            result = splice3d_main()
        self.assertEqual(result, 0)

    def test_main_file_not_found(self):
        """Test main() with nonexistent input file."""
        with patch("sys.argv", ["splice3d", "/nonexistent/file.gcode"]):
            with self.assertRaises(SystemExit) as ctx:
                splice3d_main()
            self.assertEqual(ctx.exception.code, 1)

    def test_main_many_segments_verbose(self):
        """Test main() verbose output with >20 segments (truncation path)."""
        # Create gcode with many segments
        input_path = os.path.join(self.tmpdir, "many_segments.gcode")
        with open(input_path, "w") as f:
            f.write("; START_GCODE\n")
            e = 0
            for i in range(25):
                f.write(f"T{i % 2}\n")
                e += 50
                f.write(f"G1 X{i*10} Y10 E{e:.1f}\n")
        with patch("sys.argv", ["splice3d", input_path, "-o", self.tmpdir, "-v"]):
            result = splice3d_main()
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
