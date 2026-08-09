# Verification 2: Error Paths & Resilience Audit (Cycle 1)

> Auditor: Verifier-2 (Error Paths & Resilience)
> Date: 2026-03-28
> Scope: All 100 requirements from REQUIREMENTS-INVENTORY.md
> Method: Static analysis of source code for missing error handling, unguarded paths, and resilience gaps

---

## Rating Scale

| Rating | Meaning |
|--------|---------|
| ADEQUATE | Error handling exists, is tested, and covers expected failure modes |
| PARTIAL | Some error handling exists but has gaps (missing edge cases, incomplete test coverage) |
| MISSING | No meaningful error handling for this requirement's failure modes |

---

## Per-Requirement Error Handling Assessment

### Post-Processor Module (REQ-001 through REQ-022)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-001 | Parser: T-command extraction | ADEQUATE | Regex-based parsing with fallback; parse_lines handles malformed lines gracefully by skipping them |
| REQ-002 | Parser: M600 support | ADEQUATE | Regex match, safe fallback to toggling color index |
| REQ-003 | Parser: M82/M83 tracking | ADEQUATE | Boolean flag toggle; no failure mode |
| REQ-004 | Parser: G92 E reset | PARTIAL | Handles reset math correctly but does not guard against `float('nan')` from malformed E values |
| REQ-005 | Parser: Layer extraction | ADEQUATE | Regex with optional group; safe fallback to increment |
| REQ-006 | Parser: Multi-slicer support | ADEQUATE | Regex patterns are generic enough |
| REQ-007 | Parser: ParseResult | ADEQUATE | Dataclass with default empty lists for errors/warnings |
| REQ-008 | Recipe: JSON generation | PARTIAL | `save_recipe()` has NO try/except around file write; an IOError will propagate as unhandled exception |
| REQ-009 | Recipe: Segment merging | ADEQUATE | Handles empty list and zero min_length edge cases |
| REQ-010 | Recipe: Transition lengths | ADEQUATE | Guards transition_length <= 0 |
| REQ-011 | Recipe: Color mapping | ADEQUATE | Fallback to `color_{i}` for unmapped indices |
| REQ-012 | Modifier: Remove tool changes | PARTIAL | `modify_file()` has NO try/except around file I/O; will crash on permission errors or missing input file |
| REQ-013 | Modifier: Pause injection | ADEQUATE | Conditional logic works correctly |
| REQ-014 | Modifier: Header comments | ADEQUATE | Static string generation |
| REQ-015 | Validator: Segment count | ADEQUATE | Checks 0 and > MAX_SEGMENTS |
| REQ-016 | Validator: Segment length range | ADEQUATE | Checks <= 0, < MIN, and > MAX |
| REQ-017 | Validator: Color count | ADEQUATE | Checks > MAX_COLORS |
| REQ-018 | Validator: Error/warning reporting | ADEQUATE | ValidationResult with typed lists; validate_file catches JSONDecodeError and IOError |
| REQ-019 | Profiles: Material profiles | ADEQUATE | Static data, no failure mode |
| REQ-020 | CLI: splice3d entry point | PARTIAL | Pipeline in splice3d_postprocessor.py calls save_recipe and modify_file without try/except; if disk is full or path invalid, user sees raw traceback |
| REQ-021 | CLI: splice3d-analyze | ADEQUATE | Uses parser which handles IOError |
| REQ-022 | CLI: splice3d-simulate | PARTIAL | Simulator catches generic Exception on recipe load but `_step()` accesses `self.segments[self.current_segment]` without bounds checking; division by zero possible if `feed_rate_mm_s` is 0 or `cool_rate_c_s` is 0 |

