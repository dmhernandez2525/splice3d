"""Mechanical design validation helpers for F1.1 CAD assets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import combinations
from math import acos, degrees, sqrt
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Vec3:
    """Simple 3D vector in millimeters."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Station:
    """Physical station in the assembly layout."""

    station_id: str
    origin: Vec3
    size: Vec3
    mount_pattern: str


@dataclass(frozen=True)
class PrintablePart:
    """Printable CAD part metadata."""

    name: str
    source_scad: str
    output_stl: str
    bounding_box: Vec3


@dataclass(frozen=True)
class MountInterface:
    """Mechanical interface relationship between stations."""

    source_station: str
    target_station: str
    mount_pattern: str
    clearance_mm: float


@dataclass(frozen=True)
class FilamentPath:
    """Waypoints and allowed deflection metadata."""

    max_deflection_deg: float
    waypoints: list[Vec3]


@dataclass(frozen=True)
class MechanicalLayoutSpec:
    """Parsed F1.1 mechanical layout specification."""

    path: FilamentPath
    stations: list[Station]
    printable_parts: list[PrintablePart]
    interfaces: list[MountInterface]
    printer_bed_limit: tuple[float, float]


@dataclass(frozen=True)
class ValidationReport:
    """Mechanical validation results."""

    path_violations: list[str]
    bed_fit_violations: list[str]
    interface_violations: list[str]
    layout_violations: list[str]

    @property
    def valid(self) -> bool:
        """Return True when no violations exist."""
        return not any(
            [
                self.path_violations,
                self.bed_fit_violations,
                self.interface_violations,
                self.layout_violations,
            ]
        )


def _as_vec3(values: Sequence[float], field_name: str) -> Vec3:
    if len(values) != 3:
        raise ValueError(f"{field_name} requires exactly three values")

    return Vec3(float(values[0]), float(values[1]), float(values[2]))


