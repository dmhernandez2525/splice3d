# Verification-3: Data Integrity & Integration Report (Cycle 1)

**Auditor:** Verifier-3 (Data Integrity & Integration)
**Date:** 2026-03-28
**Scope:** Cross-component data flow, serial protocol alignment, config consistency, entry points, Docker/Render configs, MQTT bridge, hardware specs

---

## 1. Recipe JSON: Python recipe_generator.py vs Firmware serial_handler.cpp

**Rating: ALIGNED (field names and types match)**

Python `recipe_generator.py` outputs segments as:
```json
{"color": 0, "length_mm": 123.45}
```

Firmware `serial_handler.cpp` (line 126) parses exactly `"color"` and `"length_mm"`:
```c
const char* colorPtr = strstr(objStart, "\"color\"");
const char* lengthPtr = strstr(objStart, "\"length_mm\"");
```

The top-level recipe also includes `"segments"` array, which the firmware expects (`strstr(args, "\"segments\"")`). Field names, types (int color, float length), and JSON structure are consistent.

**However, one sub-issue noted:** The firmware parser also looks for `"total_length_mm"` in the comment (line 126) but never actually parses it. The Python side emits it but it is unused. This is benign but indicates dead spec.

---

## 2. Serial Protocol: CLI splice3d_cli.py vs Firmware serial_handler.cpp

**Rating: ALIGNED (core commands match)**

| Command | CLI sends | Firmware handles | Match? |
|---------|-----------|-----------------|--------|
| RECIPE  | `RECIPE {json}` | `handleRecipe(args)` | YES |
| START   | `START` | `handleStart()` | YES |
| PAUSE   | (via `send_command`) | `handlePause()` | YES |
| RESUME  | (via `send_command`) | `handleResume()` | YES |
| ABORT   | (via `send_command`) | `handleAbort()` | YES |
| STATUS  | `STATUS` | `handleStatus()` | YES |
| HELP    | (via interactive) | `handleHelp()` | YES |

The CLI uses generic `send_command()` that can send any string, so TEMP, ENCODER, CUTTER, RECOVER, STREAM are all accessible. Response parsing checks for `OK` and `ERROR` prefixes, which matches firmware output patterns.

---

## 3. Material Profiles: Python filament_profiles.py vs Firmware temperature.cpp

**Rating: ALIGNED (core temperatures match)**

| Material | Python splice_temp | Firmware spliceTargetC | Match? |
|----------|-------------------|----------------------|--------|
| PLA      | 210               | 210.0f               | YES    |
| PETG     | 235               | 235.0f               | YES    |
| ABS      | 250               | 250.0f               | YES    |

**Sub-issue:** Python has additional fields (heat_time_ms, cooling_time_ms, compression_mm) that have no firmware-side counterparts in the material profile struct. Firmware uses `soakTimeMs` and `rampRateCPerSec` instead, which are different concepts:

| Python field | Python PLA value | Firmware equivalent | Firmware PLA value |
|---|---|---|---|
| heat_time_ms | 3000 | soakTimeMs | 2000 |
| cooling_time_ms | 5000 | (COOLING_TIME_MS config) | 5000 |
| compression_mm | 2.0 | (WELD_COMPRESSION_MM config) | 2.0 |

The `heat_time_ms` (3000) vs `soakTimeMs` (2000) discrepancy is notable but they may represent different concepts (total heating vs soak-at-temp). This warrants clarification.

---

## 4. Config Constants: config.h vs Python-side Equivalents

**Rating: MISMATCHED (two critical mismatches found)**

### CRITICAL: MAX_SEGMENTS mismatch
- `firmware/src/state_machine.h` line 15: `#define MAX_SEGMENTS 500`
- `postprocessor/recipe_validator.py` line 41: `MAX_SEGMENTS = 10000`
- **Impact:** Python validator will approve recipes with up to 10,000 segments, but firmware can only hold 500. Sending a 501+ segment recipe will silently truncate on the firmware side. Stack allocation of `SpliceSegment segments[MAX_SEGMENTS]` in `serial_handler.cpp` line 128 means this is a stack array of 500 elements, and the parser loop stops at MAX_SEGMENTS.

### CRITICAL: Serial buffer size mismatch
- `config.h` line 25: `#define SERIAL_BUFFER_SIZE 512`
- `serial_handler.h` line 38: `char _buffer[256]`
- **Impact:** The buffer is hardcoded to 256 bytes in the header, not using the config constant. A recipe JSON for even a modest number of segments will exceed 256 bytes. This was already flagged as REQ-092 but is still present.

