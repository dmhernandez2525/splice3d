# Consolidated Findings - Cycle 1

> Deduplicated, consensus-counted findings from 4 independent verifiers.
> Only verified, real issues included. Ordered by tier.

---

## Tier A (Critical) - Fix First

### GAP-001: [Tier A] splice3d entry point broken (bare imports)
- **Requirement:** REQ-020
- **Consensus:** 4/4 (V1, V2, V3, V4)
- **Current state:** `postprocessor/splice3d_postprocessor.py:22-24` uses `from gcode_parser import ...` (bare imports)
- **Expected state:** Package-relative imports (`from .gcode_parser import ...`) so `pip install -e .` && `splice3d` works
- **Evidence:** `ModuleNotFoundError: No module named 'gcode_parser'` when imported as package
- **Status:** OPEN

### GAP-002: [Tier A] MAX_SEGMENTS mismatch: Python 10000 vs firmware 500
- **Requirement:** REQ-015 / cross-component
- **Consensus:** 3/4 (V1, V3, V4)
- **Current state:** `recipe_validator.py:41` MAX_SEGMENTS=10000; `state_machine.h:15` MAX_SEGMENTS=500
- **Expected state:** Both should use same limit (500 unless firmware is expanded)
- **Evidence:** Python validates up to 10K; firmware truncates at 500
- **Status:** OPEN

### GAP-003: [Tier A] Serial buffer 256 vs config 512
- **Requirement:** REQ-029, REQ-092
- **Consensus:** 4/4 (V1, V2, V3, V4)
- **Current state:** `serial_handler.h` hardcodes `char _buffer[256]`; `config.h:25` defines `SERIAL_BUFFER_SIZE 512`
- **Expected state:** Buffer should use `SERIAL_BUFFER_SIZE` constant
- **Evidence:** Any recipe JSON >256 bytes is silently truncated
- **Status:** OPEN

### GAP-004: [Tier A] Static variables in state handlers (re-entry bugs)
- **Requirement:** REQ-097
- **Consensus:** 4/4 (V1, V2, V3, V4)
- **Current state:** `state_machine.cpp` has 9 `static bool` locals in handlers (lines 217, 237, 255, 271, 288, 313, 329, 351, 392)
- **Expected state:** Member variables reset in `transitionTo()`
- **Evidence:** After ABORT + re-START, handlers skip initialization
- **Status:** OPEN

### GAP-005: [Tier A] Resume doesn't restore heater state
- **Requirement:** REQ-025
- **Consensus:** 2/4 (V1, V2) - verified by direct code reading
- **Current state:** `state_machine.cpp:142-151` resume() restores state but not heater/PID
- **Expected state:** Resume should re-enable heater if paused state was HEATING/WELDING
- **Evidence:** pause() calls setHeaterPower(0); resume() never re-enables it
- **Status:** OPEN

### GAP-006: [Tier A] No watchdog timer
- **Requirement:** REQ-099
- **Consensus:** 3/4 (V1, V2, V4)
- **Current state:** `main.cpp` has no `wdt_enable()` or equivalent
- **Expected state:** Hardware WDT with ~4s timeout, fed in main loop
- **Evidence:** grep for wdt/watchdog returns zero results
- **Status:** OPEN

### GAP-007: [Tier A] millis() rollover in heater timeout
- **Requirement:** REQ-098
- **Consensus:** 3/4 (V1, V2, V4)
- **Current state:** `state_machine.cpp:298` uses `if (millis() > _heaterTimeout)` (not rollover-safe)
- **Expected state:** Use `if (millis() - _heatingStartTime > HEATER_TIMEOUT_MS)` pattern
- **Evidence:** Fails after 49.7 days of continuous operation
- **Status:** OPEN

### GAP-008: [Tier A] Auto-tune division by zero
- **Requirement:** REQ-095
- **Consensus:** 3/4 (V1, V2, V4)
- **Current state:** `temperature_autotune.cpp:50` divides by `amplitude` with no zero guard
- **Expected state:** Guard with `if (amplitude < 0.1f)` before division
- **Evidence:** If peakHigh == peakLow, amplitude=0, ku=infinity, PID gains become NaN
- **Status:** OPEN

### GAP-009: [Tier A] MQTT bridge status parsing incompatible with firmware
- **Requirement:** REQ-083
- **Consensus:** 2/4 (V2, V3) - verified by direct code reading
- **Current state:** Bridge expects `STATE:IDLE TEMP:200/210` (colon-delimited); firmware emits `STATUS IDLE TEMP 200.0/210.0` (space-delimited)
- **Expected state:** Bridge parser matches firmware output format
- **Evidence:** `_parse_status_line()` splits on `:` but firmware uses spaces
- **Status:** OPEN

---

## Tier B (Important) - Fix Second

### GAP-010: [Tier B] 29 lint errors (14 unused imports, 12 f-string, 2 unused vars, 1 bare except)
- **Requirement:** REQ-088
- **Consensus:** 2/4 (V2, V4)
- **Current state:** `ruff check` reports 29 errors across postprocessor/, cli/, services/
- **Expected state:** Zero lint errors
- **Status:** OPEN

### GAP-011: [Tier B] No tests for CLI modules (0% coverage on 1,584 lines)
- **Requirement:** REQ-087
- **Consensus:** 2/4 (V1, V4)
- **Current state:** cli/analyze_gcode.py, cli/simulator.py, cli/splice3d_cli.py, cli/gui.py, cli/api_server.py, services/mqtt_bridge.py have zero tests
- **Expected state:** At least unit tests for core logic (parsers, command builders, state management)
- **Status:** OPEN