def load_mechanical_layout(path: Path) -> MechanicalLayoutSpec:
    """Load and parse the JSON mechanical layout manifest."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    assembly = raw["assembly"]
    printer_bed = assembly["printer_bed_limit_mm"]

    stations: list[Station] = []
    for station_raw in raw["stations"]:
        stations.append(
            Station(
                station_id=station_raw["id"],
                origin=_as_vec3(station_raw["origin_mm"], "origin_mm"),
                size=_as_vec3(station_raw["size_mm"], "size_mm"),
                mount_pattern=str(station_raw["mount_pattern"]),
            )
        )

    parts: list[PrintablePart] = []
    for part_raw in raw["printable_parts"]:
        parts.append(
            PrintablePart(
                name=part_raw["name"],
                source_scad=part_raw["source_scad"],
                output_stl=part_raw["output_stl"],
                bounding_box=_as_vec3(part_raw["bounding_box_mm"], "bounding_box_mm"),
            )
        )

    interfaces: list[MountInterface] = []
    for interface_raw in raw["interfaces"]:
        interfaces.append(
            MountInterface(
                source_station=interface_raw["from"],
                target_station=interface_raw["to"],
                mount_pattern=str(interface_raw["mount_pattern"]),
                clearance_mm=float(interface_raw["clearance_mm"]),
            )
        )

    waypoints: list[Vec3] = []
    for waypoint in raw["filament_path"]["waypoints"]:
        waypoints.append(_as_vec3(waypoint["point_mm"], "point_mm"))

    path_spec = FilamentPath(
        max_deflection_deg=float(raw["filament_path"]["max_deflection_deg"]),
        waypoints=waypoints,
    )

    return MechanicalLayoutSpec(
        path=path_spec,
        stations=stations,
        printable_parts=parts,
        interfaces=interfaces,
        printer_bed_limit=(float(printer_bed[0]), float(printer_bed[1])),
    )


def _vector_subtract(a: Vec3, b: Vec3) -> Vec3:
    return Vec3(a.x - b.x, a.y - b.y, a.z - b.z)


def _vector_norm(v: Vec3) -> float:
    return sqrt((v.x * v.x) + (v.y * v.y) + (v.z * v.z))


def _dot(a: Vec3, b: Vec3) -> float:
    return (a.x * b.x) + (a.y * b.y) + (a.z * b.z)


def calculate_deflection_angles(path_points: list[Vec3]) -> list[float]:
    """Calculate internal deflection angles for each path vertex."""
    if len(path_points) < 3:
        return []

    angles: list[float] = []

    for index in range(1, len(path_points) - 1):
        incoming = _vector_subtract(path_points[index], path_points[index - 1])
        outgoing = _vector_subtract(path_points[index + 1], path_points[index])

        incoming_norm = _vector_norm(incoming)
        outgoing_norm = _vector_norm(outgoing)
        if incoming_norm == 0 or outgoing_norm == 0:
            angles.append(0.0)
            continue

        cos_angle = _dot(incoming, outgoing) / (incoming_norm * outgoing_norm)
        cos_clamped = max(-1.0, min(1.0, cos_angle))
        turn_angle = degrees(acos(cos_clamped))
        angles.append(turn_angle)

    return angles


def validate_filament_path(layout: MechanicalLayoutSpec) -> list[str]:
    """Ensure all path turns are below the allowed maximum deflection."""
    violations: list[str] = []
    angles = calculate_deflection_angles(layout.path.waypoints)

    for index, angle in enumerate(angles, start=1):
        if angle > layout.path.max_deflection_deg:
            violations.append(
                f"Waypoint index {index} exceeds deflection limit: "
                f"{angle:.2f} > {layout.path.max_deflection_deg:.2f}"
            )

    return violations


def validate_printable_bed_fit(layout: MechanicalLayoutSpec) -> list[str]:
    """Validate each part can be printed on a standard 220x220mm bed."""
    violations: list[str] = []
    max_x, max_y = layout.printer_bed_limit

    for part in layout.printable_parts:
        if part.bounding_box.x > max_x or part.bounding_box.y > max_y:
            violations.append(
                f"Part {part.name} exceeds bed envelope: "
                f"{part.bounding_box.x:.1f}x{part.bounding_box.y:.1f}"
            )

    return violations


def _bounds(station: Station) -> tuple[Vec3, Vec3]:
    half_x = station.size.x * 0.5
    half_y = station.size.y * 0.5
    half_z = station.size.z * 0.5

    minimum = Vec3(station.origin.x - half_x, station.origin.y - half_y, station.origin.z - half_z)
    maximum = Vec3(station.origin.x + half_x, station.origin.y + half_y, station.origin.z + half_z)
    return minimum, maximum


def validate_station_layout(layout: MechanicalLayoutSpec) -> list[str]:
    """Detect station collisions in compact assembly placement."""
    violations: list[str] = []

    for station_a, station_b in combinations(layout.stations, 2):
        a_min, a_max = _bounds(station_a)
        b_min, b_max = _bounds(station_b)

        overlap_x = min(a_max.x, b_max.x) - max(a_min.x, b_min.x)
        overlap_y = min(a_max.y, b_max.y) - max(a_min.y, b_min.y)
        overlap_z = min(a_max.z, b_max.z) - max(a_min.z, b_min.z)

        if overlap_x > 0 and overlap_y > 0 and overlap_z > 0:
            violations.append(
                f"Station overlap: {station_a.station_id} intersects {station_b.station_id}"
            )

    return violations


def validate_interfaces(layout: MechanicalLayoutSpec) -> list[str]:
    """Ensure mount interfaces reference valid stations and matching mount patterns."""
    violations: list[str] = []
    station_map = {station.station_id: station for station in layout.stations}

    for interface in layout.interfaces:
        source = station_map.get(interface.source_station)
        target = station_map.get(interface.target_station)

        if source is None:
            violations.append(f"Interface source missing: {interface.source_station}")
            continue
        if target is None:
            violations.append(f"Interface target missing: {interface.target_station}")
            continue

        if source.mount_pattern != interface.mount_pattern:
            violations.append(
                f"Source mount mismatch for {interface.source_station}: "
                f"{source.mount_pattern} != {interface.mount_pattern}"
            )

        if target.mount_pattern != interface.mount_pattern:
            violations.append(
                f"Target mount mismatch for {interface.target_station}: "
                f"{target.mount_pattern} != {interface.mount_pattern}"
            )

        if interface.clearance_mm < 0.2:
            violations.append(
                f"Clearance below minimum for {interface.source_station}->{interface.target_station}: "
                f"{interface.clearance_mm:.2f}mm"
            )

    return violations


def validate_layout(layout: MechanicalLayoutSpec) -> ValidationReport:
    """Run all F1.1 mechanical design checks."""
    return ValidationReport(
        path_violations=validate_filament_path(layout),
        bed_fit_violations=validate_printable_bed_fit(layout),
        interface_violations=validate_interfaces(layout),
        layout_violations=validate_station_layout(layout),
    )
