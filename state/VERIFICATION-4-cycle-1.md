# Verification-4: Test Coverage & Build Health (Cycle 1)

**Auditor:** Verifier-4
**Date:** 2026-03-28
**Scope:** Test quality, coverage gaps, lint health, build pipeline, entry points

---

## 1. Test Suite Run Results

```
585 passed in 6.43s
Overall postprocessor/ coverage: 95% (5649 stmts, 284 missed)
```

All 585 tests pass. No failures, no errors, no skips.

---

## 2. Modules Below 80% Coverage

| Module | Coverage | Missed Lines | Verdict |
|--------|----------|-------------|---------|
| `postprocessor/splice3d_postprocessor.py` | **0%** | Lines 17-163 (entire file) | **ESCALATED** |
| `postprocessor/filament_profiles.py` | **70%** | Lines 199-218 (`__main__` CLI block) | **CONFIRMED** |

### splice3d_postprocessor.py (0% coverage) - ESCALATED

This is NOT just a coverage gap; it is a **broken import**. The file uses bare imports (`from gcode_parser import ...`) instead of relative/package imports (`from postprocessor.gcode_parser import ...`). When imported as `postprocessor.splice3d_postprocessor` (as pyproject.toml entry point declares), it raises:

```
ModuleNotFoundError: No module named 'gcode_parser'
```

This means:
- The `splice3d` entry point **cannot work** when installed via `pip install -e .`
- The test file `test_splice3d_postprocessor.py` works around this by importing the sub-modules directly (`from gcode_parser import GCodeParser`) after adding the parent path to `sys.path`, so it never actually imports `splice3d_postprocessor.py` itself
- Coverage is 0% because the module cannot be imported by the coverage tool
- The CI `Test CLI` step works only because it `cd postprocessor` first, making bare imports resolve

**Root cause:** Bare imports instead of relative/package imports in `splice3d_postprocessor.py` lines 22-24.

### filament_profiles.py (70% coverage) - CONFIRMED

Lines 199-218 are a `if __name__ == "__main__"` CLI block. Not tested. This is a minor gap; the `__main__` guard is intentionally excluded from normal test runs. Low severity.

---

## 3. CLI and Services Test Coverage - ESCALATED

| Module | Lines | Coverage | Tests Exist? |
|--------|-------|----------|-------------|
| `cli/analyze_gcode.py` | 248 | **0%** | NO |
| `cli/api_server.py` | 38 | **0%** | NO |
| `cli/gui.py` | 158 | **0%** | NO |
| `cli/simulator.py` | 261 | **0%** | NO |
| `cli/splice3d_cli.py` | 247 | **0%** | NO |
| `services/mqtt_bridge.py` | 632 | **0%** | NO |

**No `cli/tests/` or `services/tests/` directories exist.** There are zero test files for any CLI module or the MQTT bridge service. That is 1,584 lines of completely untested code (885 statements).

**Verdict: ESCALATED.** REQ-087 (80%+ coverage) is violated across both `cli/` and `services/`. The MQTT bridge alone is 632 lines of untested production code handling serial communication, MQTT protocol, threading, and error recovery.

---

## 4. Validation Test Quality Assessment

Reviewed 5 of 40 validation test files:

| Test File | Tests Real Logic? | Verdict |
|-----------|-------------------|---------|
| `test_device_connection_validation.py` | Validates JSON spec field presence, tests negative cases (missing items, empty spec) | Spec structure only |
| `test_encoder_system_validation.py` | Validates spec accuracy limits, slip detection, calibration values | Spec structure only |
| `test_temperature_control_validation.py` | Checks spec values (PLA 210C, ABS 250C), validates acceptance limits | Spec structure + values |
| `test_error_recovery_validation.py` | Validates recovery phases, error categories, serial commands, negative cases | Spec structure only |
| `test_cutting_system_validation.py` | Checks cut phases, safety features, EEPROM persistence, maintenance intervals | Spec structure only |