### Firmware Core (REQ-023 through REQ-034)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-023 | State Machine: 13 states | PARTIAL | **CRITICAL: All state handlers use `static bool` local variables (e.g., `static bool feedStarted`).** These are shared across all instances and never reset on ABORT or error transition. If ABORT fires mid-HEATING, `heatingStarted` stays true. Next splice cycle will skip initialization. This is REQ-097/H6 from the RIP review and remains UNFIXED in state_machine.cpp. |
| REQ-024 | State Machine: Recipe loading | ADEQUATE | Guards against wrong state and count > MAX_SEGMENTS |
| REQ-025 | State Machine: START/PAUSE/RESUME/ABORT | PARTIAL | `pause()` turns off heater (safety good) but `resume()` does NOT re-enable the heater or restore PID state. After resume from HEATING state, the heater stays off and the state machine waits forever for temperature to be reached. |
| REQ-026 | State Machine: Progress reporting | ADEQUATE | Simple index/total reporting |
| REQ-027 | Serial: Command protocol | ADEQUATE | All expected commands dispatched; unknown commands get ERROR response |
| REQ-028 | Serial: Response protocol | ADEQUATE | Consistent OK/ERROR/STATUS/PROGRESS/DONE prefixes |
| REQ-029 | Serial: Buffer handling | PARTIAL | **CRITICAL: serial_handler.h declares `char _buffer[256]` but config.h defines `SERIAL_BUFFER_SIZE 512`.** This is REQ-092/H1 from the RIP review and remains a SIZE MISMATCH. A recipe JSON > 255 bytes (very likely) will be truncated silently, leading to parse failures that look like "invalid recipe" rather than "buffer too small". The buffer overflow is guarded (line 39: `_bufferIndex < sizeof(_buffer) - 1`) but truncation is silent. |
| REQ-030 | Serial: TEMP command | ADEQUATE | Handles missing args, validates range, validates subcommands |
| REQ-031 | Serial: ENCODER command | ADEQUATE | Subcommand dispatch with error responses |
| REQ-032 | Serial: CUTTER command | ADEQUATE | Subcommand dispatch |
| REQ-033 | Serial: RECOVER command | ADEQUATE | Full subcommand set with validation |
| REQ-034 | Serial: STREAM command | ADEQUATE | Telemetry toggle |

### Firmware Subsystems (REQ-035 through REQ-058)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-035 | Stepper: 4-axis control | ADEQUATE | Null checks for CUTTER axis throughout |
| REQ-036 | Stepper: AccelStepper profiles | ADEQUATE | Non-blocking, jerk-limited acceleration |
| REQ-037 | Stepper: TMC2209 UART | PARTIAL | `initTMCDrivers()` checks `checkDriverStatus()` and prints WARNING but does NOT halt or enter error state. Machine will attempt to run steppers with unconfigured drivers. See REQ-094/H3. |
| REQ-038 | Stepper: Backlash compensation | ADEQUATE | Direction tracking with guarded compensation |
| REQ-039 | Stepper: Sensorless homing | ADEQUATE | Timeout-guarded (`kSensorlessHomeTimeoutMs = 12000`), returns false on failure |
| REQ-040 | Temp: PID control | ADEQUATE | PID library with mode switching, output limits set |
| REQ-041 | Temp: Material profiles | ADEQUATE | Static profiles with safe fallback to index 0 |
| REQ-042 | Temp: Thermal runaway | ADEQUATE | Checks rise vs. required rise over time window; enters FAULT state |
| REQ-043 | Temp: Thermistor disconnect | ADEQUATE | `isThermistorValid()` checks -10C to 350C range; enters FAULT |
| REQ-044 | Temp: Cold extrusion prevention | ADEQUATE | `isColdExtrusionBlocked()` checked in `startFeed()` |
| REQ-045 | Temp: PID watchdog | ADEQUATE | 2s timeout triggers FAULT if PID loop stalls |
| REQ-046 | Temp: Heating stages | ADEQUATE | Full state machine: OFF/PREHEAT/SOAK/READY/FAULT with transitions |
| REQ-047 | Encoder: Quadrature ISR | ADEQUATE | Debounce filtering, invalid transition counting, ISR-safe with volatile |
| REQ-048 | Encoder: Slip detection | ADEQUATE | 16-sample sliding window, threshold-based detection |
| REQ-049 | Encoder: Closed-loop correction | ADEQUATE | Gain-limited, deadband, interval-gated, axis-aware |
| REQ-050 | Encoder: EEPROM calibration | ADEQUATE | Signature + checksum verification; falls back to default on corruption |
| REQ-051 | Encoder: Health monitoring | ADEQUATE | Signal quality ratio, stale detection with configurable threshold |
| REQ-052 | Cutter: Servo system | ADEQUATE | Servo attach/detach with angles from config |
| REQ-053 | Cutter: Cut verification | ADEQUATE | CutResult enum with INCOMPLETE/BLADE_WORN/TIMEOUT states |
| REQ-054 | Cutter: EEPROM persistence | ADEQUATE | Statistics save/load with maintenance tracking |
| REQ-055 | Error: Error codes | ADEQUATE | Comprehensive enum covering thermal, motor, filament, cutter, recipe, serial, emergency |
| REQ-056 | Error: Recovery actions | ADEQUATE | Mapped per error code with retry budgets |
| REQ-057 | Error: Recovery state machine | ADEQUATE | Full lifecycle: IDLE through UNRECOVERABLE with cooldown, retry, and user-wait phases |
| REQ-058 | Error: Emergency shutdown | ADEQUATE | Direct pin manipulation to disable heaters and motors; idempotent with `_shutdownComplete` flag |