### GAP-012: [Tier B] Python file I/O has no error handling (modify_file, save_recipe)
- **Requirement:** REQ-008, REQ-012
- **Consensus:** 2/4 (V2, V3)
- **Current state:** `gcode_modifier.py:45-53` and `recipe_generator.py:210-219` have no try/except
- **Expected state:** IOError/PermissionError handled gracefully
- **Status:** OPEN

### GAP-013: [Tier B] MQTT bridge sends PREHEAT/COOLDOWN commands firmware doesn't recognize
- **Requirement:** REQ-083
- **Consensus:** 2/4 (V2, V3)
- **Current state:** Bridge maps cmd_preheat/cmd_cooldown to serial "PREHEAT"/"COOLDOWN"
- **Expected state:** Map to `TEMP MATERIAL PLA` and `TEMP 0`
- **Status:** OPEN

### GAP-014: [Tier B] Dockerfile missing services/ dir and pyserial dependency
- **Requirement:** REQ-084
- **Consensus:** 2/4 (V3, V4)
- **Current state:** Dockerfile copies only postprocessor/, cli/, samples/. Missing pyserial.
- **Expected state:** Include services/ and all deps
- **Status:** OPEN

### GAP-015: [Tier B] Simulator division by zero on zero rates
- **Requirement:** REQ-022
- **Consensus:** 2/4 (V1, V2)
- **Current state:** `cli/simulator.py` divides by `heat_rate_c_s` and `cool_rate_c_s` with no guard
- **Expected state:** Guard against zero-value config parameters
- **Status:** OPEN

### GAP-016: [Tier B] State machine hardcodes PLA temperature (ignores material)
- **Requirement:** REQ-041 / REQ-100 (M2)
- **Consensus:** 3/4 (V1, V2, V3)
- **Current state:** `state_machine.cpp:292` always uses `WELD_TEMP_PLA` (210C)
- **Expected state:** Query material profile for correct temperature
- **Status:** OPEN

### GAP-017: [Tier B] No motor motion timeout in state machine
- **Requirement:** REQ-100 (M1)
- **Consensus:** 3/4 (V1, V2, V4)
- **Current state:** `handleFeedingA/B` checks `isStepperIdle()` but has no timeout
- **Expected state:** Timeout after configurable period, transition to ERROR
- **Status:** OPEN

### GAP-018: [Tier B] TMC2209 init failure not blocking
- **Requirement:** REQ-094
- **Consensus:** 2/4 (V1, V2)
- **Current state:** `tmc_config.cpp` prints warning but proceeds on UART failure
- **Expected state:** Halt or enter error state if TMC communication fails
- **Status:** OPEN

---

## Tier C (Completeness) - Fix Last

### GAP-019: [Tier C] pyproject.toml has placeholder URLs
- **Requirement:** Discovered
- **Consensus:** 1/4 (V4) - confirmed by reading pyproject.toml
- **Current state:** URLs point to `https://github.com/yourusername/splice3d`
- **Expected state:** Point to actual repo `https://github.com/dmhernandez2525/splice3d`
- **Status:** OPEN

### GAP-020: [Tier C] CI pipeline is non-blocking (continue-on-error on all quality steps)
- **Requirement:** REQ-085
- **Consensus:** 2/4 (V1, V4)
- **Current state:** Lint, coverage, firmware build all use `continue-on-error: true`
- **Expected state:** Quality gates that block merges
- **Status:** OPEN

### GAP-021: [Tier C] Render API server uses Flask dev server instead of gunicorn
- **Requirement:** REQ-086
- **Consensus:** 1/4 (V3) - confirmed by reading render.yaml
- **Current state:** `startCommand: python -m cli.api_server` (uses app.run())
- **Expected state:** `gunicorn cli.api_server:app` (gunicorn already in requirements-render.txt)
- **Status:** OPEN

### GAP-022: [Tier C] Bare except in mqtt_bridge.py
- **Requirement:** REQ-088
- **Consensus:** 2/4 (V2, V4)
- **Current state:** `services/mqtt_bridge.py:469` uses `except:` (catches SystemExit, etc.)
- **Expected state:** `except Exception:` at minimum
- **Status:** OPEN

### GAP-023: [Tier C] Validation tests only check JSON spec structure, not runtime logic
- **Requirement:** REQ-087
- **Consensus:** 2/4 (V1, V4)
- **Current state:** ~400 of 585 tests only validate spec file fields exist
- **Expected state:** Acknowledged as contract tests; true logic coverage is ~55-60%
- **Status:** NOTED (not actionable without hardware)

### GAP-024: [Tier C] MQTT bridge doesn't consume JSON telemetry stream
- **Requirement:** REQ-083
- **Consensus:** 1/4 (V3) - confirmed
- **Current state:** Firmware emits JSON telemetry; bridge has no handler for it
- **Expected state:** Bridge should detect and parse JSON telemetry lines
- **Status:** OPEN

---

## Summary

| Tier | Count | Status |
|------|-------|--------|
| A (Critical) | 9 | All OPEN |
| B (Important) | 9 | All OPEN |
| C (Completeness) | 6 | 5 OPEN, 1 NOTED |

**Total verified gaps: 24**
**Fix order: GAP-001 through GAP-009 (Tier A), then GAP-010 through GAP-018 (Tier B), then GAP-019 through GAP-024 (Tier C)**