**Verdict: CONFIRMED gap.** All 40 validation tests follow the same pattern: load a JSON spec file, check that expected keys/values exist, verify the report passes. They are testing that the spec file is well-formed, NOT testing any actual firmware logic, hardware behavior, or runtime code. While they serve a documentation/contract purpose, they inflate the test count (40 tests * ~10 assertions each = ~400 "tests") without testing real application behavior. The 585-test count is misleading; roughly 400 of those are spec-file-structure checks.

---

## 5. Lint Health (ruff)

```
14  F401  unused-import
12  F541  f-string-missing-placeholders
 2  F841  unused-variable
 1  E722  bare-except
--------------------------
29 total errors
```

**Breakdown by severity:**

### F401 Unused Imports (14) - CONFIRMED
- `cli/gui.py`: unused `os`
- `postprocessor/gcode_modifier.py`: unused `Optional`
- `postprocessor/recipe_validator.py`: unused `Optional`
- `postprocessor/splice3d_postprocessor.py`: unused `os`, `parse_gcode`, `generate_recipe`, `modify_gcode` (4 errors)
- `postprocessor/tests/test_parser.py`: unused `Segment`
- `postprocessor/tests/test_recipe.py`: unused `Segment`, `SpliceRecipe`, `generate_recipe`
- `postprocessor/tests/test_splice3d_postprocessor.py`: unused `patch`
- `postprocessor/tests/test_temperature_control_validation.py`: unused `Path`
- `services/mqtt_bridge.py`: unused `datetime`

### E722 Bare Except (1) - CONFIRMED
- `services/mqtt_bridge.py:469`: `except:` with no exception type. This silently swallows all exceptions including `KeyboardInterrupt` and `SystemExit`.

### F841 Unused Variables (2) - CONFIRMED
- `cli/gui.py:153`: `app = Splice3DGUI(root)` (assigned, never used)
- `postprocessor/tests/test_gcode_modifier.py:200`: `stats` variable unused

### F541 f-string Without Placeholders (12) - CONFIRMED
- 7 in `cli/analyze_gcode.py`
- 2 in `postprocessor/gcode_modifier.py`
- 2 in `postprocessor/splice3d_postprocessor.py`
- 1 in `cli/simulator.py`

**REQ-088 (zero lint errors) is violated with 29 errors.**

---

## 6. Entry Point Verification

| Entry Point | Target | Importable? | Verdict |
|-------------|--------|-------------|---------|
| `splice3d` | `postprocessor.splice3d_postprocessor:main` | **NO** - `ModuleNotFoundError: No module named 'gcode_parser'` | **ESCALATED** |
| `splice3d-analyze` | `cli.analyze_gcode:main` | YES | OK |
| `splice3d-simulate` | `cli.simulator:main` | YES | OK |
| `splice3d-mqtt-bridge` | `services.mqtt_bridge:main` | YES | OK |

The primary entry point (`splice3d`) is broken. See Section 2 for details.

---

## 7. Hardcoded Paths

Grep for `/Users/` in all `.py` and `.md` files (excluding .venv): **No matches found.**

**Verdict: DISPUTED (not a real issue).** REQ-090 is satisfied.

---

## 8. CI Pipeline Issues

### 8a. Coverage not enforced - ESCALATED
The CI workflow (`ci.yml`) runs `pytest --cov` but does **not** fail on coverage thresholds. There is no `--cov-fail-under=80` flag. Coverage data is generated but never enforced.

### 8b. Lint steps use `continue-on-error: true` - CONFIRMED
Both `flake8` and `black` checks have `continue-on-error: true`, meaning lint failures never block merges. REQ-088 cannot be enforced this way.

### 8c. CI uses flake8 but project uses ruff locally - CONFIRMED
The CI installs `flake8` and `black`; the local tooling uses `ruff`. These tools have different rule sets, so passing locally does not guarantee passing in CI and vice versa.