### Other config comparisons:
| Parameter | config.h | Python side | Match? |
|-----------|----------|-------------|--------|
| SERIAL_BAUD (115200) | Yes | CLI default 115200 | YES |
| MAX_TEMP (280) | Yes | Not validated Python-side | N/A |
| WELD_TEMP_PLA (210) | Yes | filament_profiles PLA 210 | YES |
| WELD_TEMP_PETG (235) | Yes | filament_profiles PETG 235 | YES |
| WELD_TEMP_ABS (250) | Yes | filament_profiles ABS 250 | YES |
| MAX_COLORS (8) | Not in config.h | recipe_validator MAX_COLORS=8 | UNTESTABLE (firmware has no explicit limit) |

---

## 5. pyproject.toml Entry Points

**Rating: ALIGNED (all entry points resolve)**

| Entry point | Target | Function exists? |
|-------------|--------|-----------------|
| `splice3d` | `postprocessor.splice3d_postprocessor:main` | YES (line 27) |
| `splice3d-analyze` | `cli.analyze_gcode:main` | YES (line 196) |
| `splice3d-simulate` | `cli.simulator:main` | YES (line 214) |
| `splice3d-mqtt-bridge` | `services.mqtt_bridge:main` | YES (line 554) |

All four entry points reference `main()` functions that exist in the target modules.

---

## 6. Docker/Render Configs

**Rating: MISMATCHED (multiple issues)**

### Dockerfile issues:
1. **Missing requirements.txt content mismatch:** Dockerfile runs `pip install -r postprocessor/requirements.txt`, which contains only `regex>=2023.0.0`. But the project needs `pyserial` (used by CLI/MQTT bridge) and the postprocessor imports `gcode_parser` and `recipe_generator` as bare module names (not `postprocessor.gcode_parser`). The Docker image would fail imports for CLI tools.
2. **Missing services/ directory:** Dockerfile copies `postprocessor/`, `cli/`, `samples/` but NOT `services/`. The MQTT bridge would not be available in the container.
3. **Missing setup.py/pyproject.toml:** Neither `setup.py` nor `pyproject.toml` is copied into the container, so `pip install -e .` or entry points would not work.

### docker-compose.yml issues:
4. **Samples file assumed:** References `test_multicolor.gcode` and `test_multicolor_splice_recipe.json` in samples/. These files exist, so this is fine.

### render.yaml issues:
5. **Website directory exists** (confirmed: has `package.json`, `vite.config.js`, `src/`, `dist/`). Static site config looks correct.
6. **API server references `requirements-render.txt`** which contains `flask` and `gunicorn`, but the `startCommand` is `python -m cli.api_server` which uses Flask directly (no gunicorn). This will work in development but is not production-grade. The `api_server.py` uses `app.run()` directly.
7. **API server needs pyproject.toml or setup.py** for `python -m cli.api_server` to resolve correctly. Without package installation, the module path may fail on Render.

---

## 7. MQTT Bridge vs Firmware Telemetry Format

**Rating: MISMATCHED (protocol parsing does not match firmware output)**

### Status line parsing mismatch:
The MQTT bridge `_parse_status_line()` (line 278) expects colon-delimited format:
```
STATE:IDLE TEMP:200/210 PROGRESS:0 SEGMENT:0/0
```

But the firmware `handleStatus()` (serial_handler.cpp line 215) outputs space-delimited format:
```
STATUS IDLE PROGRESS 3/10 TEMP 200.0/210.0 ENC_MM 15.30 ENC_SLIP 0
```

These formats are **incompatible**. The firmware uses space-separated key-value pairs (no colons), while the bridge parser splits on `:`. The bridge would fail to parse any firmware status output correctly.

### Temperature line parsing:
Bridge expects `TEMP:200/210`, firmware emits `TEMP C=200.0 T=210.0 EFF=... PWM=... STAGE=... FAULT=... ETA=...` (from `serial_temperature.cpp` handleTemp). These are completely different formats.

### PREHEAT/COOLDOWN commands:
The MQTT bridge maps `cmd_preheat` to serial command `PREHEAT` and `cmd_cooldown` to `COOLDOWN`. **Neither PREHEAT nor COOLDOWN are recognized commands in the firmware serial handler.** The firmware would respond with `ERROR Unknown command: PREHEAT`. The correct way to preheat is `TEMP MATERIAL PLA` or `TEMP 210`.

