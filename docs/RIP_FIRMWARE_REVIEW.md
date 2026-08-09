# Splice3D Firmware RIP Cycle Report

**Date:** 2026-03-28
**Scope:** Firmware hardware interface layer, serial protocols, error handling, timeouts
**Files Reviewed:** 15 firmware source files (~2,800 lines of C++)
**Issues Found:** 33 (8 HIGH, 14 MEDIUM, 5 LOW, 6 informational)

---

## Test Results

- **Total tests:** 585 (549 existing + 36 new)
- **Pass rate:** 100%
- **Coverage:** 95% (postprocessor module)
- **New test file:** `postprocessor/tests/test_splice3d_postprocessor.py`

---

## Architecture Overview

The firmware runs on an STM32F103-based BTT SKR Mini E3 v2 board. The main loop calls
32 subsystem update functions sequentially. Hardware communication uses:
- USB Serial at 115200 baud for host commands
- TMC2209 UART for stepper driver configuration
- GPIO for heater PWM, fan control, thermistor ADC
- ISR-driven quadrature encoder for filament tracking
- AccelStepper library for non-blocking motor control

---

## HIGH Severity Issues

### H1: Serial Buffer Overflow (silent data loss)
**File:** `serial_handler.cpp:39-40`
**Config:** `config.h` defines `SERIAL_BUFFER_SIZE 512`, but `serial_handler.h` allocates `char _buffer[256]`.
**Impact:** RECIPE commands with JSON > 256 bytes are silently truncated. No error reported.
**Fix:** Align buffer to `SERIAL_BUFFER_SIZE`. Add overflow error response.

### H2: Manual JSON Parsing Vulnerable to Malformed Input
**File:** `serial_handler.cpp:119-193`
**Impact:** Uses `strstr()`/`strchr()`/`atoi()`/`atof()` to parse recipe JSON. No bounds validation
on segment arrays. `atoi()` returns 0 on parse failure (silently accepted as valid colorIndex).
Unterminated JSON strings could cause the parser to scan past the buffer.
**Fix:** Validate `colorIndex` range (0-1 for two-color). Validate `lengthMm > 0`. Add explicit
bounds checking on all pointer arithmetic. Consider a lightweight JSON parser.

### H3: TMC2209 UART Initialization Failures Silently Ignored
**File:** `tmc_config.cpp:35`
**Impact:** `checkDriverStatus()` can fail, but `initTMCDrivers()` continues anyway. System operates
with unconfigured stepper drivers (wrong current, no stall detection, no StealthChop).
100ms busy-wait blocks MCU during init.
**Fix:** Require TMC communication success before declaring ready. Report TMC init status via serial.

### H4: Auto-Tune Division by Zero
**File:** `temperature_autotune.cpp:50`
**Impact:** If oscillation amplitude is 0 (too small to measure), `Ku = 4.0 * range / (pi * 0.0)` = NaN.
NaN propagates to PID gains, making temperature control unpredictable.
**Fix:** Guard with `if (amplitude < 0.1f) { Serial.println("AUTOTUNE_FAIL amplitude too small"); return; }`

### H5: Dual Error State Machines (unsynchronized)
**Files:** `state_machine.cpp:188-197`, `error_handler.h`, `error_recovery.h`
**Impact:** `StateMachine` has its own `ERROR` state with `_errorMessage`. `ErrorHandler` has its own
`ErrorCode` and `_currentError`. `ErrorRecovery` has its own `RecoveryPhase`. None synchronize.
Recovery could succeed in ErrorRecovery while StateMachine stays in ERROR.
**Fix:** Unify. ErrorHandler should be the single authority. StateMachine ERROR state should delegate
to ErrorHandler for recovery decisions.

### H6: Static Variables in State Handlers (re-entry bugs)
**File:** `state_machine.cpp:217, 237, 255, 271, 288, 313, 329, 351, 392`
**Impact:** Every state handler uses `static bool xxxStarted = false`. On pause/resume, these persist.
If timing goes wrong, a static flag from a previous entry can cause skipped initialization.
The `handleComplete` handler has `static bool completionReported` that never resets, preventing
re-use after loading a new recipe without power cycling.
**Fix:** Move all `static` flags into StateMachine member variables. Reset them in `transitionTo()`.

### H7: millis() Rollover Breaks Heater Timeout
**File:** `state_machine.cpp:293-298`
```cpp
_heaterTimeout = millis() + HEATER_TIMEOUT_MS;  // Set
if (millis() > _heaterTimeout) { ... }           // Check
```
**Impact:** After 49.7 days of continuous operation, `millis()` rolls over to 0. The comparison
`millis() > _heaterTimeout` immediately becomes true, triggering a false HEATER_TIMEOUT error.
**Fix:** Use elapsed time pattern: `if (millis() - _heatingStartTime > HEATER_TIMEOUT_MS)`.

