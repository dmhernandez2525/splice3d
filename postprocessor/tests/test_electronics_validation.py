"""Tests for F1.2 electronics validation logic."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from postprocessor.electronics_validation import (
    load_electronics_spec,
    summarize_power_budget,
    validate_drc,
    validate_electronics_spec,
    validate_power_budget,
    validate_sourcing,
)


class TestElectronicsValidation(unittest.TestCase):
    """Validation tests for the electronics design manifest."""

    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        cls.spec_path = repo_root / "hardware" / "f1_2" / "spec" / "electronics_design.json"
        cls.spec = load_electronics_spec(cls.spec_path)

    def test_drc_rules_pass(self) -> None:
        violations = validate_drc(self.spec)
        self.assertEqual(violations, [])

    def test_supplier_redundancy_passes(self) -> None:
        violations = validate_sourcing(self.spec)
        self.assertEqual(violations, [])

    def test_power_budget_passes(self) -> None:
        violations = validate_power_budget(self.spec)
        self.assertEqual(violations, [])

    def test_power_budget_totals(self) -> None:
        summary = summarize_power_budget(self.spec)
        self.assertIn("24V", summary)
        self.assertIn("12V", summary)

        self.assertLessEqual(summary["24V"]["VIN_24"], 8.0)
        self.assertLessEqual(summary["24V"]["VREG_5"], 2.0)
        self.assertLessEqual(summary["12V"]["VIN_12"], 10.0)
        self.assertLessEqual(summary["12V"]["VREG_5"], 2.0)

    def test_full_report_valid(self) -> None:
        report = validate_electronics_spec(self.spec)
        self.assertTrue(report.valid)


if __name__ == "__main__":
    unittest.main()
