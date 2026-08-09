# Verification 2 - Cycle 2: Error Paths & Resilience

> **Verifier focus:** Error handling paths, resilience, edge cases, and regressions from Cycle 1 fixes.
> **Date:** 2026-03-28
> **Scope:** postprocessor/, firmware/src/, services/, cli/

---

## Section 1: Verification of Cycle 1 Fixes

### GAP-012 (IOError handling in gcode_modifier.py) -- VERIFIED FIXED

File: `postprocessor/gcode_modifier.py` lines 44-56

The `modify_file` method now wraps both `open(input_path)` and `open(output_path)` in try/except IOError blocks, re-raising with descriptive messages and proper exception chaining (`from e`). Correct.

### GAP-012 (IOError handling in recipe_generator.py) -- VERIFIED FIXED

File: `postprocessor/recipe_generator.py` lines 218-222

The `save_recipe` method wraps the write in try/except IOError with proper chaining. Correct.

**Minor note:** The `save_recipe` method handles write errors, but the `generate()` method does not guard against an empty `parse_result.segments` list. If called with no segments, it runs fine (produces an empty recipe), so this is acceptable behavior.

### GAP-004 (Static -> member variable migration in state_machine.cpp) -- VERIFIED FIXED

File: `firmware/src/state_machine.h` lines 123-131, `firmware/src/state_machine.cpp` lines 191-208

All 8 handler flags (`_feedStarted`, `_cutStarted`, `_positionStarted`, `_heatingStarted`, `_weldStarted`, `_coolingStarted`, `_spoolingStarted`, `_completionReported`) are now member variables. They are initialized in the constructor (lines 20-27) and reset in `transitionTo()` (lines 197-204). This is the correct pattern.

**Handler flag reset logic review:** The `transitionTo()` method resets ALL flags on EVERY state transition. This is correct and safe. No handler resets flags incorrectly on every call; they all follow the pattern `if (!_flag) { doInit(); _flag = true; }`.

**REGRESSION FOUND (NEW-001):** See Section 2 below regarding redundant manual resets in handlers.

### GAP-008 (Auto-tune division by zero guard) -- VERIFIED FIXED

File: `firmware/src/temperature_autotune.cpp` lines 52-56

Guard checks `amplitude < 0.1f || tu < 0.001f` before the division at line 57. Both divisors (`amplitude` in the `ku` calculation and `tu` in the `ki` calculation) are properly guarded. The function prints an error message and deactivates autotune on failure. Correct.

### GAP-009 (MQTT bridge status parser rewrite) -- VERIFIED FIXED

File: `services/mqtt_bridge.py` lines 276-314

The `_parse_status_line()` method now uses a token-scanning loop over `parts = line.split()`. It correctly handles:
- `STATUS <state>` -- extracts state name
- `PROGRESS <n/m>` -- parses fraction with ValueError guard
- `TEMP <c/t>` -- parses temperature pair with ValueError guard
- `ENC_MM <val>` -- consumed but not stored (acceptable)
- `ENC_SLIP <val>` -- consumed but not stored

Edge case handling for `_parse_status_line`:
- Empty string: `parts = []`, loop never executes. `last_update` is still set at line 315. Acceptable.
- Partial data (e.g., `"STATUS"`): `i + 1 < len(parts)` guard prevents IndexError. Correct.
- Malformed values (e.g., `"PROGRESS abc/def"`): ValueError is caught by the `except ValueError: pass`. Correct.
- Unknown tokens: Skipped silently via the else-increment at `i += 1`. Correct.

### GAP-015 (Simulator zero-rate protection) -- VERIFIED FIXED

File: `cli/simulator.py` lines 152-153, 170

The HEATING state uses `max(self.config.heat_rate_c_s, 0.1)` as denominator. The COOLING state uses `max(self.config.cool_rate_c_s, 0.1)`. Both prevent division by zero. Correct.

Empty segments: The `run()` method at line 112-114 checks `if not self.segments` and transitions to COMPLETE. Correct.

### GAP-005 (Resume heater restoration) -- VERIFIED FIXED, WITH ISSUE

File: `firmware/src/state_machine.cpp` lines 150-165

Resume now checks if the paused state was HEATING or WELDING and calls `setTargetTemperature(WELD_TEMP_PLA)` plus resets `_heatingStarted = false`. **However, this introduces a correctness issue** -- see NEW-002 below.

---

## Section 2: NEW Issues Found

### NEW-001: [Tier C] Redundant flag resets in handlers (dead code, not a bug)