### H8: No Watchdog Timer
**File:** `main.cpp`
**Impact:** No `wdt_enable()` call. If any subsystem hangs (e.g., TMC UART deadlock, ISR disable
without re-enable), the MCU stops responding permanently. Heater could remain on.
**Fix:** Enable hardware WDT with ~4s timeout. Feed in main loop.

---

## MEDIUM Severity Issues

### M1: No Timeout on Motor Motion
**File:** `state_machine.cpp:230-233, 248-250`
**Impact:** `handleFeedingA/B` checks `isStepperIdle()` but has no timeout. If a motor is jammed
(encoder detects no movement), the state machine waits forever.
**Fix:** Add timeout (e.g., `if (millis() - _stateStartTime > FEED_TIMEOUT_MS)`) and transition to ERROR.

### M2: Temperature Always Uses PLA Profile
**File:** `state_machine.cpp:292`
```cpp
setTargetTemperature(WELD_TEMP_PLA);  // Hardcoded!
```
**Impact:** PETG needs 235C, ABS needs 250C. Using 210C for these materials produces weak welds.
The temperature system already has material profiles that are never queried by the state machine.
**Fix:** Query `activeProfileEntry().spliceTargetC` or accept material in recipe JSON.

### M3: Serial Temperature Change During Active Splice
**File:** `serial_temperature.cpp`
**Impact:** `TEMP <value>` command can change temperature mid-weld with no safety check.
Could compromise weld quality or cause thermal shock.
**Fix:** Reject temperature changes when state machine is in HEATING/WELDING/COOLING states.

### M4: Sensorless Homing Failure Not Propagated
**File:** `stepper_control.cpp:248`
**Impact:** `sensorlessHome()` returns `false` on 12s timeout, but calling code doesn't check.
Machine proceeds with incorrect position reference.
**Fix:** Propagate failure to state machine. Require successful homing before recipe start.

### M5: Emergency Stop Doesn't Reset Motor Current
**File:** `stepper_control.cpp:161-168, 173`
**Impact:** `emergencyStopAll()` stops motion but doesn't restore motor current from run level
to hold level. Motors stay at 800mA (run) instead of 400mA (hold), causing overheating.
**Fix:** Call `restoreHoldCurrent()` in emergency stop path.

### M6: Backlash Compensation During Active Motion
**File:** `stepper_control.cpp:116-125`
**Impact:** Backlash compensation injects extra movement on direction change without checking
if motor is already moving. Could cause unexpected jolts.
**Fix:** Queue backlash compensation, apply only when motor is idle.

### M7: Thermal Runaway Baseline Stale in SOAK Stage
**File:** `temperature.cpp:88-101`
**Impact:** `runawayBaselineC` is updated at line 101 every check interval, but `stageEnteredMs`
(used for elapsed time) is only updated on stage entry. In SOAK, if temp oscillates,
the runaway check could use mismatched baseline/elapsed values.
**Fix:** Track runaway per-window, not per-stage. Reset baseline and timer together.

### M8: Thermistor ADC Blocking (5 samples)
**File:** `temperature.cpp:59-64`
**Impact:** `readThermistorRaw()` calls `analogRead()` 5 times (~500us total). During this time,
encoder ISR may accumulate, and stepper timing could jitter.
**Fix:** Use DMA-based ADC or spread samples across loop iterations.

### M9: No PID Soft-Start / Ramp Limiting
**File:** `temperature.cpp:193-195`
**Impact:** PID output goes directly to `analogWrite()`. Can jump from 0 to 255 PWM instantly.
This causes inrush current spikes and thermal shock to the heating element.
**Fix:** Clamp per-iteration PWM change to e.g., 10 units.

### M10: Cold Extrusion Check Not Enforced
**File:** `temperature.cpp:254-256`
**Impact:** `isColdExtrusionBlocked()` returns a bool but is never called in the state machine.
Motors can extrude cold filament, potentially jamming the feed path.
**Fix:** Check in `handleFeedingA/B` before starting feed. Block with error if cold.

### M11: Encoder Correction Oscillation
**File:** `encoder_system.cpp`
**Impact:** Closed-loop correction applies 0.25 * error every 120ms with no backoff. If the
correction itself introduces error (e.g., backlash), correction oscillates.
**Fix:** Add integral windup limit. Implement deadband + proportional-only correction.

### M12: Encoder Health Stale Not Immediately Reported
**File:** `encoder_system.cpp:135`
**Impact:** `health.failed` set when encoder stale for 1.5s during active motion, but no interrupt
or callback notifies the state machine. Failure only visible on next `STATUS` query.
**Fix:** Add callback or flag that state machine checks each loop iteration.

### M13: No Recipe Segment Validation
**File:** `state_machine.cpp:100-109`
**Impact:** Checks segment count > 0, but doesn't validate individual segments. Zero-length segments
or out-of-range colorIndex values are accepted.
**Fix:** Validate each segment: `lengthMm > 0`, `colorIndex < COLOR_COUNT`.

