# Verification-1: Functional Completeness Audit (Cycle 1)

> Auditor: Verifier-1 (Functional Completeness)
> Date: 2026-03-28
> Scope: REQ-001 through REQ-100 against actual codebase
> Method: Direct code reading of implementation files, test files, and configuration

---

## Summary

| Rating   | Count |
|----------|-------|
| DONE     | 62    |
| PARTIAL  | 19    |
| MISSING  | 8     |
| BROKEN   | 11    |

---

## Post-Processor Module (REQ-001 through REQ-022)

### REQ-001: [Parser] Parse multi-tool G-code with T-command extraction
**DONE**
- File: `postprocessor/gcode_parser.py:45` -- `TOOL_CHANGE_PATTERN = re.compile(r'^T(\d+)', re.IGNORECASE)`
- File: `postprocessor/gcode_parser.py:130-146` -- tool change handling creates segments on T-command
- Test: `postprocessor/tests/test_parser.py::TestGCodeParser::test_tool_changes`

### REQ-002: [Parser] Support M600 color change commands
**DONE**
- File: `postprocessor/gcode_parser.py:46` -- `M600_PATTERN = re.compile(r'^M600', re.IGNORECASE)`
- File: `postprocessor/gcode_parser.py:148-163` -- M600 handler toggles color
- Note: M600 hardcodes 2-color toggle `(self.current_tool + 1) % 2`. This is a limitation but matches the spec for M600 which typically implies a single filament change.

### REQ-003: [Parser] Track extrusion in absolute (M82) and relative (M83) modes
**DONE**
- File: `postprocessor/gcode_parser.py:122-127` -- M82/M83 handling
- File: `postprocessor/gcode_parser.py:170-177` -- absolute vs relative extrusion tracking
- Test: `postprocessor/tests/test_parser.py::TestGCodeParser::test_relative_extrusion`

### REQ-004: [Parser] Handle G92 E reset commands
**DONE**
- File: `postprocessor/gcode_parser.py:179-186` -- G92 E handling with offset adjustment
- Test: `postprocessor/tests/test_parser.py::TestGCodeParser::test_g92_reset`

### REQ-005: [Parser] Extract layer information from slicer comments
**DONE**
- File: `postprocessor/gcode_parser.py:48` -- `LAYER_PATTERN = re.compile(r';LAYER:(\d+)|;LAYER_CHANGE', re.IGNORECASE)`
- File: `postprocessor/gcode_parser.py:112-118` -- Layer tracking from comments

### REQ-006: [Parser] Support OrcaSlicer, PrusaSlicer, BambuStudio G-code formats
**PARTIAL**
- The parser uses generic patterns that should work across slicers, but there is no slicer-specific detection or handling.
- The `LAYER_PATTERN` covers `;LAYER:N` (PrusaSlicer/BambuStudio) and `;LAYER_CHANGE` (OrcaSlicer).
- Missing: No explicit handling for BambuStudio-specific features like plate metadata or Orca-specific purge tower comments.
- Missing: No test cases exercising actual slicer-specific G-code output.

### REQ-007: [Parser] Return ParseResult with segments, total_length_mm, color_count, layer_count, errors, warnings
**DONE**
- File: `postprocessor/gcode_parser.py:27-35` -- `ParseResult` dataclass with all required fields
- File: `postprocessor/gcode_parser.py:195-204` -- All fields populated after parsing

### REQ-008: [Recipe] Generate JSON recipe with version, segments, colors, metadata
**DONE**
- File: `postprocessor/recipe_generator.py:15-31` -- `SpliceRecipe` dataclass with version, segments, colors, metadata
- File: `postprocessor/recipe_generator.py:67-113` -- `generate()` populates all fields
- Test: `postprocessor/tests/test_recipe.py`

### REQ-009: [Recipe] Merge segments below configurable minimum length
**DONE**
- File: `postprocessor/recipe_generator.py:115-168` -- `_merge_small_segments()` with configurable `min_segment_length_mm`
- Logic handles same-color merging and too-small segment absorption correctly.

### REQ-010: [Recipe] Add transition lengths for color purging
**DONE**
- File: `postprocessor/recipe_generator.py:170-192` -- `_add_transitions()` adds `transition_length_mm` to each segment except last

### REQ-011: [Recipe] Map tool indices to color names
**DONE**
- File: `postprocessor/recipe_generator.py:39-49` -- `DEFAULT_COLORS` dict maps indices 0-7 to color names
- File: `postprocessor/recipe_generator.py:85-86` -- Used colors mapped in output

