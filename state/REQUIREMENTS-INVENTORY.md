# Splice3D Requirements Inventory

> Flat, numbered checklist of every discrete, testable requirement.
> Source: README.md, SOFTWARE_DESIGN_DOCUMENT.md, FEATURE_ROADMAP.md, ROADMAP.md, hardware specs

---

## Post-Processor Module

- REQ-001: [Parser] Parse multi-tool G-code with T-command extraction (T0, T1, etc.) (source: SDD)
- REQ-002: [Parser] Support M600 color change commands (source: SDD)
- REQ-003: [Parser] Track extrusion in absolute (M82) and relative (M83) modes (source: SDD)
- REQ-004: [Parser] Handle G92 E reset commands (source: SDD)
- REQ-005: [Parser] Extract layer information from slicer comments (source: SDD)
- REQ-006: [Parser] Support OrcaSlicer, PrusaSlicer, BambuStudio G-code formats (source: SDD)
- REQ-007: [Parser] Return ParseResult with segments, total_length_mm, color_count, layer_count, errors, warnings (source: SDD)
- REQ-008: [Recipe] Generate JSON recipe with version, segments, colors, metadata (source: SDD)
- REQ-009: [Recipe] Merge segments below configurable minimum length (source: SDD)
- REQ-010: [Recipe] Add transition lengths for color purging (source: SDD)
- REQ-011: [Recipe] Map tool indices to color names (source: SDD)
- REQ-012: [Modifier] Remove tool change commands from G-code (source: SDD)
- REQ-013: [Modifier] Add pause injection at start for spool loading (source: SDD)
- REQ-014: [Modifier] Add Splice3D header comments to modified G-code (source: SDD)
- REQ-015: [Validator] Validate recipe segment count within limits (MAX_SEGMENTS=10000) (source: SDD)
- REQ-016: [Validator] Validate segment lengths within range (3.0-50000.0mm) (source: SDD)
- REQ-017: [Validator] Validate color count <= 8 (source: SDD)
- REQ-018: [Validator] Report validation errors and warnings (source: SDD)
- REQ-019: [Profiles] Material profiles for PLA, PETG, ABS with temperature/timing (source: SDD)
- REQ-020: [CLI] splice3d main entry point with --output, --transition, --min-segment, --no-pause, --verbose, --colors (source: SDD)
- REQ-021: [CLI] splice3d-analyze for G-code analysis (source: SDD)
- REQ-022: [CLI] splice3d-simulate for firmware simulation (source: SDD)

## Firmware Core

- REQ-023: [State Machine] 13-state splice cycle (IDLE through COMPLETE + ERROR) (source: SDD)
- REQ-024: [State Machine] Recipe loading from serial (source: SDD)
- REQ-025: [State Machine] START/PAUSE/RESUME/ABORT commands (source: SDD)
- REQ-026: [State Machine] Progress reporting (segment N/total) (source: SDD)
- REQ-027: [Serial] Command protocol: RECIPE, START, PAUSE, RESUME, ABORT, STATUS, HELP (source: SDD)
- REQ-028: [Serial] Response protocol: OK, ERROR, STATUS, PROGRESS, DONE messages (source: SDD)
- REQ-029: [Serial] Buffer handling for incoming commands (source: config.h)
- REQ-030: [Serial] TEMP command for temperature control (source: serial_temperature.cpp)
- REQ-031: [Serial] ENCODER command for encoder status/calibration (source: serial_encoder.cpp)
- REQ-032: [Serial] CUTTER command for cutter control (source: serial_cutting.cpp)
- REQ-033: [Serial] RECOVER command for error recovery (source: serial_recovery.cpp)
- REQ-034: [Serial] STREAM command for telemetry control (source: serial_telemetry.cpp)

## Firmware Subsystems

- REQ-035: [Stepper] 4-axis stepper control: FEED_A, FEED_B, WINDER, CUTTER (source: stepper_control.h)
- REQ-036: [Stepper] AccelStepper non-blocking acceleration profiles (source: SDD)
- REQ-037: [Stepper] TMC2209 UART configuration (StealthChop, current, stall detect) (source: tmc_config.h)
- REQ-038: [Stepper] Backlash compensation (source: stepper_control.cpp)
- REQ-039: [Stepper] Sensorless homing via stall detection (source: stepper_control.cpp)
- REQ-040: [Temp] PID temperature control with auto-tune (source: temperature.h)
- REQ-041: [Temp] Material profiles: PLA 210C, PETG 235C, ABS 250C (source: temperature.cpp)
- REQ-042: [Temp] Thermal runaway detection (10C rise in 40s window) (source: config.h)
- REQ-043: [Temp] Thermistor disconnect detection (-10C to 350C range) (source: config.h)
- REQ-044: [Temp] Cold extrusion prevention (block below 170C) (source: config.h)
- REQ-045: [Temp] PID watchdog (2s loop timeout) (source: config.h)
- REQ-046: [Temp] Heating stages: OFF, PREHEAT, SOAK, READY, FAULT (source: temperature.h)
- REQ-047: [Encoder] Quadrature encoder with ISR-driven counting (source: encoder_system.h)
- REQ-048: [Encoder] Slip detection (2mm threshold, 16-sample window) (source: config.h)
- REQ-049: [Encoder] Closed-loop correction (0.25 gain, 0.35mm max, 120ms interval) (source: config.h)
- REQ-050: [Encoder] EEPROM calibration storage with checksum (source: encoder_system.cpp)
- REQ-051: [Encoder] Health monitoring (stale threshold 1.5s) (source: config.h)
- REQ-052: [Cutter] Servo-based cutting system (open/closed angles) (source: cutting_system.h)
- REQ-053: [Cutter] Cut verification and blade wear tracking (source: cutting_system spec)
- REQ-054: [Cutter] EEPROM persistence for maintenance counters (source: config.h)
- REQ-055: [Error] Error codes for thermal, motor, filament, cutter, recipe, serial (source: error_handler.h)
- REQ-056: [Error] Recovery actions: RETRY_ONCE, RETRY_AFTER_COOL, MANUAL_REQUIRED, ABORT, RESET (source: error_handler.h)
- REQ-057: [Error] Error recovery state machine: IDLE, ASSESSING, COOLDOWN, RETRYING, AWAITING_USER, RESOLVED, UNRECOVERABLE (source: error_recovery.h)
- REQ-058: [Error] Emergency shutdown (disable all outputs) (source: error_handler.h)