### M14: Cooldown Timeout Gives Up Too Early
**File:** `error_recovery.cpp:110`
**Impact:** 60-second cooldown timeout marks recovery as failed even if temperature is dropping
(just slowly). Should continue as long as temperature is decreasing.
**Fix:** Continue cooldown if temp is still dropping. Only fail if temp plateaus above target.

---

## LOW Severity Issues

### L1: Device Connection Layer is Non-functional
**File:** `device_connection.cpp`
**Impact:** Stub implementation. All stats are zero. No device scanning.
**Recommendation:** Remove or clearly mark as unimplemented to avoid confusion.

### L2: Error History Limited to 8 Entries
**File:** `error_recovery.cpp:13`
**Impact:** Ring buffer, oldest entries overwritten. Adequate for typical use, but long production
runs may lose early error context.
**Recommendation:** Log errors to serial/telemetry as they occur.

### L3: Encoder Tick Counter Overflow
**File:** `encoder_system.cpp`
**Impact:** `int64_t tickCount` can overflow after ~9 exabytes of filament (theoretical, not practical).
**Recommendation:** No action needed. Document the limit.

### L4: Retry Count Not Reset Between Different Errors
**File:** `error_handler.cpp`
**Impact:** If error A uses 1 retry, then error B only gets 2 retries (3 max - 1 used).
**Fix:** Reset `_retryCount` in `reportError()` when error code changes.

### L5: Emergency Shutdown Flag Not Reversible
**File:** `error_handler.cpp:126`
**Impact:** `_shutdownComplete = true` prevents outputs from re-enabling after emergency.
Requires MCU reset to recover from any emergency stop.
**Recommendation:** Allow reset via explicit serial command or hardware button, not just MCU reset.

---

## Timeout and Retry Configuration Summary

| Parameter | Value | Location |
|-----------|-------|----------|
| Serial baud rate | 115200 | config.h |
| Serial buffer (configured) | 512 bytes | config.h |
| Serial buffer (actual) | 256 bytes | serial_handler.h (MISMATCH) |
| Heater timeout | 120s | config.h |
| Thermal runaway window | 40s | config.h |
| Thermal runaway check interval | 5s | config.h |
| PID watchdog | 2s | config.h |
| Encoder debounce | 70us | config.h |
| Encoder correction interval | 120ms | config.h |
| Encoder stale threshold | 1.5s | config.h |
| Sensorless homing timeout | 12s | stepper_control.cpp |
| Cutter servo travel | 300ms | config.h |
| Weld hold time | 3s | config.h |
| Cooling time | 5s | config.h |
| Error retry limit | 3 | error_recovery.cpp |
| Cooldown recovery timeout | 60s | error_recovery.cpp |
| Retry delay | 1s | error_recovery.cpp |
| Cut wait (hardcoded) | 500ms | state_machine.cpp |
| Positioning wait (hardcoded) | 1000ms | state_machine.cpp |
| Serial port init wait | 3s | main.cpp |

---

## Race Conditions Identified

1. **Encoder correction + state machine motion:** Encoder closed-loop correction injects motor
   commands every 120ms while state machine is also commanding motion in FEEDING states.
2. **Serial temperature change during weld:** `TEMP` command changes setpoint with no state guard.
3. **Dual error state machines:** StateMachine ERROR vs ErrorHandler _currentError vs ErrorRecovery
   RecoveryPhase can disagree on error state.
4. **Static handler variables on pause/resume:** `feedStarted`, `cutStarted`, etc. persist across
   pause/resume cycles and can cause double-initialization or skipped initialization.

---

## Recommended Priority Order

**Immediate (before first production use):**
1. H8: Add watchdog timer
2. H6: Replace static variables with member variables
3. H7: Fix millis() rollover pattern
4. H1: Fix serial buffer size mismatch
5. M1: Add motor motion timeouts

**Before multi-material support:**
6. M2: Use material profile for weld temperature
7. M10: Enforce cold extrusion check
8. H5: Unify error state machines

**Before extended production runs:**
9. H3: Validate TMC UART init
10. H4: Guard auto-tune division by zero
11. H2: Harden JSON parsing
12. M3: Guard temperature changes during active splice

---

## Main Loop Performance Concern

The `loop()` function calls 32 update functions sequentially with no time budgeting.
If any single update function takes > 10ms (e.g., TMC UART communication, thermistor
sampling), the control loop period becomes unpredictable. This affects:
- Stepper motion smoothness (AccelStepper needs frequent `run()` calls)
- Encoder edge processing (ISR-driven, but snapshot timing varies)
- PID temperature control (jitter in compute interval)

Consider adding loop timing instrumentation: measure `micros()` at loop start/end,
report via telemetry if loop exceeds a threshold (e.g., 5ms).