### REQ-012: [Modifier] Remove tool change commands from G-code
**DONE**
- File: `postprocessor/gcode_modifier.py:99-101` -- T-commands replaced with comments
- Test: `postprocessor/tests/test_gcode_modifier.py`

### REQ-013: [Modifier] Add pause injection at start for spool loading
**DONE**
- File: `postprocessor/gcode_modifier.py:89-96` -- Pause injection with M0 command after start G-code detection
- Configurable via `add_pause_at_start` parameter

### REQ-014: [Modifier] Add Splice3D header comments to modified G-code
**DONE**
- File: `postprocessor/gcode_modifier.py:109-122` -- `_generate_header()` adds Splice3D header block

### REQ-015: [Validator] Validate recipe segment count within limits (MAX_SEGMENTS=10000)
**DONE**
- File: `postprocessor/recipe_validator.py:41` -- `MAX_SEGMENTS = 10000`
- File: `postprocessor/recipe_validator.py:68-69` -- Validation check

### REQ-016: [Validator] Validate segment lengths within range (3.0-50000.0mm)
**DONE**
- File: `postprocessor/recipe_validator.py:39-40` -- `MIN_SEGMENT_LENGTH_MM = 3.0`, `MAX_SEGMENT_LENGTH_MM = 50000.0`
- File: `postprocessor/recipe_validator.py:89-94` -- Length validation per segment

### REQ-017: [Validator] Validate color count <= 8
**DONE**
- File: `postprocessor/recipe_validator.py:42` -- `MAX_COLORS = 8`
- File: `postprocessor/recipe_validator.py:100-101` -- Color count validation

### REQ-018: [Validator] Report validation errors and warnings
**DONE**
- File: `postprocessor/recipe_validator.py:14-32` -- `ValidationResult` with errors, warnings, and string formatting
- Test: `postprocessor/tests/test_recipe_validator.py`

### REQ-019: [Profiles] Material profiles for PLA, PETG, ABS with temperature/timing
**DONE**
- File: `postprocessor/filament_profiles.py:42-108` -- PLA (210C), PETG (235C), ABS (250C) plus specialty profiles
- Test: `postprocessor/tests/test_filament_profiles.py`

### REQ-020: [CLI] splice3d main entry point with all options
**DONE**
- File: `postprocessor/splice3d_postprocessor.py:28-66` -- argparse with `--output`, `--transition`, `--min-segment`, `--no-pause`, `--verbose`, `--colors`
- File: `pyproject.toml:42` -- Entry point: `splice3d = "postprocessor.splice3d_postprocessor:main"`
- Test: `postprocessor/tests/test_splice3d_postprocessor.py`

### REQ-021: [CLI] splice3d-analyze for G-code analysis
**DONE**
- File: `cli/analyze_gcode.py` -- Full analysis tool with SegmentStats, AnalysisResult, color distribution
- File: `pyproject.toml:43` -- Entry point: `splice3d-analyze = "cli.analyze_gcode:main"`

### REQ-022: [CLI] splice3d-simulate for firmware simulation
**DONE**
- File: `cli/simulator.py` -- Full simulator with 14-state state machine, SimConfig, timing simulation
- File: `pyproject.toml:44` -- Entry point: `splice3d-simulate = "cli.simulator:main"`

---

## Firmware Core (REQ-023 through REQ-034)

### REQ-023: [State Machine] 13-state splice cycle (IDLE through COMPLETE + ERROR)
**BROKEN**
- File: `firmware/src/state_machine.h:24-39` -- Defines 14 states (IDLE, LOADING, READY, FEEDING_A, FEEDING_B, CUTTING, POSITIONING, HEATING, WELDING, COOLING, SPOOLING, NEXT_SEGMENT, COMPLETE, ERROR)
- The state count is actually 14, not 13 as specified (FEEDING_A and FEEDING_B are separate states). This is a spec discrepancy, not a bug.
- **Critical issue:** All state handlers use `static bool` local variables (e.g., `feedStarted`, `cutStarted`, etc.) at `state_machine.cpp:217,237,255,271,288,313,329,351,392`. These static variables are never reset when transitioning TO a state from a non-standard path (e.g., after ABORT then re-START). If a state is entered mid-cycle via error recovery, the static flag retains its previous value, causing the handler to skip initialization.

### REQ-024: [State Machine] Recipe loading from serial
**DONE**
- File: `firmware/src/serial_handler.cpp:119-193` -- `handleRecipe()` parses JSON and calls `loadRecipe()`
- File: `firmware/src/state_machine.cpp:75-98` -- `loadRecipe()` copies segments, transitions to READY