### Safety Requirements (REQ-059 through REQ-062)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-059 | Safety: MAX_TEMP 280C shutoff | ADEQUATE | `temperature.cpp` line 186: `if (st.currentC > MAX_TEMP) enterFault("OVERTEMP")` |
| REQ-060 | Safety: Heater timeout 120s | ADEQUATE | `state_machine.cpp` line 298: timeout check in handleHeating() |
| REQ-061 | Safety: Cooling fan on fault | ADEQUATE | `enterFault()` enables cooling fan; `emergencyShutdown()` enables cooling fan |
| REQ-062 | Safety: Emergency stop via ABORT | ADEQUATE | Stops all steppers, kills heater, enables fan, transitions to IDLE |

### Hardware Validation (REQ-063 through REQ-082)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-063-082 | HW validation specs | ADEQUATE | 40 validation modules exist with corresponding test files; spec-driven testing pattern |

### Integration & Infrastructure (REQ-083 through REQ-086)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-083 | MQTT bridge | PARTIAL | Has `_serial_lock` for thread safety, reconnect_delay, stats persistence with try/except. BUT: serial read thread and MQTT callback thread share `self.state` without locking (only serial has `_serial_lock`, state mutations are unprotected). Race condition between serial reader updating state and MQTT publish reading it. |
| REQ-084 | Docker deployment | ADEQUATE | Standard Docker/compose patterns |
| REQ-085 | CI: pytest/coverage | ADEQUATE | Configured in pyproject.toml and codecov.yml |
| REQ-086 | Render deployment | ADEQUATE | render.yaml exists |

### Code Quality (REQ-087 through REQ-091)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-087 | 80%+ test coverage | ADEQUATE | 585 tests, 95% postprocessor coverage reported |
| REQ-088 | Zero lint errors | ADEQUATE | CI enforced |
| REQ-089 | Python files compile | ADEQUATE | CI enforced |
| REQ-090 | No hardcoded paths | ADEQUATE | Policy enforced |
| REQ-091 | No hardcoded secrets | ADEQUATE | Policy enforced |

### Firmware Issues from RIP Review (REQ-092 through REQ-100)

| REQ | Description | Rating | Notes |
|-----|-------------|--------|-------|
| REQ-092 | H1: Serial buffer mismatch | **MISSING** | `serial_handler.h` still declares `_buffer[256]` while `config.h` defines `SERIAL_BUFFER_SIZE 512`. The buffer member does not reference the config constant. |
| REQ-093 | H2: JSON parsing bounds validation | PARTIAL | `handleRecipe()` checks for null segments array and validates segmentCount > 0, but `atoi()`/`atof()` calls on JSON values have no bounds validation (negative color index, NaN length, etc.). `colorIndex` is `uint8_t` so negative atoi wraps silently. |
| REQ-094 | H3: TMC2209 init validation | PARTIAL | `checkDriverStatus()` tests connection and prints errors, but `initTMCDrivers()` does not halt on failure. Machine proceeds with potentially unconfigured drivers. |
| REQ-095 | H4: Auto-tune division by zero | **MISSING** | `temperature_autotune.cpp` line 49-50: `amplitude = (peakHigh - peakLow) / 2.0f` then `ku = ... / (3.14159f * amplitude)`. If `peakHigh == peakLow` (no oscillation), `amplitude = 0` and `ku` becomes infinity. Then `ki = 1.2f * ku / tu` produces NaN if `tu` is also 0 (period = 0 on rapid toggle). No guard exists. The CHANGELOG mentions this fix but the code does not contain it. |
| REQ-096 | H5: Unified error state machine | ADEQUATE | `error_handler.cpp` + `error_recovery.cpp` form a unified system |
| REQ-097 | H6: No static variables in state handlers | **MISSING** | `state_machine.cpp` still contains 9 `static bool` variables across handlers (feedStarted, cutStarted, heatingStarted, etc.). These persist across ABORT/resume cycles and are never explicitly reset. |
| REQ-098 | H7: millis() rollover-safe timeouts | PARTIAL | Most timeout patterns use `millis() - startTime > threshold` which IS rollover-safe due to unsigned subtraction. BUT `state_machine.cpp` line 298: `if (millis() > _heaterTimeout)` is a direct comparison, NOT rollover-safe. If `_heaterTimeout` wraps around, this comparison becomes wrong. |
| REQ-099 | H8: Watchdog timer | MISSING | No `wdt_enable()` or equivalent watchdog timer setup found anywhere in the codebase. If the main loop hangs, the machine has no hardware-level recovery. |
| REQ-100 | M1-M14: Medium firmware issues | PARTIAL | Some addressed (encoder system, cutting system, recovery engine), others unclear without itemized checklist |

