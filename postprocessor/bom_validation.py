"""Validation helpers for Phase F1.3 bill of materials artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Supplier:
    """Supplier entry for one component."""

    vendor: str
    url: str


@dataclass(frozen=True)
class Component:
    """BOM component entry with tiered costs."""

    component_id: str
    quantity: int
    critical: bool
    cost_budget: float
    cost_standard: float
    cost_premium: float
    suppliers: list[Supplier]


@dataclass(frozen=True)
class BOMSpec:
    """Parsed BOM specification."""

    declared_budget_total: float
    declared_standard_total: float
    declared_premium_total: float
    components: list[Component]
    regional_guides: dict[str, list[str]]


@dataclass(frozen=True)
class ValidationReport:
    """BOM validation report."""

    cost_violations: list[str]
    sourcing_violations: list[str]
    structure_violations: list[str]

    @property
    def valid(self) -> bool:
        """Return True when all checks pass."""
        return not (self.cost_violations or self.sourcing_violations or self.structure_violations)


def load_bom_spec(path: Path) -> BOMSpec:
    """Load BOM catalog specification from JSON."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    components: list[Component] = []
    for item in raw["components"]:
        suppliers: list[Supplier] = []
        for supplier in item["suppliers"]:
            suppliers.append(Supplier(vendor=str(supplier["vendor"]), url=str(supplier["url"])))

        costs = item["cost_unit"]
        components.append(
            Component(
                component_id=str(item["id"]),
                quantity=int(item["quantity"]),
                critical=bool(item["critical"]),
                cost_budget=float(costs["budget"]),
                cost_standard=float(costs["standard"]),
                cost_premium=float(costs["premium"]),
                suppliers=suppliers,
            )
        )

    tiers = raw["cost_tiers"]

    regional_guides: dict[str, list[str]] = {}
    for region, vendors in raw["regional_sourcing_guides"].items():
        regional_guides[str(region)] = [str(vendor) for vendor in vendors]

    return BOMSpec(
        declared_budget_total=float(tiers["budget_total"]),
        declared_standard_total=float(tiers["standard_total"]),
        declared_premium_total=float(tiers["premium_total"]),
        components=components,
        regional_guides=regional_guides,
    )


def compute_tier_totals(spec: BOMSpec) -> dict[str, float]:
    """Calculate total BOM cost per tier."""
    budget = 0.0
    standard = 0.0
    premium = 0.0

    for component in spec.components:
        budget += component.quantity * component.cost_budget
        standard += component.quantity * component.cost_standard
        premium += component.quantity * component.cost_premium

    return {
        "budget_total": round(budget, 2),
        "standard_total": round(standard, 2),
        "premium_total": round(premium, 2),
    }


def validate_costs(spec: BOMSpec) -> list[str]:
    """Validate declared totals and standard tier ceiling."""
    violations: list[str] = []
    calculated = compute_tier_totals(spec)

    if abs(calculated["budget_total"] - spec.declared_budget_total) > 0.5:
        violations.append(
            f"Budget total mismatch: {calculated['budget_total']:.2f} != {spec.declared_budget_total:.2f}"
        )

    if abs(calculated["standard_total"] - spec.declared_standard_total) > 0.5:
        violations.append(
            f"Standard total mismatch: {calculated['standard_total']:.2f} != {spec.declared_standard_total:.2f}"
        )

    if abs(calculated["premium_total"] - spec.declared_premium_total) > 0.5:
        violations.append(
            f"Premium total mismatch: {calculated['premium_total']:.2f} != {spec.declared_premium_total:.2f}"
        )

    if calculated["standard_total"] >= 250.0:
        violations.append(
            f"Standard tier exceeds target ceiling: {calculated['standard_total']:.2f} >= 250.00"
        )

    return violations


def _supplier_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()


def validate_sourcing(spec: BOMSpec) -> list[str]:
    """Check link presence and critical-component supplier redundancy."""
    violations: list[str] = []

    for component in spec.components:
        if len(component.suppliers) == 0:
            violations.append(f"No suppliers listed for component: {component.component_id}")
            continue

        domains: set[str] = set()
        for supplier in component.suppliers:
            if not supplier.url.startswith("https://"):
                violations.append(
                    f"Supplier URL must use https for {component.component_id}: {supplier.url}"
                )
            domain = _supplier_domain(supplier.url)
            if not domain:
                violations.append(
                    f"Supplier URL missing valid domain for {component.component_id}: {supplier.url}"
                )
            domains.add(domain)

        if component.critical and len(domains) < 2:
            violations.append(
                f"Critical component has single-source dependency: {component.component_id}"
            )

    return violations


def validate_structure(spec: BOMSpec) -> list[str]:
    """Validate regional sourcing guide coverage."""
    violations: list[str] = []

    required_regions = ["US", "EU", "ASIA"]
    for region in required_regions:
        vendors = spec.regional_guides.get(region, [])
        if len(vendors) == 0:
            violations.append(f"Missing sourcing guide for region: {region}")

    return violations


def validate_bom_spec(spec: BOMSpec) -> ValidationReport:
    """Run all BOM validation checks."""
    return ValidationReport(
        cost_violations=validate_costs(spec),
        sourcing_violations=validate_sourcing(spec),
        structure_violations=validate_structure(spec),
    )