### REQ-025: [State Machine] START/PAUSE/RESUME/ABORT commands
**DONE**
- File: `firmware/src/state_machine.cpp:100-163` -- `start()`, `pause()`, `resume()`, `abort()` all implemented
- PAUSE saves state, stops motors, disables heater. RESUME restores state. ABORT resets to IDLE.

### REQ-026: [State Machine] Progress reporting (segment N/total)
**DONE**
- File: `firmware/src/state_machine.cpp:367-374` -- `PROGRESS N/total` printed at each segment transition
- File: `firmware/src/state_machine.cpp:165-168` -- `getProgress()` method

### REQ-027: [Serial] Command protocol: RECIPE, START, PAUSE, RESUME, ABORT, STATUS, HELP
**DONE**
- File: `firmware/src/serial_handler.cpp:77-116` -- All commands dispatched

### REQ-028: [Serial] Response protocol: OK, ERROR, STATUS, PROGRESS, DONE messages
**DONE**
- OK responses: `serial_handler.cpp:187`, `state_machine.cpp:122,139,151,163`
- ERROR responses: `serial_handler.cpp:114,121,134,140`
- STATUS: `serial_handler.cpp:216-239`
- PROGRESS: `state_machine.cpp:371-374`
- DONE: `state_machine.cpp:395`

### REQ-029: [Serial] Buffer handling for incoming commands
**BROKEN** (see also REQ-092)
- File: `firmware/src/serial_handler.h:38` -- `char _buffer[256]`
- File: `firmware/src/config.h:23` -- `SERIAL_BUFFER_SIZE 512`
- The buffer is hardcoded at 256 bytes in the header, not using the config constant. Additionally, there is no overflow protection message when the buffer fills; it simply stops accepting characters silently.

### REQ-030: [Serial] TEMP command for temperature control
**DONE**
- File: `firmware/src/serial_temperature.cpp:9-98` -- Handles: bare TEMP (status), TEMP <value>, TEMP MATERIAL, TEMP PID, TEMP AUTOTUNE, TEMP FAN, TEMP HEATER

### REQ-031: [Serial] ENCODER command for encoder status/calibration
**DONE**
- File: `firmware/src/serial_encoder.cpp:43-111` -- Handles: STATUS, CAL_START, CAL_COMPLETE, TICKS_PER_MM, LOG_INTERVAL, CLOSED_LOOP, SAVE, RESET_COUNTERS

### REQ-032: [Serial] CUTTER command for cutter control
**DONE**
- File: `firmware/src/serial_cutting.cpp:7-75` -- Handles: STATUS, CUT, ANGLES, TRAVEL, MAINT_ACK, SAVE, RESET, MAINT_INTERVAL

### REQ-033: [Serial] RECOVER command for error recovery
**DONE**
- File: `firmware/src/serial_recovery.cpp:4-93` -- Handles: BEGIN, CONFIRM, ABORT, STATS, RESET_STATS, CONFIG

### REQ-034: [Serial] STREAM command for telemetry control
**DONE**
- File: `firmware/src/serial_telemetry.cpp:3-55` -- Handles: OFF, SUMMARY, VERBOSE, INTERVAL, HEARTBEAT, REPORT

---

## Firmware Subsystems (REQ-035 through REQ-058)

### REQ-035: [Stepper] 4-axis stepper control: FEED_A, FEED_B, WINDER, CUTTER
**DONE**
- File: `firmware/src/stepper_control.h:13-18` -- `MotorAxis` enum with all 4 axes
- File: `firmware/src/stepper_control.cpp:12-19` -- AccelStepper instances for all axes (servo fallback for cutter)

### REQ-036: [Stepper] AccelStepper non-blocking acceleration profiles
**DONE**
- File: `firmware/src/stepper_control.cpp:4` -- `#include <AccelStepper.h>`
- File: `firmware/src/stepper_control.cpp:151-172` -- `runSteppers()` calls `.run()` on all steppers (non-blocking)
- File: `firmware/src/stepper_control.cpp:71-80` -- `applyProfile()` with jerk-limited acceleration

### REQ-037: [Stepper] TMC2209 UART configuration (StealthChop, current, stall detect)
**DONE**
- File: `firmware/src/tmc_config.cpp:42-71` -- `configureTMCDriver()` sets current, microstepping, StealthChop, PWM autoscale
- File: `firmware/src/tmc_config.cpp:186-205` -- `enableStallDetection()` with threshold

