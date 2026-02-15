"""Tests for F1.1 mechanical design validation assets."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from postprocessor.mechanical_validation import (
    calculate_deflection_angles,
    load_mechanical_layout,
    validate_interfaces,
    validate_layout,
    validate_printable_bed_fit,
    validate_station_layout,
)


class TestMechanicalValidation(unittest.TestCase):
    """Validate Phase 1.1 mechanical CAD constraints."""

    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        cls.repo_root = repo_root
        cls.layout_path = repo_root / "hardware" / "f1_1" / "spec" / "mechanical_layout.json"
        cls.layout = load_mechanical_layout(cls.layout_path)

    def test_filament_path_deflection_under_limit(self) -> None:
        angles = calculate_deflection_angles(self.layout.path.waypoints)
        self.assertTrue(angles)
        max_angle = max(angles)
        self.assertLessEqual(max_angle, self.layout.path.max_deflection_deg)

    def test_printable_parts_fit_standard_bed(self) -> None:
        violations = validate_printable_bed_fit(self.layout)
        self.assertEqual(violations, [])

    def test_station_layout_has_no_collisions(self) -> None:
        collisions = validate_station_layout(self.layout)
        self.assertEqual(collisions, [])

    def test_station_interfaces_match_mount_patterns(self) -> None:
        violations = validate_interfaces(self.layout)
        self.assertEqual(violations, [])

    def test_scad_sources_exist(self) -> None:
        for part in self.layout.printable_parts:
            source_path = self.repo_root / part.source_scad
            self.assertTrue(source_path.exists(), f"Missing CAD source {source_path}")

    def test_full_layout_validation_passes(self) -> None:
        report = validate_layout(self.layout)
        self.assertTrue(report.valid)


if __name__ == "__main__":
    unittest.main()