### Telemetry stream not consumed:
Firmware telemetry_stream.cpp emits JSON objects like `{"type":"telemetry","t":12345,"state":"IDLE",...}` but the MQTT bridge `_handle_serial_line()` has no handler for JSON telemetry. It only looks for lines starting with `STATUS:`, `PROGRESS:`, `DONE`, `ERROR`, or `TEMP:`.

---

## 8. Hardware Validation Spec JSONs vs Firmware

**Rating: ALIGNED (spot-checked 4 specs)**

### F2.3 Temperature Control spec:
| Spec field | Spec value | Firmware config.h / temperature.cpp | Match? |
|---|---|---|---|
| max_temperature_c | 280 | MAX_TEMP 280 | YES |
| min_cold_extrusion_c | 170 | COLD_EXTRUSION_MIN_C 170.0f | YES |
| thermistor_disconnect_low_c | -10 | THERMISTOR_DISCONNECT_LOW_C -10.0f | YES |
| thermistor_disconnect_high_c | 350 | THERMISTOR_DISCONNECT_HIGH_C 350.0f | YES |
| pid_watchdog_ms | 2000 | PID_WATCHDOG_MS 2000UL | YES |
| PLA splice_target_c | 210 | kProfiles PLA 210.0f | YES |
| PLA soak_time_ms | 2000 | kProfiles PLA soakTimeMs 2000 | YES |
| heating_stages | OFF,PREHEAT,SOAK,READY,FAULT | HeatingStage enum | YES |

### F2.2 Encoder spec:
| Spec field | Spec value | config.h | Match? |
|---|---|---|---|
| slip_detection_mm | 2.0 | ENCODER_SLIP_THRESHOLD_MM 2.0f | YES |

### F2.4 Cutting spec:
| Spec field | Spec value | config.h | Match? |
|---|---|---|---|
| servo_travel_ms | 300 | CUTTER_SERVO_TRAVEL_MS 300UL | YES |
| maintenance_interval_cuts | 500 | CUTTER_MAINTENANCE_INTERVAL 500 | YES |
| max_force_threshold | 200 | CUTTER_MAX_FORCE_THRESHOLD 200 | YES |
| pre_cut_retract_mm | 1.5 | CUTTER_PRE_CUT_RETRACT_MM 1.5f | YES |
| servo_open_angle | 0 | CUTTER_SERVO_OPEN_ANGLE 0 | YES |
| servo_closed_angle | 90 | CUTTER_SERVO_CLOSED_ANGLE 90 | YES |
| eeprom address | 64 | CUTTER_EEPROM_ADDRESS 64 | YES |

### F4.1 Telemetry spec:
| Spec field | Spec value | telemetry_stream.cpp | Match? |
|---|---|---|---|
| default_interval_ms | 1000 | kDefaultIntervalMs 1000UL | YES |
| min_interval_ms | 100 | kMinIntervalMs 100UL | YES |
| heartbeat_interval_ms | 5000 | kHeartbeatIntervalMs 5000UL | YES |
| stream_modes | OFF,SUMMARY,VERBOSE | StreamMode enum | YES |
| summary_fields | type,t,state,temp,target,pos_mm,vel,slip,splice_active,quality,error | emitSummary() output | YES |

---

## Integration Gaps Found (NEW)

### Gap 1 (CRITICAL): MAX_SEGMENTS 500 vs 10000
- **Location:** `state_machine.h:15` vs `recipe_validator.py:41`
- **Impact:** Python validator approves recipes 20x larger than firmware can handle. Recipes with 501-10000 segments will be validated as OK but silently truncated on the device.
- **Fix:** Align both to 500, or increase firmware allocation and use dynamic allocation.

### Gap 2 (CRITICAL): MQTT Bridge Status Parsing Incompatible with Firmware Output
- **Location:** `services/mqtt_bridge.py:278-305` vs `firmware/src/serial_handler.cpp:215-240`
- **Impact:** The MQTT bridge cannot parse any status data from the firmware. Home Assistant integration is completely non-functional.
- **Fix:** Rewrite `_parse_status_line()` to match firmware's space-delimited format, or have firmware emit colon-delimited format.