### REQ-038: [Stepper] Backlash compensation
**DONE**
- File: `firmware/src/stepper_control.cpp:111-125` -- `queueRelativeMove()` applies backlash compensation on direction reversal
- File: `firmware/src/stepper_control.cpp:208-211` -- `setBacklashCompensation()` public API

### REQ-039: [Stepper] Sensorless homing via stall detection
**DONE**
- File: `firmware/src/stepper_control.cpp:240-264` -- `performSensorlessHome()` with timeout, stall check, position reset

### REQ-040: [Temp] PID temperature control with auto-tune
**DONE**
- File: `firmware/src/temperature.cpp:26` -- PID_v1 library
- File: `firmware/src/temperature_autotune.cpp` -- Full relay-based auto-tune with Ziegler-Nichols tuning
- File: `firmware/src/temperature.cpp:258-263` -- `setPidTunings()` for manual PID configuration

### REQ-041: [Temp] Material profiles: PLA 210C, PETG 235C, ABS 250C
**DONE**
- File: `firmware/src/temperature.cpp:14-18` -- `kProfiles[]` with PLA 210C, PETG 235C, ABS 250C
- File: `firmware/src/config.h:152-154` -- Weld temps matching profiles

### REQ-042: [Temp] Thermal runaway detection (10C rise in 40s window)
**DONE**
- File: `firmware/src/config.h:179-180` -- `THERMAL_RUNAWAY_PERIOD_MS 40000UL`, `THERMAL_RUNAWAY_MIN_RISE_C 10.0f`
- File: `firmware/src/temperature.cpp:89-102` -- `checkThermalRunaway()` implementation

### REQ-043: [Temp] Thermistor disconnect detection (-10C to 350C range)
**DONE**
- File: `firmware/src/config.h:182-183` -- `THERMISTOR_DISCONNECT_LOW_C -10.0f`, `THERMISTOR_DISCONNECT_HIGH_C 350.0f`
- File: `firmware/src/temperature.cpp:76-77` -- `isThermistorValid()` range check
- File: `firmware/src/temperature.cpp:185` -- Calls `enterFault("THERMISTOR")` on disconnect

### REQ-044: [Temp] Cold extrusion prevention (block below 170C)
**PARTIAL**
- File: `firmware/src/config.h:184` -- `COLD_EXTRUSION_MIN_C 170.0f`
- File: `firmware/src/temperature.cpp:254-256` -- `isColdExtrusionBlocked()` function implemented
- **Missing:** The state machine does not actually check `isColdExtrusionBlocked()` before feeding filament. The function exists but is never called in `handleFeedingA()` or `handleFeedingB()`. Motors will run at any temperature.

### REQ-045: [Temp] PID watchdog (2s loop timeout)
**DONE**
- File: `firmware/src/config.h:186` -- `PID_WATCHDOG_MS 2000UL`
- File: `firmware/src/temperature.cpp:198-199` -- Watchdog check triggers `enterFault("PID_WATCHDOG")`

### REQ-046: [Temp] Heating stages: OFF, PREHEAT, SOAK, READY, FAULT
**DONE**
- File: `firmware/src/temperature.h:18-24` -- `HeatingStage` enum with all 5 stages
- File: `firmware/src/temperature.cpp:103-143` -- `updateHeatingStage()` state machine

### REQ-047: [Encoder] Quadrature encoder with ISR-driven counting
**DONE**
- File: `firmware/src/encoder_system.cpp:155-183` -- ISR handler with quadrature decoding, debounce
- File: `firmware/src/encoder_system.cpp:193-194` -- `attachInterrupt()` on both channels

### REQ-048: [Encoder] Slip detection (2mm threshold, 16-sample window)
**DONE**
- File: `firmware/src/config.h:85` -- `ENCODER_SLIP_THRESHOLD_MM 2.0f`
- File: `firmware/src/encoder_system.cpp:8` -- `kSlipWindowSize = 16`
- File: `firmware/src/encoder_system.cpp:212-215` -- Slip detection comparing motor position to encoder position

### REQ-049: [Encoder] Closed-loop correction (0.25 gain, 0.35mm max, 120ms interval)
**DONE**
- File: `firmware/src/config.h:87-89` -- `ENCODER_CORRECTION_GAIN 0.25f`, `ENCODER_CORRECTION_MAX_MM 0.35f`, `ENCODER_CORRECTION_INTERVAL_MS 120UL`
- File: `firmware/src/encoder_system.cpp:95-122` -- `applyClosedLoopCorrection()` with deadband, gain, and max clamping