**Files:** `firmware/src/state_machine.cpp` lines 278, 294-295, 311-312, 349, 371, 388
**Severity:** Low (cosmetic/maintenance)

Several handlers manually reset their `_*Started` flag before calling `transitionTo()`:
- `handleFeedingB()` line 278: `_feedStarted = false;` then line 279 calls `transitionTo(State::CUTTING)` which resets ALL flags
- `handleCutting()` line 295: `_cutStarted = false;`
- `handlePositioning()` line 312: `_positionStarted = false;`
- `handleWelding()` line 349: `_weldStarted = false;`
- `handleCooling()` line 371: `_coolingStarted = false;`
- `handleSpooling()` line 388: `_spoolingStarted = false;`

These manual resets are harmless but redundant since `transitionTo()` already resets all flags. They appear to be leftover from the pre-fix code where static locals could not be reset centrally. Notably, `handleFeedingA()` does NOT have this redundant reset (line 258 calls `transitionTo` directly), showing inconsistency.

**Impact:** No runtime bug, but confusing for future maintainers who might wonder if the manual reset serves a special purpose.

### NEW-002: [Tier A] resume() hardcodes WELD_TEMP_PLA, ignoring active material profile

**File:** `firmware/src/state_machine.cpp` line 161
**Requirement:** REQ-041, REQ-025

The `resume()` method restores the heater with:
```cpp
setTargetTemperature(WELD_TEMP_PLA);
```

This always sets 210C regardless of the active material. The `handleHeating()` method (line 321) correctly queries the material profile:
```cpp
const TemperatureProfile profile = getActiveTemperatureProfile();
setTargetTemperature(profile.spliceTargetC);
```

If the machine is paused during HEATING or WELDING with PETG (235C) or ABS (250C), resuming will set the wrong temperature (210C). This was introduced by the GAP-005 fix. The fix for GAP-016 (use material profile in handleHeating) is correct, but the resume path was not updated to match.

**Fix:** Replace `WELD_TEMP_PLA` with `getActiveTemperatureProfile().spliceTargetC` in `resume()`.

### NEW-003: [Tier B] resume() resets _heatingStarted but not other handler flags, causing state re-entry mismatch

**File:** `firmware/src/state_machine.cpp` line 162
**Requirement:** REQ-025

When resuming to `State::HEATING`, the code sets `_heatingStarted = false` to force the heating handler to re-initialize. This is correct for HEATING. But when resuming to `State::WELDING`, the same `_heatingStarted = false` is set, which is irrelevant (WELDING uses `_weldStarted`). More importantly, `_weldStarted` is NOT reset, so the WELDING handler will NOT re-initialize the weld compression on resume.

This means: if paused during WELDING, the weld compression step (`compressWeld()`) is not re-initiated on resume. The handler will just wait for the remaining hold time (which restarted from the wrong baseline since `_stateStartTime` was not reset either).

Additionally, if paused during FEEDING_A, COOLING, SPOOLING, or any other active state, none of the corresponding flags are reset, so motors/actions that were stopped by `pause()` are never re-started.

**Impact:** After pause/resume in any active state other than HEATING, the machine hangs because the handler thinks initialization already happened but the hardware was stopped.

**Fix:** `resume()` should reset the flag corresponding to `_pausedState`, or alternatively call `transitionTo(_pausedState)` which resets all flags and restarts `_stateStartTime`. However, `transitionTo()` would also reset the state start time, which may or may not be desired (losing progress timing). The safest fix is to reset all handler flags in resume, matching what transitionTo does:

```cpp
void StateMachine::resume() {
    if (!_isPaused) return;
    _isPaused = false;

    // Reset all handler flags so the resumed state re-initializes
    _feedStarted = false;
    _cutStarted = false;
    _positionStarted = false;
    _heatingStarted = false;
    _weldStarted = false;
    _coolingStarted = false;
    _spoolingStarted = false;
    _completionReported = false;

    _state = _pausedState;
    _stateStartTime = millis();  // Reset timeout baseline

    // Restore heater if needed
    if (_state == State::HEATING || _state == State::WELDING) {
        const TemperatureProfile profile = getActiveTemperatureProfile();
        setTargetTemperature(profile.spliceTargetC);
    }

    Serial.println(F("OK RESUMED"));
}
```

### NEW-004: [Tier B] MQTT bridge _handle_serial_line: DONE handler does not clear error state

**File:** `services/mqtt_bridge.py` lines 367-374
**Requirement:** REQ-083

When the bridge receives "DONE", it sets `self.state.state = "IDLE"` and records a splice. However, if a previous error had set `self.state.error = True` and `self.state.error_message`, those fields are never cleared. Subsequent MQTT publishes will show the machine as IDLE but still report `error: ON` and the old error message.

