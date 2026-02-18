"""Validation helpers for F2.2 encoder system acceptance metrics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PositionTrial:
    expected_mm: float
    observed_mm: float


@dataclass(frozen=True)
class SlipTrial:
    scenario: str
    actual_slip_mm: float
    detected_mm: float


@dataclass(frozen=True)
class CalibrationTrial:
    run: str
    ticks_per_mm: float


@dataclass(frozen=True)
class HealthTrial:
    scenario: str
    valid_transitions: int
    invalid_transitions: int
    expected_degraded: bool


@dataclass(frozen=True)
class EncoderSystemSpec:
    max_position_error_mm: float
    max_slip_detection_mm: float
    max_calibration_variance_percent: float
    health_min_signal_quality: float
    position_trials: list[PositionTrial]
    slip_trials: list[SlipTrial]
    calibration_trials: list[CalibrationTrial]
    health_trials: list[HealthTrial]


@dataclass(frozen=True)
class ValidationReport:
    position_violations: list[str]
    slip_violations: list[str]
    calibration_violations: list[str]
    health_violations: list[str]

    @property
    def valid(self) -> bool:
        return not (
            self.position_violations
            or self.slip_violations
            or self.calibration_violations
            or self.health_violations
        )


def load_encoder_system_spec(path: Path) -> EncoderSystemSpec:
    raw = json.loads(path.read_text(encoding="utf-8"))
    limits = raw["acceptance_limits"]

    position_trials = [
        PositionTrial(expected_mm=float(item["expected_mm"]), observed_mm=float(item["observed_mm"]))
        for item in raw["position_trials"]
    ]
    slip_trials = [
        SlipTrial(
            scenario=str(item["scenario"]),
            actual_slip_mm=float(item["actual_slip_mm"]),
            detected_mm=float(item["detected_mm"]),
        )
        for item in raw["slip_detection_trials"]
    ]
    calibration_trials = [
        CalibrationTrial(run=str(item["run"]), ticks_per_mm=float(item["ticks_per_mm"]))
        for item in raw["calibration_trials"]
    ]
    health_trials = [
        HealthTrial(
            scenario=str(item["scenario"]),
            valid_transitions=int(item["valid_transitions"]),
            invalid_transitions=int(item["invalid_transitions"]),
            expected_degraded=bool(item["expected_degraded"]),
        )
        for item in raw["health_trials"]
    ]

    return EncoderSystemSpec(
        max_position_error_mm=float(limits["position_accuracy_mm"]),
        max_slip_detection_mm=float(limits["slip_detection_mm"]),
        max_calibration_variance_percent=float(limits["calibration_variance_percent"]),
        health_min_signal_quality=float(limits["health_min_signal_quality"]),
        position_trials=position_trials,
        slip_trials=slip_trials,
        calibration_trials=calibration_trials,
        health_trials=health_trials,
    )


def validate_position_accuracy(spec: EncoderSystemSpec) -> list[str]:
    violations: list[str] = []
    for trial in spec.position_trials:
        error_mm = abs(trial.expected_mm - trial.observed_mm)
        if error_mm > spec.max_position_error_mm:
            violations.append(
                "Position error exceeds limit: "
                f"expected={trial.expected_mm:.3f}, observed={trial.observed_mm:.3f}, error={error_mm:.3f}"
            )
    return violations


def validate_slip_detection(spec: EncoderSystemSpec) -> list[str]:
    violations: list[str] = []
    for trial in spec.slip_trials:
        if trial.detected_mm > spec.max_slip_detection_mm:
            violations.append(
                f"Slip detection exceeded limit for {trial.scenario}: "
                f"{trial.detected_mm:.2f}mm > {spec.max_slip_detection_mm:.2f}mm"
            )
        if trial.detected_mm > trial.actual_slip_mm:
            violations.append(
                f"Slip detection was later than actual slip for {trial.scenario}: "
                f"detected={trial.detected_mm:.2f}mm, actual={trial.actual_slip_mm:.2f}mm"
            )
    return violations


def validate_calibration_repeatability(spec: EncoderSystemSpec) -> list[str]:
    if not spec.calibration_trials:
        return ["No calibration trials provided"]

    values = [trial.ticks_per_mm for trial in spec.calibration_trials]
    mean_value = sum(values) / float(len(values))
    spread_percent = ((max(values) - min(values)) / mean_value) * 100.0
    if spread_percent <= spec.max_calibration_variance_percent:
        return []

    return [
        "Calibration variance exceeds limit: "
        f"{spread_percent:.3f}% > {spec.max_calibration_variance_percent:.3f}%"
    ]


def validate_health_monitoring(spec: EncoderSystemSpec) -> list[str]:
    violations: list[str] = []
    for trial in spec.health_trials:
        total = trial.valid_transitions + trial.invalid_transitions
        if total <= 0:
            violations.append(f"Invalid transition totals for {trial.scenario}")
            continue
        quality = trial.valid_transitions / float(total)
        degraded = quality < spec.health_min_signal_quality
        if degraded != trial.expected_degraded:
            violations.append(
                f"Health degradation mismatch for {trial.scenario}: expected_degraded={trial.expected_degraded}, "
                f"measured_quality={quality:.3f}"
            )
    return violations


def validate_encoder_system_spec(spec: EncoderSystemSpec) -> ValidationReport:
    return ValidationReport(
        position_violations=validate_position_accuracy(spec),
        slip_violations=validate_slip_detection(spec),
        calibration_violations=validate_calibration_repeatability(spec),
        health_violations=validate_health_monitoring(spec),
    )