### REQ-050: [Encoder] EEPROM calibration storage with checksum
**DONE**
- File: `firmware/src/encoder_system.cpp:11-16` -- `PersistentCalibration` struct with signature and checksum
- File: `firmware/src/encoder_system.cpp:247-263` -- `saveEncoderCalibration()` and `loadEncoderCalibration()` with checksum validation

### REQ-051: [Encoder] Health monitoring (stale threshold 1.5s)
**DONE**
- File: `firmware/src/config.h:91` -- `ENCODER_HEALTH_STALE_MS 1500UL`
- File: `firmware/src/encoder_system.cpp:123-136` -- `updateHealth()` with signal quality and stale detection

### REQ-052: [Cutter] Servo-based cutting system (open/closed angles)
**DONE**
- File: `firmware/src/config.h:164-165` -- `CUTTER_SERVO_OPEN_ANGLE 0`, `CUTTER_SERVO_CLOSED_ANGLE 90`
- File: `firmware/src/cutting_system.cpp` -- Full multi-phase cut cycle with servo control

### REQ-053: [Cutter] Cut verification and blade wear tracking
**DONE**
- File: `firmware/src/cutting_system.cpp:114-135` -- Verification phase with force reading
- File: `firmware/src/cutting_system.cpp:52-69` -- `finishCut()` tracks success/failure/force/maintenance due

### REQ-054: [Cutter] EEPROM persistence for maintenance counters
**DONE**
- File: `firmware/src/cutting_system.cpp:173-195` -- `saveCutStatistics()` and `loadCutStatistics()` with signature and checksum

### REQ-055: [Error] Error codes for thermal, motor, filament, cutter, recipe, serial
**DONE**
- File: `firmware/src/error_handler.h:13-43` -- `ErrorCode` enum covering all categories (thermal 10-12, motor 20-22, filament 30-32, cutter 40, recipe 50-51, serial 60, emergency 99)

### REQ-056: [Error] Recovery actions: RETRY_ONCE, RETRY_AFTER_COOL, MANUAL_REQUIRED, ABORT, RESET
**DONE**
- File: `firmware/src/error_handler.h:46-53` -- `RecoveryAction` enum with all 5 actions + NONE

### REQ-057: [Error] Error recovery state machine
**DONE**
- File: `firmware/src/error_recovery.h:15-23` -- `RecoveryPhase` enum: IDLE, ASSESSING, COOLDOWN_WAIT, RETRYING, AWAITING_USER, RESOLVED, UNRECOVERABLE
- File: `firmware/src/error_recovery.cpp:140-210` -- Full update loop with phase handlers

### REQ-058: [Error] Emergency shutdown (disable all outputs)
**DONE**
- File: `firmware/src/error_handler.cpp:126-136` -- `emergencyShutdown()` disables heaters, enables cooling fan, disables motors

---

## Safety Requirements (REQ-059 through REQ-062)

### REQ-059: [Safety] MAX_TEMP emergency shutoff at 280C
**DONE**
- File: `firmware/src/config.h:176` -- `MAX_TEMP 280`
- File: `firmware/src/temperature.cpp:186` -- `if (st.currentC > static_cast<float>(MAX_TEMP)) { enterFault("OVERTEMP"); }`

### REQ-060: [Safety] Heater timeout at 120s
**DONE**
- File: `firmware/src/config.h:178` -- `HEATER_TIMEOUT_MS 120000`
- File: `firmware/src/state_machine.cpp:293-301` -- Timeout check in `handleHeating()`

### REQ-061: [Safety] Cooling fan auto-enable on fault
**DONE**
- File: `firmware/src/temperature.cpp:84` -- `digitalWrite(COOLING_FAN_PIN, HIGH)` in `enterFault()`
- File: `firmware/src/error_handler.cpp:147-148` -- Cooling fan enabled in `disableHeaters()`
- File: `firmware/src/state_machine.cpp:192` -- `setCoolingFan(true)` in `handleError()`

### REQ-062: [Safety] Emergency stop via ABORT command
**DONE**
- File: `firmware/src/state_machine.cpp:153-163` -- `abort()` stops motors, disables heater, enables cooling fan
- File: `firmware/src/serial_handler.cpp:104` -- ABORT command dispatched

---

## Hardware Validation Specs (REQ-063 through REQ-082)

