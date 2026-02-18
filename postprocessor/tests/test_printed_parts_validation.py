"""Tests for F1.4 printed-parts validation logic."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from postprocessor.printed_parts_validation import (
    load_printed_parts_spec,
    validate_artifacts,
    validate_bed_fit,
    validate_printed_parts_spec,
    validate_snap_fit,
    validate_spool_holder_support,
    validate_support_requirements,
)


class TestPrintedPartsValidation(unittest.TestCase):
    """Validation tests for the F1.4 printed parts package."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.spec_path = cls.repo_root / "hardware" / "f1_4" / "spec" / "printed_parts_design.json"
        cls.spec = load_printed_parts_spec(cls.spec_path)

    def test_bed_fit_passes(self) -> None:
        violations = validate_bed_fit(self.spec)
        self.assertEqual(violations, [])

    def test_snap_fit_thresholds_pass(self) -> None:
        violations = validate_snap_fit(self.spec)
        self.assertEqual(violations, [])

    def test_critical_support_free_requirement_passes(self) -> None:
        violations = validate_support_requirements(self.spec)
        self.assertEqual(violations, [])

    def test_required_artifacts_exist(self) -> None:
        violations = validate_artifacts(self.spec, self.repo_root)
        self.assertEqual(violations, [])

    def test_spool_holder_requirements_pass(self) -> None:
        violations = validate_spool_holder_support(self.spec)
        self.assertEqual(violations, [])

    def test_full_report_valid(self) -> None:
        report = validate_printed_parts_spec(self.spec, self.repo_root)
        self.assertTrue(report.valid)


if __name__ == "__main__":
    unittest.main()