## Safety Requirements

- REQ-059: [Safety] MAX_TEMP emergency shutoff at 280C (source: config.h)
- REQ-060: [Safety] Heater timeout at 120s (source: config.h)
- REQ-061: [Safety] Cooling fan auto-enable on fault (source: temperature.cpp)
- REQ-062: [Safety] Emergency stop via ABORT command (source: state_machine.cpp)

## Hardware Validation Specs (40 specs across hardware/f*_*/spec/)

- REQ-063: [HW] F1.1 Mechanical design validation (source: hardware/f1_1/spec)
- REQ-064: [HW] F1.2 Electronics design validation (source: hardware/f1_2/spec)
- REQ-065: [HW] F1.3 BOM validation (source: hardware/f1_3/spec)
- REQ-066: [HW] F1.4 Printed parts validation (source: hardware/f1_4/spec)
- REQ-067: [HW] F2.1 Motor control validation (source: hardware/f2_1/spec)
- REQ-068: [HW] F2.2 Encoder system validation (source: hardware/f2_2/spec)
- REQ-069: [HW] F2.3 Temperature control validation (source: hardware/f2_3/spec)
- REQ-070: [HW] F2.4 Cutting system validation (source: hardware/f2_4/spec)
- REQ-071: [HW] F3.1 Filament feeding validation (source: hardware/f3_1/spec)
- REQ-072: [HW] F3.2 Splice execution validation (source: hardware/f3_2/spec)
- REQ-073: [HW] F3.3 Position tracking validation (source: hardware/f3_3/spec)
- REQ-074: [HW] F3.4 Error recovery validation (source: hardware/f3_4/spec)
- REQ-075: [HW] F4.1 Telemetry stream validation (source: hardware/f4_1/spec)
- REQ-076: [HW] F4.2-F4.4 Quality, job queue, batch processing validation (source: hardware/f4_*/spec)
- REQ-077: [HW] F5.1-F5.4 Material, cross-material, profile, validator validation (source: hardware/f5_*/spec)
- REQ-078: [HW] F6.1-F6.4 Segment batch, thermal opt, waste, speed validation (source: hardware/f6_*/spec)
- REQ-079: [HW] F7.1-F7.4 Slicer plugins (Orca, Prusa, Cura, Bambu) validation (source: hardware/f7_*/spec)
- REQ-080: [HW] F8.1-F8.4 Recipe editor, preview, connection, queue mgr validation (source: hardware/f8_*/spec)
- REQ-081: [HW] F9.1-F9.4 WiFi, dashboard, OTA, notifications validation (source: hardware/f9_*/spec)
- REQ-082: [HW] F10.1-F10.4 Realtime, multi-color, print farm, mfg-ready validation (source: hardware/f10_*/spec)

## Integration & Infrastructure

- REQ-083: [MQTT] Home Assistant MQTT bridge service (source: services/mqtt_bridge.py)
- REQ-084: [Docker] Docker/docker-compose for deployment (source: Dockerfile, docker-compose.yml)
- REQ-085: [CI] pytest/coverage in CI pipeline (source: pyproject.toml, codecov.yml)
- REQ-086: [Render] render.yaml for cloud deployment (source: render.yaml)

## Code Quality

- REQ-087: [Quality] 80%+ test coverage across all metrics (source: CLAUDE.md)
- REQ-088: [Quality] Zero lint errors (source: CLAUDE.md)
- REQ-089: [Quality] All Python files compile without errors (source: standard)
- REQ-090: [Quality] No hardcoded user paths in committed code (source: CLAUDE.md)
- REQ-091: [Quality] No hardcoded secrets in committed code (source: CLAUDE.md)

## Firmware Issues (from RIP Review)

- REQ-092: [FW-Fix] H1: Serial buffer size matches config (256 vs 512 mismatch) (source: RIP review)
- REQ-093: [FW-Fix] H2: JSON parsing validates bounds and input (source: RIP review)
- REQ-094: [FW-Fix] H3: TMC2209 init validates communication success (source: RIP review)
- REQ-095: [FW-Fix] H4: Auto-tune guards against division by zero (source: RIP review)
- REQ-096: [FW-Fix] H5: Unified error state machine (source: RIP review)
- REQ-097: [FW-Fix] H6: No static variables in state handlers (source: RIP review)
- REQ-098: [FW-Fix] H7: millis() rollover-safe timeout patterns (source: RIP review)
- REQ-099: [FW-Fix] H8: Watchdog timer enabled (source: RIP review)
- REQ-100: [FW-Fix] M1-M14: Medium severity firmware issues (source: RIP review)