### REQ-063 through REQ-082: Hardware validation modules
**DONE** (all 20 requirements)
- Each F-module has:
  1. A firmware implementation in `firmware/src/` (e.g., `motor_control_validation` maps to motor control code)
  2. A Python validation module in `postprocessor/` (e.g., `mechanical_validation.py`, `electronics_validation.py`, etc.)
  3. A test file in `postprocessor/tests/` (e.g., `test_mechanical_validation.py`)
  4. A spec directory under `hardware/f*_*/spec/`
- The validation modules are NOT stubs; they contain real validation logic (e.g., `mechanical_validation.py` has `validate_filament_path()`, `validate_printable_bed_fit()`, `validate_station_layout()`, `validate_interfaces()`).
- The firmware modules for F9/F10 features (wifi_manager, web_dashboard, ota_updater, etc.) ARE stubs. See GAP-1 below.

---

## Integration & Infrastructure (REQ-083 through REQ-086)

### REQ-083: [MQTT] Home Assistant MQTT bridge service
**DONE**
- File: `services/mqtt_bridge.py` -- Full implementation with serial/MQTT bridging, topic configuration, threading

### REQ-084: [Docker] Docker/docker-compose for deployment
**DONE**
- File: `Dockerfile` -- Python 3.11 slim, copies postprocessor/cli/samples
- File: `docker-compose.yml` -- Services for postprocessor, simulator, and test

### REQ-085: [CI] pytest/coverage in CI pipeline
**PARTIAL**
- File: `pyproject.toml:65-68` -- pytest configuration with testpaths and patterns
- File: `codecov.yml` -- Codecov integration configured
- **Missing:** No `.github/workflows/` directory found. No GitHub Actions CI pipeline definition exists. The codecov.yml references coverage but there is no CI workflow to actually run the tests and generate coverage reports.

### REQ-086: [Render] render.yaml for cloud deployment
**DONE**
- File: `render.yaml` -- Static site (splice3d-site) and API server (splice3d-api) configured

---

## Code Quality (REQ-087 through REQ-091)

### REQ-087: [Quality] 80%+ test coverage across all metrics
**PARTIAL**
- The project claims 95% postprocessor coverage but there is no CI to verify.
- 585 tests exist in `postprocessor/tests/` with comprehensive test files for every module.
- **Missing:** No coverage enforcement in CI. `codecov.yml` target is set to `auto` not `80%` for project status.
- Firmware has zero automated test coverage (embedded C++ with no unit test framework configured).

### REQ-088: [Quality] Zero lint errors
**PARTIAL**
- `pyproject.toml` includes `black`, `flake8`, `isort` in dev dependencies
- **Missing:** No pre-commit hooks or CI step to enforce linting. No evidence of linting being run.

### REQ-089: [Quality] All Python files compile without errors
**PARTIAL**
- Core files use relative imports (e.g., `from gcode_parser import ...`) which work when running from the postprocessor directory but break with standard package imports.
- `pyproject.toml:42` defines entry point as `postprocessor.splice3d_postprocessor:main` but the file uses `from gcode_parser import GCodeParser` (relative) instead of `from postprocessor.gcode_parser import GCodeParser` (package-qualified).

### REQ-090: [Quality] No hardcoded user paths in committed code
**DONE**
- Grep for `/Users/` across the codebase found no hardcoded user paths in committed code.

### REQ-091: [Quality] No hardcoded secrets in committed code
**DONE**
- No API keys, passwords, or credentials found in committed code.

---

## Firmware Issues from RIP Review (REQ-092 through REQ-100)

### REQ-092: [FW-Fix] H1: Serial buffer size matches config (256 vs 512 mismatch)
**BROKEN** (not fixed)
- File: `firmware/src/serial_handler.h:38` -- `char _buffer[256]`
- File: `firmware/src/config.h:23` -- `SERIAL_BUFFER_SIZE 512`
- The buffer is hardcoded at 256, not using the config constant `SERIAL_BUFFER_SIZE`.

### REQ-093: [FW-Fix] H2: JSON parsing validates bounds and input
**BROKEN** (not fixed)
- File: `firmware/src/serial_handler.cpp:126-178` -- `handleRecipe()`:
  - Uses `atoi()`/`atof()` with no validation on parsed values
  - No check for negative `length_mm` values
  - No check for `colorIndex` being within valid range
  - `SpliceSegment segments[MAX_SEGMENTS]` (500 * 6 bytes = 3KB) allocated on the stack, which is dangerous on embedded (typical STM32F103 stack is 2-8KB)
  - No check for malformed JSON (missing closing brackets, etc.)

