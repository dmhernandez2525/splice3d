"""Validation helpers for Phase F1.2 electronics design artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PowerRail:
    """Power rail metadata for a supply mode."""

    name: str
    voltage_v: float
    max_current_a: float


@dataclass(frozen=True)
class PowerMode:
    """Input power mode and available rails."""

    name: str
    rails: dict[str, PowerRail]


@dataclass(frozen=True)
class Load:
    """Electrical load that draws current from rails by mode."""

    load_id: str
    rail_by_mode: dict[str, str]
    current_by_mode_a: dict[str, float]


@dataclass(frozen=True)
class ValidationReport:
    """Result of F1.2 electronics validation checks."""

    drc_violations: list[str]
    sourcing_violations: list[str]
    power_budget_violations: list[str]

    @property
    def valid(self) -> bool:
        """Return True when no violations are present."""
        return not (self.drc_violations or self.sourcing_violations or self.power_budget_violations)


@dataclass(frozen=True)
class ElectronicsSpec:
    """Strongly typed representation of the electronics design spec."""

    required_subsystems: list[str]
    required_safety_features: list[str]
    required_esd_connectors: list[str]
    subsystems_enabled: dict[str, bool]
    safety_features: dict[str, bool]
    connector_esd_map: dict[str, str]
    critical_sourcing: dict[str, list[str]]
    power_modes: dict[str, PowerMode]
    loads: list[Load]


def load_electronics_spec(path: Path) -> ElectronicsSpec:
    """Load and parse electronics design data from JSON."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    rules = raw["drc_rules"]
    subsystem_data = raw["subsystems"]
    safety_data = raw["safety"]

    connector_esd_map: dict[str, str] = {}
    for connector in raw["external_connectors"]:
        connector_esd_map[str(connector["id"])] = str(connector["esd_device"])

    critical_sourcing: dict[str, list[str]] = {}
    for item in raw["sourcing"]:
        if bool(item["critical"]):
            available_vendors: list[str] = []
            for alt in item["alternatives"]:
                if str(alt["availability"]).lower() == "in_stock":
                    available_vendors.append(str(alt["vendor"]))
            critical_sourcing[str(item["component"])] = available_vendors

    power_modes: dict[str, PowerMode] = {}
    for mode in raw["power_modes"]:
        rail_map: dict[str, PowerRail] = {}
        for rail in mode["rails"]:
            rail_map[str(rail["name"])] = PowerRail(
                name=str(rail["name"]),
                voltage_v=float(rail["voltage_v"]),
                max_current_a=float(rail["max_current_a"]),
            )
        mode_name = str(mode["mode"])
        power_modes[mode_name] = PowerMode(name=mode_name, rails=rail_map)

    loads: list[Load] = []
    for load in raw["loads"]:
        rail_by_mode = {str(key): str(value) for key, value in load["rail_by_mode"].items()}
        current_by_mode = {
            str(key): float(value) for key, value in load["current_by_mode_a"].items()
        }
        loads.append(
            Load(
                load_id=str(load["id"]),
                rail_by_mode=rail_by_mode,
                current_by_mode_a=current_by_mode,
            )
        )

    subsystems_enabled = {
        key: bool(value.get("enabled", False)) for key, value in subsystem_data.items()
    }

    safety_features = {key: bool(value) for key, value in safety_data.items()}

    return ElectronicsSpec(
        required_subsystems=[str(item) for item in rules["required_subsystems"]],
        required_safety_features=[str(item) for item in rules["required_safety_features"]],
        required_esd_connectors=[str(item) for item in rules["required_esd_connectors"]],
        subsystems_enabled=subsystems_enabled,
        safety_features=safety_features,
        connector_esd_map=connector_esd_map,
        critical_sourcing=critical_sourcing,
        power_modes=power_modes,
        loads=loads,
    )


def validate_drc(spec: ElectronicsSpec) -> list[str]:
    """Validate rule-driven design checks for required circuitry."""
    violations: list[str] = []

    for subsystem in spec.required_subsystems:
        if not spec.subsystems_enabled.get(subsystem, False):
            violations.append(f"Required subsystem not enabled: {subsystem}")

    for feature in spec.required_safety_features:
        if not spec.safety_features.get(feature, False):
            violations.append(f"Required safety feature missing: {feature}")

    for connector in spec.required_esd_connectors:
        esd_device = spec.connector_esd_map.get(connector, "")
        if not esd_device:
            violations.append(f"Required ESD connector missing: {connector}")

    return violations


def validate_sourcing(spec: ElectronicsSpec) -> list[str]:
    """Ensure every critical component has at least two available suppliers."""
    violations: list[str] = []

    for component, vendors in spec.critical_sourcing.items():
        unique_vendors = sorted(set(vendors))
        if len(unique_vendors) < 2:
            violations.append(
                f"Critical component lacks supplier redundancy: {component} ({len(unique_vendors)})"
            )

    return violations


def _compute_mode_currents(spec: ElectronicsSpec, mode_name: str) -> dict[str, float]:
    """Aggregate current per rail for one power mode."""
    totals: dict[str, float] = {}

    for load in spec.loads:
        if mode_name not in load.rail_by_mode:
            raise ValueError(f"Load {load.load_id} missing rail mapping for mode {mode_name}")
        if mode_name not in load.current_by_mode_a:
            raise ValueError(f"Load {load.load_id} missing current mapping for mode {mode_name}")

        rail_name = load.rail_by_mode[mode_name]
        current = load.current_by_mode_a[mode_name]
        totals[rail_name] = totals.get(rail_name, 0.0) + current

    return totals


def validate_power_budget(spec: ElectronicsSpec) -> list[str]:
    """Validate current draw for each rail in each power mode."""
    violations: list[str] = []

    for mode_name, mode in spec.power_modes.items():
        totals = _compute_mode_currents(spec, mode_name)

        for rail_name, current in totals.items():
            rail = mode.rails.get(rail_name)
            if rail is None:
                violations.append(f"Mode {mode_name} references unknown rail: {rail_name}")
                continue

            if current > rail.max_current_a:
                violations.append(
                    f"Power budget exceeded in {mode_name} for {rail_name}: "
                    f"{current:.2f}A > {rail.max_current_a:.2f}A"
                )

    return violations


def summarize_power_budget(spec: ElectronicsSpec) -> dict[str, dict[str, float]]:
    """Return current totals per rail and mode for reporting."""
    summary: dict[str, dict[str, float]] = {}

    for mode_name in spec.power_modes:
        summary[mode_name] = _compute_mode_currents(spec, mode_name)

    return summary


def validate_electronics_spec(spec: ElectronicsSpec) -> ValidationReport:
    """Run all validation checks for the F1.2 electronics design spec."""
    return ValidationReport(
        drc_violations=validate_drc(spec),
        sourcing_violations=validate_sourcing(spec),
        power_budget_violations=validate_power_budget(spec),
    )
