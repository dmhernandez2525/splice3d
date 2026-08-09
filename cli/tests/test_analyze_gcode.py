"""Tests for the Splice3D G-code analysis tool."""

import os
import tempfile
import unittest

from cli.analyze_gcode import analyze_gcode, SegmentStats


class TestAnalyzeGcode(unittest.TestCase):
    """Tests for the analyze_gcode function."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_gcode(self, name, content):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_two_color_analysis(self):
        path = self._write_gcode("two_color.gcode", (
            "T0\n"
            "G1 X10 E50.0 F1200\n"
            "T1\n"
            "G1 X20 E100.0\n"
        ))
        result = analyze_gcode(path)
        self.assertEqual(result.color_count, 2)
        self.assertEqual(result.segment_stats.count, 2)
        self.assertGreater(result.segment_stats.total_mm, 0)
        self.assertIn("T0", result.color_distribution)
        self.assertIn("T1", result.color_distribution)

    def test_empty_gcode(self):
        path = self._write_gcode("empty.gcode", "G28\nG1 X10 Y10 F1200\n")
        result = analyze_gcode(path)
        self.assertEqual(result.segment_stats.count, 0)
        self.assertIn("No segments found", result.warnings)

    def test_segment_distribution_buckets(self):
        # Create gcode with segments of known lengths
        lines = ["T0\n", "G1 X10 E2.0\n"]  # 2mm = very_short
        lines += ["T1\n", "G1 X20 E15.0\n"]  # 13mm = short
        lines += ["T0\n", "G1 X30 E65.0\n"]  # 50mm = medium
        lines += ["T1\n", "G1 X40 E365.0\n"]  # 300mm = long
        lines += ["T0\n", "G1 X50 E1365.0\n"]  # 1000mm = very_long
        path = self._write_gcode("buckets.gcode", "".join(lines))
        result = analyze_gcode(path)
        stats = result.segment_stats
        self.assertEqual(stats.very_short, 1)
        self.assertEqual(stats.short, 1)
        self.assertEqual(stats.medium, 1)
        self.assertEqual(stats.long, 1)
        self.assertEqual(stats.very_long, 1)

    def test_splice_time_estimate(self):
        lines = []
        for i in range(10):
            lines.append(f"T{i % 2}\n")
            lines.append(f"G1 X{i*10} E{(i+1)*50}.0\n")
        path = self._write_gcode("timed.gcode", "".join(lines))
        result = analyze_gcode(path)
        # 10 segments * 45 seconds / 3600 = 0.125 hours
        self.assertGreater(result.estimated_splice_time_hours, 0)

    def test_waste_reduction_estimate(self):
        lines = ["T0\n", "G1 X10 E100.0\n", "T1\n", "G1 X20 E200.0\n"]
        path = self._write_gcode("waste.gcode", "".join(lines))
        result = analyze_gcode(path)
        self.assertEqual(result.estimated_waste_reduction_percent, 80.0)

    def test_high_short_segment_warning(self):
        # Create many very short segments (>20% threshold)
        lines = []
        for i in range(10):
            lines.append(f"T{i % 2}\n")
            lines.append(f"G1 X{i} E{(i+1)*2}.0\n")  # 2mm segments
        path = self._write_gcode("shorts.gcode", "".join(lines))
        result = analyze_gcode(path)
        short_warnings = [w for w in result.warnings if "very short" in w]
        self.assertGreater(len(short_warnings), 0)

    def test_min_max_avg_median(self):
        lines = [
            "T0\n", "G1 X10 E50.0\n",
            "T1\n", "G1 X20 E250.0\n",
        ]
        path = self._write_gcode("stats.gcode", "".join(lines))
        result = analyze_gcode(path)
        self.assertEqual(result.segment_stats.min_mm, 50.0)
        self.assertEqual(result.segment_stats.max_mm, 200.0)

    def test_nonexistent_file(self):
        result = analyze_gcode("/nonexistent/file.gcode")
        # Should handle gracefully (parser returns errors)
        self.assertEqual(result.segment_stats.count, 0)


class TestSegmentStats(unittest.TestCase):
    """Tests for SegmentStats dataclass."""

    def test_defaults(self):
        stats = SegmentStats()
        self.assertEqual(stats.count, 0)
        self.assertEqual(stats.total_mm, 0.0)
        self.assertEqual(stats.very_short, 0)


if __name__ == "__main__":
    unittest.main()