### REQ-094: [FW-Fix] H3: TMC2209 init validates communication success
**PARTIAL**
- File: `firmware/src/tmc_config.cpp:35-39` -- `checkDriverStatus()` is called after init
- It tests connection with `test_connection()` and prints errors
- **Missing:** On failure, it prints `"WARNING: Driver communication issue"` but does NOT halt initialization or set an error state. The machine continues to operate with potentially unconfigured drivers. No retry logic.

### REQ-095: [FW-Fix] H4: Auto-tune guards against division by zero
**BROKEN** (not fixed)
- File: `firmware/src/temperature_autotune.cpp:49-51`:
  ```cpp
  const float amplitude = (atState.peakHigh - atState.peakLow) / 2.0f;
  const float ku = ... / (3.14159f * amplitude);  // Division by zero if amplitude == 0
  const float tu = static_cast<float>(period) / 1000.0f;  // Used in division below
  ```
  Line 53: `atState.computedKi = 1.2f * ku / tu;` -- Division by zero if `tu == 0` (period == 0)
- No guard against `amplitude == 0` (peakHigh == peakLow) or `period == 0`.

### REQ-096: [FW-Fix] H5: Unified error state machine
**DONE**
- File: `firmware/src/error_recovery.h` -- `RecoveryPhase` enum with 7 states
- File: `firmware/src/error_recovery.cpp` -- Full recovery engine with statistics, phase handlers, and configuration
- The error_handler.h + error_recovery.h form a unified two-layer system: error_handler detects and classifies, error_recovery manages the recovery process.

### REQ-097: [FW-Fix] H6: No static variables in state handlers
**BROKEN** (not fixed)
- File: `firmware/src/state_machine.cpp` -- 9 state handlers use `static bool` local variables:
  - Line 217: `handleFeedingA()` - `static bool feedStarted`
  - Line 237: `handleFeedingB()` - `static bool feedStarted`
  - Line 255: `handleCutting()` - `static bool cutStarted`
  - Line 271: `handlePositioning()` - `static bool positionStarted`
  - Line 288: `handleHeating()` - `static bool heatingStarted`
  - Line 313: `handleWelding()` - `static bool weldStarted`
  - Line 329: `handleCooling()` - `static bool coolingStarted`
  - Line 351: `handleSpooling()` - `static bool spoolingStarted`
  - Line 392: `handleComplete()` - `static bool completionReported`
- These should be instance variables reset in `transitionTo()`.

### REQ-098: [FW-Fix] H7: millis() rollover-safe timeout patterns
**BROKEN** (not fixed)
- File: `firmware/src/state_machine.cpp:293` -- `_heaterTimeout = millis() + HEATER_TIMEOUT_MS;`
- File: `firmware/src/state_machine.cpp:298` -- `if (millis() > _heaterTimeout)` -- NOT rollover-safe
- The correct pattern is `if (millis() - startTime >= timeout)` which handles 32-bit unsigned overflow. The current pattern will fail after ~49.7 days of uptime.
- Other files (cutting_system.cpp, error_recovery.cpp, encoder_system.cpp) use the correct `millis() - startTime` pattern, so this is inconsistent.

### REQ-099: [FW-Fix] H8: Watchdog timer enabled
**MISSING**
- No hardware watchdog timer (WDT) initialization found anywhere in the codebase.
- The PID watchdog at `temperature.cpp:198` is a software-level loop timing check, NOT a hardware watchdog.
- No `IWDG` or `WWDG` STM32 peripheral initialization exists.
- If the main loop hangs (infinite loop, hard fault), nothing will reset the MCU.

### REQ-100: [FW-Fix] M1-M14: Medium severity firmware issues
**PARTIAL**
- This is a catch-all for 14 medium-severity issues. Based on code review:
  - Some issues appear addressed (e.g., error handler has proper error codes, recovery engine exists)
  - Many issues cannot be fully verified without the original M1-M14 list being itemized
  - The stepper_compat.cpp provides clean legacy wrappers, suggesting some refactoring was done
  - LCD display module exists (`lcd_display.cpp/h`) but was not audited in detail

---

## NEW GAPS NOT IN INVENTORY

### GAP-1: F9/F10 Firmware Modules Are Empty Stubs
**SEVERITY: HIGH**
The following firmware modules have no actual functionality; they initialize, print a log line, and do nothing in their update loops:
- `firmware/src/wifi_manager.cpp` -- `updateWifiManager()` is empty
- `firmware/src/web_dashboard.cpp` -- `updateWebDashboard()` is empty
- `firmware/src/ota_updater.cpp` -- `updateOtaUpdater()` is empty
- `firmware/src/notification_manager.cpp` -- likely empty (pattern matches others)
- `firmware/src/print_farm.cpp` -- likely empty
- `firmware/src/mfg_ready.cpp` -- likely empty