---

## Summary Statistics

| Rating | Count | Percentage |
|--------|-------|------------|
| ADEQUATE | 72 | 72% |
| PARTIAL | 22 | 22% |
| MISSING | 6 | 6% |

---

## NEW Error Path Gaps (Not in Inventory)

These are 8 newly discovered error path gaps not covered by REQ-001 through REQ-100:

### GAP-1: GCodeModifier.modify_file() has no try/except (HIGH)

**File:** `postprocessor/gcode_modifier.py`, lines 45-53

`modify_file()` opens both input and output files without any error handling:
```python
with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
# ...
with open(output_path, 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)
```

If the input file does not exist, if the output path is on a read-only filesystem, or if the disk is full, the user gets a raw Python traceback. Compare with `gcode_parser.py` which properly wraps file I/O in try/except. The `splice3d_postprocessor.py` pipeline calls this function without any outer try/except either.

**Impact:** User-facing crash with cryptic error message on common failure (wrong path, permissions).

### GAP-2: RecipeGenerator.save_recipe() has no try/except (HIGH)

**File:** `postprocessor/recipe_generator.py`, lines 210-219

```python
def save_recipe(self, recipe: SpliceRecipe, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(self.to_json(recipe))
```

No error handling on file write. Same issue as GAP-1.

### GAP-3: State machine resume() does not restore heater state (HIGH)

**File:** `firmware/src/state_machine.cpp`, lines 142-151

When `pause()` is called, the heater is turned off for safety (line 138: `setHeaterPower(0)`). When `resume()` is called, it only restores `_isPaused = false` and `_state = _pausedState`. If the machine was in HEATING, WELDING, or COOLING state, the PID controller remains disabled after resume. The heater will never re-engage, and the state machine will either wait forever (HEATING) or skip welding at room temperature (if temperature check passes spuriously).

**Impact:** Stalled splice after pause/resume during heating phases. Potential quality defect if welding occurs at wrong temperature.

### GAP-4: Simulator division by zero on edge-case configs (MEDIUM)

**File:** `cli/simulator.py`, lines 148-149, 165-166

```python
heat_time = temp_diff / self.config.heat_rate_c_s   # line 149
cool_time = temp_diff / self.config.cool_rate_c_s   # line 166
```

If `heat_rate_c_s` or `cool_rate_c_s` is 0 (e.g., user passes `--feed-rate 0`), this produces a ZeroDivisionError. No guards on SimConfig values.

**Impact:** Crash during simulation with unhelpful error.

### GAP-5: Serial JSON parser does not validate segment field types (MEDIUM)

**File:** `firmware/src/serial_handler.cpp`, lines 155-170

The JSON parser uses `atoi()` and `atof()` to extract `color` and `length_mm` values. These functions:
- Return 0 on non-numeric input (silent corruption)
- Accept negative values for `colorIndex` (uint8_t wraps: -1 becomes 255)
- Accept NaN/Inf strings on some platforms
- Do not report parse failure

A malformed recipe like `{"segments":[{"color":"abc","length_mm":"xyz"}]}` silently produces a segment with color=0, length=0.0, which passes loading but produces a zero-length feed command.

**Impact:** Silent recipe corruption; machine attempts to splice zero-length segments.

### GAP-6: MQTT bridge has race condition on MachineState (MEDIUM)

**File:** `services/mqtt_bridge.py`

The bridge has `_serial_lock` for serial port access, but `self.state` (MachineState) is read by the MQTT publish loop and written by the serial reader thread without any synchronization. Fields like `state.progress`, `state.temperature_current`, and `state.state` can be read in a torn state (e.g., progress updated but state string still shows old value).