### Gap 3 (HIGH): MQTT Bridge sends PREHEAT/COOLDOWN, firmware does not recognize them
- **Location:** `services/mqtt_bridge.py:228-235` maps to commands "PREHEAT" and "COOLDOWN"
- **Impact:** Home Assistant preheat/cooldown buttons would trigger `ERROR Unknown command` on the firmware.
- **Fix:** Map PREHEAT to `TEMP MATERIAL PLA` (or parameterized) and COOLDOWN to `TEMP 0`.

### Gap 4 (HIGH): Serial buffer 256 bytes, ignoring SERIAL_BUFFER_SIZE 512 constant
- **Location:** `serial_handler.h:38` hardcodes `char _buffer[256]` while `config.h:25` defines `SERIAL_BUFFER_SIZE 512`
- **Impact:** Buffer overflow for any recipe JSON > 256 bytes. Even 5 segments produce ~150 bytes of JSON; a 20-segment recipe would exceed 256 bytes.
- **Fix:** Change `_buffer[256]` to `_buffer[SERIAL_BUFFER_SIZE]`.

### Gap 5 (HIGH): MQTT bridge does not consume JSON telemetry stream
- **Location:** `services/mqtt_bridge.py:308-350` vs `firmware/src/telemetry_stream.cpp:53-69`
- **Impact:** Firmware can emit rich JSON telemetry (`{"type":"telemetry",...}`) but the bridge has no handler for it. All telemetry data is silently dropped. The bridge relies on polling STATUS instead, which has a different (also mismatched) format.
- **Fix:** Add JSON line detection in `_handle_serial_line()` to parse telemetry objects.

### Gap 6 (MEDIUM): Dockerfile missing services/ and pyserial dependency
- **Location:** `Dockerfile:13-14` copies only postprocessor/, cli/, samples/
- **Impact:** Docker image cannot run MQTT bridge. Also, `requirements.txt` only has `regex` but CLI needs `pyserial`.
- **Fix:** Add `COPY services/ ./services/` and add `pyserial` to requirements.txt or use pyproject.toml.

### Gap 7 (MEDIUM): Render API server lacks gunicorn in startCommand
- **Location:** `render.yaml:46` uses `python -m cli.api_server` with `app.run()`
- **Impact:** Running Flask's development server in production. No worker management, no graceful restarts.
- **Fix:** Change to `gunicorn cli.api_server:app` (gunicorn is already in requirements-render.txt).

### Gap 8 (MEDIUM): Python postprocessor uses bare module imports
- **Location:** `splice3d_postprocessor.py:23-25`: `from gcode_parser import ...`
- **Impact:** Works only when CWD is `postprocessor/` or it's on PYTHONPATH. Breaks when run as `python -m postprocessor.splice3d_postprocessor` (the pyproject.toml entry point path). The Dockerfile sets `PYTHONPATH="/app"` but the imports would need `postprocessor.gcode_parser`.
- **Fix:** Use relative imports (`from .gcode_parser import ...`) or absolute (`from postprocessor.gcode_parser import ...`).

### Gap 9 (LOW): Python heat_time_ms (3000) vs firmware soakTimeMs (2000) for PLA
- **Location:** `filament_profiles.py:46` vs `temperature.cpp:15`
- **Impact:** These likely represent different concepts (total heat time vs soak-after-reaching-temp), but the naming does not make this clear. Could cause confusion if someone tries to use Python profiles to predict firmware timing.

### Gap 10 (LOW): Simulator hardcodes 2-color assumption
- **Location:** `cli/simulator.py:196-202`
- **Impact:** Simulator only handles color 0 (FEEDING_A) and anything else (FEEDING_B). Firmware state machine also only has FEEDING_A and FEEDING_B states. This is consistent but limits multi-color support to 2 physical inputs despite the recipe format supporting 8 colors.

---

## Summary Table

| Interface | Rating | Severity of Issues |
|---|---|---|
| 1. Recipe JSON fields | ALIGNED | None |
| 2. Serial protocol commands | ALIGNED | None |
| 3. Material temperatures | ALIGNED | Low (timing field confusion) |
| 4. Config constants | **MISMATCHED** | CRITICAL (MAX_SEGMENTS 500 vs 10000, buffer 256 vs 512) |
| 5. pyproject.toml entry points | ALIGNED | None |
| 6. Docker/Render configs | **MISMATCHED** | Medium (missing files, wrong server mode) |
| 7. MQTT bridge vs firmware | **MISMATCHED** | CRITICAL (status format mismatch, phantom commands) |
| 8. Hardware validation specs | ALIGNED | None |

**Total new integration gaps found: 10** (2 critical, 3 high, 3 medium, 2 low)