These modules are compiled, initialized in `main.cpp:97-100`, and called every loop iteration (adding overhead), but perform no work. The corresponding Python validation modules DO contain real validation logic, but they validate specs, not actual firmware behavior.

### GAP-2: No CI/CD Pipeline Exists
**SEVERITY: HIGH**
No `.github/workflows/` directory or CI configuration file exists. Despite having:
- 585 test files
- codecov.yml
- pytest configured in pyproject.toml
There is no automated mechanism to run tests on push/PR. All test enforcement is manual.

### GAP-3: Cold Extrusion Prevention Not Enforced in State Machine
**SEVERITY: MEDIUM**
`isColdExtrusionBlocked()` is implemented in `temperature.cpp:254-256` but never called by the state machine's `handleFeedingA()` or `handleFeedingB()`. The machine will happily try to feed filament through the weld chamber at room temperature, which could jam the mechanism.

### GAP-4: Main Loop Has 30+ Update Calls With No Priority/Throttling
**SEVERITY: MEDIUM**
`firmware/src/main.cpp:109-225` calls `update*()` on 30+ subsystems every single loop iteration. On an STM32F103 at 72MHz with 48KB RAM:
- Many of these are empty stubs (GAP-1) adding function call overhead
- No priority system: encoder ISR timing-critical updates run at the same priority as empty wifi_manager updates
- No throttling: modules like `updateMaterialDatabase()` or `updateProfileValidator()` that only need periodic checks run every loop
- Combined with the 3KB stack allocation in recipe parsing (REQ-093), memory pressure is a concern

### GAP-5: Inconsistent Import Paths Break Package Installation
**SEVERITY: MEDIUM**
`postprocessor/splice3d_postprocessor.py:23-25` uses bare imports:
```python
from gcode_parser import GCodeParser, parse_gcode
from recipe_generator import RecipeGenerator, generate_recipe
from gcode_modifier import GCodeModifier, modify_gcode
```
But `pyproject.toml:42` defines the entry point as `postprocessor.splice3d_postprocessor:main`. Running `pip install -e .` and then `splice3d` will fail because the bare imports require being in the `postprocessor/` directory. Similarly, `recipe_generator.py:10` imports `from gcode_parser import ParseResult, Segment` without the package prefix.

### GAP-6: M600 Handler Limited to 2-Color Toggle
**SEVERITY: LOW**
`gcode_parser.py:157` -- `self.current_tool = (self.current_tool + 1) % 2` hardcodes a 2-color assumption for M600. While M600 is traditionally a single-filament-change command, some slicers (Cura) use sequential M600 commands for multi-color (3+) prints. The current implementation would cycle between colors 0 and 1 only, silently ignoring the 3rd+ colors.

### GAP-7: Recipe JSON Parsing Stack Overflow Risk on Firmware
**SEVERITY: HIGH**
`firmware/src/serial_handler.cpp:128` -- `SpliceSegment segments[MAX_SEGMENTS]` allocates `500 * sizeof(SpliceSegment)` on the stack. With `MAX_SEGMENTS = 500`, and each segment being at least 5 bytes (1 byte color + 4 byte float), that's 2.5-3KB on the stack. STM32F103 has 48KB RAM total, but with all the other static allocations (30+ module state structs, AccelStepper instances, PID state, etc.), the available stack is likely 2-4KB. This allocation alone could cause a stack overflow, which would manifest as random crashes or data corruption.

---

## Overall Assessment

The post-processor module (Python) is well-implemented with comprehensive tests and clean architecture. REQ-001 through REQ-022 are essentially complete.

The firmware core (C++) has solid implementations for the primary subsystems (stepper control, temperature, encoder, cutting, error handling), but carries several unresolved issues from the original RIP review (REQ-092, 093, 095, 097, 098 still broken). The most dangerous are the division-by-zero in auto-tune (REQ-095), the static variables in state handlers (REQ-097), and the stack overflow risk in recipe parsing (GAP-7).

The F9/F10 firmware modules (WiFi, web dashboard, OTA, print farm, manufacturing readiness) are stubs that compile and initialize but do nothing (GAP-1). The corresponding Python validation modules validate specs, not actual firmware functionality.

Infrastructure is incomplete: no CI pipeline exists (GAP-2) despite having test tooling configured.
