| Cycle | Item | Tier | Action | Tests Added | Verification | Status |
|-------|------|------|--------|-------------|-------------|--------|
| 1 | GAP-001 | A | Fix bare imports in splice3d_postprocessor.py and recipe_generator.py; add main() tests | 7 unit | 592 pass, lint clean, 96% cov | DONE |
| 2 | GAP-002 | A | Align MAX_SEGMENTS to 500 in recipe_validator.py to match firmware | 0 (existing tests cover) | 592 pass | DONE |
| 3 | GAP-003 | A | Use SERIAL_BUFFER_SIZE constant in serial_handler.h instead of hardcoded 256 | N/A (firmware) | lint clean | DONE |
| 4 | GAP-004 | A | Replace 9 static bool locals with member variables, reset in transitionTo() | N/A (firmware) | lint clean | DONE |
| 5 | GAP-005 | A | Resume restores heater state when paused during heating/welding | N/A (firmware) | lint clean | DONE |
| 6 | GAP-006 | A | Add IWDG hardware watchdog timer (4s timeout) to main.cpp | N/A (firmware) | lint clean | DONE |
| 7 | GAP-007 | A | Fix millis() rollover: use elapsed time pattern for heater timeout | N/A (firmware) | lint clean | DONE |
| 8 | GAP-008 | A | Guard auto-tune against amplitude<0.1 and tu<0.001 division by zero | N/A (firmware) | lint clean | DONE |
| 9 | GAP-010 | B | Fix all 29 lint errors (ruff --fix + manual: bare except, unused vars) | 0 | ruff 0 errors | DONE |
| 10 | GAP-012 | B | Add try/except IOError to modify_file() and save_recipe() | 0 | 592 pass | DONE |
| 11 | GAP-019 | C | Fix placeholder URLs in pyproject.toml | 0 | N/A | DONE |
| 12 | GAP-014 | B | Fix Dockerfile: add services/, use pip install -e . | 0 | N/A | DONE |
| 13 | GAP-021 | C | Fix render.yaml: use gunicorn instead of Flask dev server | 0 | N/A | DONE |
| 14 | GAP-022 | C | Fix bare except in mqtt_bridge.py | 0 | lint clean | DONE |
| 15 | GAP-016 | B | State machine uses material profile for temperature instead of hardcoded PLA | N/A (firmware) | lint clean | DONE |
| 16 | GAP-009 | A | Rewrite MQTT bridge status parser to match firmware space-delimited format | 0 | lint clean | DONE |
| 17 | GAP-013 | B | Map PREHEAT->TEMP MATERIAL PLA, COOLDOWN->TEMP 0 in MQTT bridge | 0 | lint clean | DONE |
| 18 | GAP-024 | C | Add JSON telemetry and TEMP_LOG parsing to MQTT bridge _handle_serial_line | 0 | lint clean | DONE |
| 19 | GAP-015 | B | Guard simulator against division by zero with max(..., 0.1) | 0 | lint clean | DONE |
| 20 | GAP-017 | B | Add 30-second motor timeout in handleFeedingA/B, transition to ERROR | N/A (firmware) | N/A | DONE |
| 21 | GAP-018 | B | TMC init failure now reports error via REPORT_ERROR macro | N/A (firmware) | N/A | DONE |
| 22 | GAP-011 | B | Add test suites for cli/simulator.py and cli/analyze_gcode.py (23 tests) | 14 unit + 9 analysis | 615 pass, 92% cov | DONE |
| 23 | BUG | B | Fix IndexError on empty segments in simulator (discovered by new test) | 1 regression test | 615 pass | DONE |