The ERROR handler at line 377 sets `self.state.error = True`, but there is no code path that resets `error` to `False` except for initial construction. A successful DONE, a new STATUS update, or a START should clear the error flag.

**Impact:** Home Assistant dashboard shows a stale error indicator after the machine recovers and completes a new job.

**Fix:** Add `self.state.error = False; self.state.error_message = ""` in the DONE handler, and also in the STATUS handler when state is not "ERROR".

### NEW-005: [Tier B] MQTT bridge _parse_status_line ignores the "STATUS" value when line starts with "STATUS:" or contains "STATE:"

**File:** `services/mqtt_bridge.py` lines 320-322, 282-289
**Requirement:** REQ-083

The `_handle_serial_line` dispatches to `_parse_status_line` if the line starts with `"STATUS "`, `"STATUS:"`, or contains `"STATE:"` (line 321). However, `_parse_status_line` only recognizes the token `"STATUS"` (uppercase, no colon).

If the firmware sends `"STATUS:IDLE TEMP 200/210"` (colon-delimited variant), the tokenizer splits on whitespace producing `["STATUS:IDLE", "TEMP", "200/210"]`. The first token is `"STATUS:IDLE"` which when uppercased is `"STATUS:IDLE"` -- this does NOT match `token == "STATUS"`, so the state field is never extracted.

Similarly, if a line like `"STATE:HEATING"` arrives (matched by `"STATE:" in line` at line 321), the token `"STATE:HEATING"` does not match `"STATUS"`.

The dispatch at line 321 accepts three formats, but the parser only handles one of them.

**Impact:** Status updates using the colon-delimited format are silently dropped (state not updated, temperature possibly missed).

**Fix:** In `_parse_status_line`, also check for tokens that start with `"STATUS:"` or `"STATE:"` and extract the value after the colon.

### NEW-006: [Tier B] Simulator does not validate segment structure before accessing keys

**File:** `cli/simulator.py` lines 120-133, 179
**Requirement:** REQ-022

The simulator accesses `seg['length_mm']` and `seg.get('color', 0)` without verifying these keys exist. If a malformed recipe JSON has segments without `length_mm` (e.g., `{"color": 0}` or `{}`), a KeyError will crash the simulation with no descriptive error.

The `load_recipe` method (line 71) reads `data.get('segments', [])` but performs no validation on individual segment structure. Combined with the broad `except Exception` at line 77, a load failure gives a generic message, but an in-flight crash during `run()` is unhandled.

**Impact:** Unhandled KeyError crash on malformed recipe input. Low severity since this is a development tool, but inconsistent with the defensive patterns added elsewhere.

---

## Section 3: Summary

### Cycle 1 Fix Verification

| GAP | Fix Status | Notes |
|-----|-----------|-------|
| GAP-004 | VERIFIED CORRECT | Static -> member, centralized reset in transitionTo() |
| GAP-005 | VERIFIED, REGRESSION | Heater restoration works but hardcodes PLA temp (NEW-002) |
| GAP-008 | VERIFIED CORRECT | Division-by-zero guard with proper thresholds |
| GAP-009 | VERIFIED CORRECT | Token-scanning parser handles edge cases |
| GAP-012 | VERIFIED CORRECT | IOError handling in both files |
| GAP-015 | VERIFIED CORRECT | Zero-rate guards and empty segments check |

### New Issues Found: 6

| ID | Tier | File | Description |
|----|------|------|-------------|
| NEW-001 | C | state_machine.cpp | Redundant flag resets (dead code, cosmetic) |
| NEW-002 | A | state_machine.cpp:161 | resume() hardcodes WELD_TEMP_PLA instead of using active profile |
| NEW-003 | B | state_machine.cpp:150-165 | resume() only resets _heatingStarted; other flags stale after pause, causing hang |
| NEW-004 | B | mqtt_bridge.py:367-374 | DONE handler never clears error flag, causing stale error in MQTT |
| NEW-005 | B | mqtt_bridge.py:320-322 | STATUS:/STATE: colon-format lines dispatched to parser but not actually parsed |
| NEW-006 | B | cli/simulator.py:120-133 | No validation of segment keys; KeyError on malformed recipe |

### Counts

- Total fixes verified: 6 of 6 assigned
- Verified correct: 5
- Verified with regression: 1 (GAP-005)
- New issues found: 6 (1 Tier A, 4 Tier B, 1 Tier C)
- Required minimum (3 new): MET