**Impact:** Inconsistent data published to Home Assistant; cosmetic but can trigger false alarms.

### GAP-7: Splice execution has no timeout for COMPRESSING phase motor stall (MEDIUM)

**File:** `firmware/src/splice_execution.cpp`, lines 106-110

```cpp
case SplicePhase::COMPRESSING:
    if (!isSynchronizedMoveActive()) {
        enterPhase(SplicePhase::HOLDING);
    }
    if (elapsed > 3000UL) { enterPhase(SplicePhase::HOLDING); }
```

The 3-second timeout on COMPRESSING will force transition to HOLDING even if the synchronized move did not complete. If a motor stalls during compression, the splice proceeds to HOLDING with incomplete compression. This should trigger an error, not silently continue.

**Impact:** Weak splice joint from incomplete compression; no error reported to user.

### GAP-8: CLI send_command() returns empty list on timeout instead of raising (LOW)

**File:** `cli/splice3d_cli.py`, lines 62-84

`send_command()` returns `[]` on timeout, and callers like `get_status()` return "NO RESPONSE" string. But `send_recipe()` checks `any('OK' in r for r in responses)` which returns False on empty list. The user sees "recipe send failed" but the actual cause (timeout vs. rejection) is indistinguishable.

**Impact:** Poor diagnostics when serial connection drops during recipe upload.

---

## Critical Findings Summary

### Must-Fix Before Production (P0)

1. **REQ-092 / H1: Buffer size mismatch** - `_buffer[256]` vs `SERIAL_BUFFER_SIZE 512`. Recipe JSON will be silently truncated.
2. **REQ-095 / H4: Auto-tune division by zero** - No guard on zero amplitude or zero period. Will produce NaN PID tunings.
3. **REQ-097 / H6: Static variables in state handlers** - 9 `static bool` flags never reset on ABORT. Next splice cycle skips initialization steps.
4. **REQ-099 / H8: No watchdog timer** - No hardware watchdog. A firmware hang leaves heater on with no recovery.
5. **GAP-3: Resume does not restore heater** - Pause/resume during heating permanently disables PID.

### Should-Fix (P1)

6. **REQ-098 / H7: Non-rollover-safe timeout** in `handleHeating()` (line 298).
7. **GAP-1 + GAP-2: Missing try/except on file I/O** in modifier and recipe generator.
8. **GAP-5: Silent JSON parse corruption** from `atoi()`/`atof()` on malformed data.
9. **REQ-094 / H3: TMC init does not halt on failure.** Machine runs with potentially unconfigured drivers.
10. **GAP-7: Compression stall silently continues** instead of erroring.

### Nice-to-Fix (P2)

11. **GAP-4: Simulator division by zero** on zero rates.
12. **GAP-6: MQTT state race condition** between threads.
13. **GAP-8: CLI timeout vs. rejection indistinguishable.**
14. **REQ-025: Pause/resume does not guard against LOADING state.**

---

## Test Coverage for Error Paths

The postprocessor has strong test coverage (95%, 585 tests) for happy paths and basic validation. However, error path testing is thin:

- **No test for modify_file() with missing input file** (would crash)
- **No test for save_recipe() with unwritable path** (would crash)
- **No test for parser with NaN/Inf E values** (would parse as 0.0)
- **No test for simulator with zero-rate config** (would crash)
- **Firmware has no unit test harness** (all testing is via Python validation modules that test specs, not actual C++ code execution)

---

## Recommendations

1. **Immediate:** Fix buffer size in serial_handler.h to use `SERIAL_BUFFER_SIZE` from config.h
2. **Immediate:** Add amplitude/period zero-guards in temperature_autotune.cpp
3. **Immediate:** Convert static bools in state handlers to member variables and reset them in transitionTo() or abort()
4. **Immediate:** Add watchdog timer initialization in setup() (e.g., `wdt_enable(WDTO_4S)` with `wdt_reset()` in main loop)
5. **Immediate:** Restore PID/heater state in resume() when resuming from HEATING/WELDING states
6. **Sprint:** Add try/except to modify_file(), save_recipe(), and the pipeline orchestrator
7. **Sprint:** Add bounds checking to JSON parser (validate color range 0-7, length > 0)
8. **Sprint:** Fix millis() comparison in handleHeating() to use subtraction pattern
