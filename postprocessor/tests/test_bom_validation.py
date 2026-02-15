"""Tests for F1.3 BOM validation rules."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from postprocessor.bom_validation import (
    compute_tier_totals,
    load_bom_spec,
    validate_bom_spec,
    validate_costs,
    validate_sourcing,
    validate_structure,
)


class TestBomValidation(unittest.TestCase):
    """Validation coverage for BOM artifact checks."""

    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        cls.spec_path = repo_root / "hardware" / "f1_3" / "spec" / "bom_catalog.json"
        cls.spec = load_bom_spec(cls.spec_path)

    def test_cost_validation_passes(self) -> None:
        violations = validate_costs(self.spec)
        self.assertEqual(violations, [])

    def test_sourcing_validation_passes(self) -> None:
        violations = validate_sourcing(self.spec)
        self.assertEqual(violations, [])

    def test_structure_validation_passes(self) -> None:
        violations = validate_structure(self.spec)
        self.assertEqual(violations, [])

    def test_standard_tier_under_limit(self) -> None:
        totals = compute_tier_totals(self.spec)
        self.assertLess(totals["standard_total"], 250.0)

    def test_full_bom_report_valid(self) -> None:
        report = validate_bom_spec(self.spec)
        self.assertTrue(report.valid)


if __name__ == "__main__":
    unittest.main()
