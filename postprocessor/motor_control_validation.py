"""Validation helpers for F2.1 motor control acceptance metrics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Trial:
    commanded_mm: float
    observed_mm: float


@dataclass(frozen=True)
class StopTrial:
    scenario: str
    latency_ms: float


@dataclass(frozen=True)
class StallTrial:
    scenario: str
    detected_before_skip_mm: float


@dataclass(frozen=True)
class MotorControlSpec:
    max_position_error_mm: float
    max_stop_latency_ms: float
    max_stall_distance_mm: float
    position_trials: list[Trial]
    stop_trials: list[StopTrial]
    stall_trials: list[StallTrial]


@dataclass(frozen=True)
class ValidationReport:
    position_violations: list[str]
    stop_violations: list[str]
    stall_violations: list[str]

    @property
    def valid(self) -> bool:
        return not (self.position_violations or self.stop_violations or self.stall_violations)


def load_motor_control_spec(path: Path) -> MotorControlSpec:
    raw = json.loads(path.read_text(encoding="utf-8"))
    limits = raw["acceptance_limits"]

    position_trials: list[Trial] = []
    for entry in raw["position_trials"]:
        position_trials.append(Trial(commanded_mm=float(entry["commanded_mm"]), observed_mm=float(entry["observed_mm"])))

    stop_trials: list[StopTrial] = []
    for entry in raw["emergency_stop_trials"]:
        stop_trials.append(StopTrial(scenario=str(entry["scenario"]), latency_ms=float(entry["latency_ms"])))

    stall_trials: list[StallTrial] = []
    for entry in raw["stall_detection_trials"]:
        stall_trials.append(
            StallTrial(
                scenario=str(entry["scenario"]),
                detected_before_skip_mm=float(entry["detected_before_skip_mm"]),
            )
        )

    return MotorControlSpec(
        max_position_error_mm=float(limits["position_accuracy_mm"]),
        max_stop_latency_ms=float(limits["emergency_stop_latency_ms"]),
        max_stall_distance_mm=float(limits["stall_trigger_before_skip_mm"]),
        position_trials=position_trials,
        stop_trials=stop_trials,
        stall_trials=stall_trials,
    )


def validate_position_accuracy(spec: MotorControlSpec) -> list[str]:
    violations: list[str] = []
    for trial in spec.position_trials:
        error_mm = abs(trial.commanded_mm - trial.observed_mm)
        if error_mm > spec.max_position_error_mm:
            violations.append(
                f"Position error exceeds limit: commanded={trial.commanded_mm:.2f}, "
                f"observed={trial.observed_mm:.2f}, error={error_mm:.3f}"
            )
    return violations


def validate_emergency_stop_latency(spec: MotorControlSpec) -> list[str]:
    violations: list[str] = []
    for trial in spec.stop_trials:
        if trial.latency_ms > spec.max_stop_latency_ms:
            violations.append(
                f"Emergency stop latency exceeded in {trial.scenario}: "
                f"{trial.latency_ms:.1f}ms > {spec.max_stop_latency_ms:.1f}ms"
            )
    return violations


def validate_stall_detection(spec: MotorControlSpec) -> list[str]:
    violations: list[str] = []
    for trial in spec.stall_trials:
        if trial.detected_before_skip_mm > spec.max_stall_distance_mm:
            violations.append(
                f"Stall detection too late in {trial.scenario}: "
                f"{trial.detected_before_skip_mm:.2f}mm > {spec.max_stall_distance_mm:.2f}mm"
            )
    return violations


def validate_motor_control_spec(spec: MotorControlSpec) -> ValidationReport:
    return ValidationReport(
        position_violations=validate_position_accuracy(spec),
        stop_violations=validate_emergency_stop_latency(spec),
        stall_violations=validate_stall_detection(spec),
    )
