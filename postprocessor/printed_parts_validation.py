"""Validation helpers for F1.4 printed parts design artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SnapFit:
    """Snap-fit strength metadata for a printed part."""

    enabled: bool
    retention_force_n: float
    minimum_force_n: float


@dataclass(frozen=True)
class PartSpec:
    """Printed part spec entry."""

    part_id: str
    source_scad: str
    output_stl: str
    profile_readme: str
    size_x: float
    size_y: float
    size_z: float
    support_required_critical_areas: bool
    snap_fit: SnapFit


@dataclass(frozen=True)
class PrintedPartsSpec:
    """Parsed printed parts design specification."""

    bed_x: float
    bed_y: float
    spool_outer_diameter_mm: float
    spool_hub_diameter_mm: float
    parts: list[PartSpec]


@dataclass(frozen=True)
class ValidationReport:
    """Validation result for F1.4 artifacts."""

    bed_fit_violations: list[str]
    snap_fit_violations: list[str]
    support_violations: list[str]
    artifact_violations: list[str]
    spool_holder_violations: list[str]

    @property
    def valid(self) -> bool:
        """Return True when all checks pass."""
        return not any(
            [
                self.bed_fit_violations,
                self.snap_fit_violations,
                self.support_violations,
                self.artifact_violations,
                self.spool_holder_violations,
            ]
        )


def load_printed_parts_spec(path: Path) -> PrintedPartsSpec:
    """Load F1.4 spec from JSON."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    parts: list[PartSpec] = []
    for entry in raw["parts"]:
        bounds = entry["bounding_box_mm"]
        snap = entry["snap_fit"]
        parts.append(
            PartSpec(
                part_id=str(entry["id"]),
                source_scad=str(entry["source_scad"]),
                output_stl=str(entry["output_stl"]),
                profile_readme=str(entry["profile_readme"]),
                size_x=float(bounds[0]),
                size_y=float(bounds[1]),
                size_z=float(bounds[2]),
                support_required_critical_areas=bool(entry["support_required_critical_areas"]),
                snap_fit=SnapFit(
                    enabled=bool(snap["enabled"]),
                    retention_force_n=float(snap["retention_force_n"]),
                    minimum_force_n=float(snap["minimum_force_n"]),
                ),
            )
        )

    req = raw["spool_holder_requirements"]
    bed = raw["printer_bed_limit_mm"]

    return PrintedPartsSpec(
        bed_x=float(bed[0]),
        bed_y=float(bed[1]),
        spool_outer_diameter_mm=float(req["supported_outer_diameter_mm"]),
        spool_hub_diameter_mm=float(req["supported_hub_diameter_mm"]),
        parts=parts,
    )


def validate_bed_fit(spec: PrintedPartsSpec) -> list[str]:
    """Validate each part fits a 220x220 class print bed."""
    violations: list[str] = []

    for part in spec.parts:
        if part.size_x > spec.bed_x or part.size_y > spec.bed_y:
            violations.append(
                f"Part exceeds bed envelope: {part.part_id} ({part.size_x:.1f}x{part.size_y:.1f})"
            )

    return violations


def validate_snap_fit(spec: PrintedPartsSpec) -> list[str]:
    """Validate snap-fit retention force thresholds."""
    violations: list[str] = []

    for part in spec.parts:
        if not part.snap_fit.enabled:
            continue
        if part.snap_fit.retention_force_n < part.snap_fit.minimum_force_n:
            violations.append(
                f"Snap-fit force below minimum: {part.part_id} "
                f"{part.snap_fit.retention_force_n:.1f} < {part.snap_fit.minimum_force_n:.1f}"
            )

    return violations


def validate_support_requirements(spec: PrintedPartsSpec) -> list[str]:
    """Ensure critical functional areas remain support-free."""
    violations: list[str] = []

    for part in spec.parts:
        if part.support_required_critical_areas:
            violations.append(f"Supports required in critical areas: {part.part_id}")

    return violations


def validate_artifacts(spec: PrintedPartsSpec, repo_root: Path) -> list[str]:
    """Validate CAD and print profile files exist for every part."""
    violations: list[str] = []

    for part in spec.parts:
        source_path = repo_root / part.source_scad
        profile_path = repo_root / part.profile_readme

        if not source_path.exists():
            violations.append(f"Missing CAD source: {part.source_scad}")

        if not profile_path.exists():
            violations.append(f"Missing print profile README: {part.profile_readme}")

    return violations


def validate_spool_holder_support(spec: PrintedPartsSpec) -> list[str]:
    """Validate spool holder geometry envelope against 1kg spool requirements."""
    violations: list[str] = []

    spool_parts = [part for part in spec.parts if part.part_id == "spool_holder"]
    if len(spool_parts) != 1:
        return ["Spool holder part entry missing or duplicated"]

    spool_holder = spool_parts[0]

    if spool_holder.size_x < spec.spool_outer_diameter_mm:
        violations.append(
            f"Spool holder width too small: {spool_holder.size_x:.1f} < {spec.spool_outer_diameter_mm:.1f}"
        )

    if spool_holder.size_y < spec.spool_hub_diameter_mm:
        violations.append(
            f"Spool holder hub support too small: {spool_holder.size_y:.1f} < {spec.spool_hub_diameter_mm:.1f}"
        )

    return violations


def validate_printed_parts_spec(spec: PrintedPartsSpec, repo_root: Path) -> ValidationReport:
    """Run all F1.4 printed-parts checks."""
    return ValidationReport(
        bed_fit_violations=validate_bed_fit(spec),
        snap_fit_violations=validate_snap_fit(spec),
        support_violations=validate_support_requirements(spec),
        artifact_violations=validate_artifacts(spec, repo_root),
        spool_holder_violations=validate_spool_holder_support(spec),
    )