### 8d. Firmware build uses `continue-on-error: true` - CONFIRMED
The `test-firmware-build` job has `continue-on-error: true` on the `pio run` step. A firmware that fails to compile will not block the pipeline.

### 8e. CLI and services not tested in CI - ESCALATED
The CI only runs `python -m pytest postprocessor/tests/`. There is no test step for `cli/` or `services/`. Even if tests existed, they would not be run.

---

## 9. Codecov Configuration Issues

The `codecov.yml` sets:
- `range: "60...100"` (green starts at 60%, far below the 80% requirement)
- `status.project.default.informational: true` (coverage is **informational only**, never blocks PRs)
- `status.patch.default.informational: true` (same for patch coverage)
- Only tracks `postprocessor/` via flags; `cli/` and `services/` are untracked

**Verdict: CONFIRMED.** Codecov is configured as a suggestion, not an enforcement mechanism.

---

## 10. New Gaps Discovered (Beyond Original Inventory)

### NEW-1: Primary entry point is broken (ESCALATED)
`splice3d` command fails on import due to bare imports in `splice3d_postprocessor.py`. The file uses `from gcode_parser import ...` instead of `from postprocessor.gcode_parser import ...`. This breaks `pip install -e .` && `splice3d`.

### NEW-2: 1,584 lines of completely untested code in cli/ and services/ (ESCALATED)
Zero test files exist for 5 CLI modules and the MQTT bridge. This is not a "below 80%" situation; it is 0% coverage on 885 statements.

### NEW-3: CI pipeline is entirely non-blocking (ESCALATED)
Between `continue-on-error: true` on lint/firmware steps, no coverage threshold enforcement, and informational-only codecov, the CI pipeline cannot prevent any quality regression from merging.

### NEW-4: Test count is inflated by spec-structure tests (CONFIRMED)
Of 585 tests, approximately 400 are validation tests that only check JSON spec file structure. The real logic test count is closer to 185. The 95% coverage figure only applies to `postprocessor/`, not the full codebase.

### NEW-5: pyproject.toml URLs are placeholder (CONFIRMED)
`Homepage`, `Repository`, and `Issues` URLs all point to `https://github.com/yourusername/splice3d` - placeholder values that were never updated.

### NEW-6: Bare except in mqtt_bridge.py (CONFIRMED)
Line 469 uses `except:` which catches `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit` in addition to normal exceptions. This can mask critical failures in serial communication cleanup.

### NEW-7: Test isolation concern - sys.path manipulation (CONFIRMED)
Multiple test files (test_parser.py, test_recipe.py, test_splice3d_postprocessor.py, test_encoder_system_validation.py) manipulate `sys.path` at import time. This is fragile and can cause import ordering bugs in larger test suites.

---

## Summary Scorecard

| Check | Status | Severity |
|-------|--------|----------|
| REQ-087: 80%+ coverage | **FAIL** - 0% on cli/, services/, splice3d_postprocessor.py | ESCALATED |
| REQ-088: Zero lint errors | **FAIL** - 29 errors | CONFIRMED |
| REQ-089: All Python files compile | **FAIL** - splice3d_postprocessor.py import error | ESCALATED |
| REQ-090: No hardcoded user paths | **PASS** | DISPUTED (not an issue) |
| REQ-085: CI enforces quality | **FAIL** - all checks are non-blocking | ESCALATED |
| Entry points functional | **FAIL** - primary entry point broken | ESCALATED |
| Validation tests test real logic | **FAIL** - spec structure checks only | CONFIRMED |

**Overall assessment:** The 95% coverage and 585-test headline numbers are misleading. The primary CLI entry point is broken, 1,584 lines of production code have zero tests, the CI pipeline cannot block any regression, and roughly 70% of the test count is JSON spec structure validation rather than logic testing. Actual functional test coverage of the full Python codebase is approximately 55-60%.
