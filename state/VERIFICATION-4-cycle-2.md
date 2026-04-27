# Verification-4: Test Coverage & Build Health (Cycle 2)

**Auditor:** Verifier-4
**Date:** 2026-03-28
**Scope:** Verify fixes from Cycle 1 gaps, assess test quality, find new gaps

---

## 1. Test Suite Run Results

```
615 passed in 1.71s
Overall coverage (postprocessor + cli + services): 86% (6829 stmts, 940 missed)
Ruff lint errors: 0
Entry point import: OK (from postprocessor.splice3d_postprocessor import main succeeds)
```

All 615 tests pass. No failures, errors, or skips. This is an increase of 30 tests from Cycle 1 (585).

---

## 2. Cycle 1 Gap Fix Verification

### GAP: splice3d_postprocessor.py broken import (was 0% coverage) -- FIXED
- Imports now use `from postprocessor.gcode_parser import ...` (package-relative)
- `from postprocessor.splice3d_postprocessor import main` succeeds
- Coverage now **92%** (77 stmts, 6 missed: lines 80, 97-99, 102, 162)
- `TestSplice3DMainFunction` class exercises main() with 7 test cases covering success, verbose, colors, transition, no-pause, file-not-found, and many-segments-verbose paths
- **Verdict: FIXED.** Entry point works, coverage above 80%.

### GAP: cli/ modules at 0% coverage -- PARTIALLY FIXED
- `cli/simulator.py`: now **92%** (167 stmts, 14 missed). Tests in `cli/tests/test_simulator.py` cover config, state machine, recipe loading, running, edge cases. **FIXED.**
- `cli/analyze_gcode.py`: now **48%** (115 stmts, 60 missed). Tests in `cli/tests/test_analyze_gcode.py` cover the `analyze_gcode()` function but NOT `print_analysis()` (50 lines) or `main()` (49 lines). **PARTIALLY FIXED.**
- `cli/splice3d_cli.py`: still **0%** (141 stmts). No tests exist. **NOT FIXED.**
- `cli/gui.py`: still **0%** (88 stmts). No tests exist. **NOT FIXED.**
- `cli/api_server.py`: still **0%** (12 stmts). No tests exist. **NOT FIXED.**

### GAP: services/mqtt_bridge.py at 0% coverage -- NOT FIXED
- Still **0%** (405 stmts, all missed). No `services/tests/` directory exists. **NOT FIXED.**

### GAP: filament_profiles.py at 70% -- NOT FIXED
- Still **70%** (56 stmts, 17 missed). Lines 199-218 (`__main__` block) remain untested. Low severity, unchanged from Cycle 1.

### GAP: 29 ruff/lint errors -- FIXED
- `ruff check postprocessor/ cli/ services/ --statistics` returns zero errors.
- **Verdict: FIXED.** REQ-088 now satisfied locally.

### GAP: CI pipeline non-blocking -- NOT FIXED
- `ci.yml` still has `continue-on-error: true` on firmware build (line 64) and both lint steps (lines 88, 93)
- No `--cov-fail-under=80` flag on pytest
- CI still only tests `postprocessor/tests/`, not `cli/tests/`
- `codecov.yml` still uses `informational: true` on both project and patch status
- **Verdict: NOT FIXED.** REQ-085 still violated.

### GAP: pyproject.toml placeholder URLs -- FIXED
- URLs now point to `https://github.com/dmhernandez2525/splice3d`. No longer `yourusername`. **FIXED.**

---

## 3. Current Coverage by Module

| Module | Stmts | Miss | Cover | Status vs REQ-087 (80%) |
|--------|-------|------|-------|------------------------|
| `postprocessor/gcode_parser.py` | 118 | 0 | 100% | PASS |
| `postprocessor/splice3d_postprocessor.py` | 77 | 6 | 92% | PASS |
| `postprocessor/filament_profiles.py` | 56 | 17 | 70% | **FAIL** |
| `cli/simulator.py` | 167 | 14 | 92% | PASS |
| `cli/analyze_gcode.py` | 115 | 60 | 48% | **FAIL** |
| `cli/splice3d_cli.py` | 141 | 141 | 0% | **FAIL** |
| `cli/gui.py` | 88 | 88 | 0% | **FAIL** |
| `cli/api_server.py` | 12 | 12 | 0% | **FAIL** |
| `services/mqtt_bridge.py` | 405 | 405 | 0% | **FAIL** |

6 of 9 key modules fail the 80% coverage requirement.

---

## 4. Test Quality Assessment

### cli/tests/test_simulator.py -- GOOD
Tests meaningful behavior: state machine transitions, recipe loading (success/failure/invalid), full run completion, color routing via internal `_step()`, zero-rate division protection, empty segments, default color fallback. 15 tests exercising real logic.

### cli/tests/test_analyze_gcode.py -- GOOD (but incomplete)
Tests meaningful behavior: two-color analysis, segment distribution bucketing, splice time estimation, waste reduction, short-segment warnings, min/max/avg stats, error handling. 9 tests exercising real logic. However, `print_analysis()` and `main()` (the CLI entry point with argparse, file output, quiet mode) are completely untested, leaving 48% of the module uncovered.

### postprocessor/tests/test_splice3d_postprocessor.py -- GOOD
The `TestSplice3DMainFunction` class (lines 517-589) exercises the actual `splice3d_main()` entry point via `patch("sys.argv", ...)`. Tests cover success paths, all CLI flags (verbose, colors, transition, no-pause), file-not-found error exit, and many-segments verbose truncation. This is real entry-point testing. The earlier test classes in the same file also test the pipeline components directly. 31 tests total.

---

## 5. New Gaps Discovered

### NEW-GAP-C2-1: cli/analyze_gcode.py main() and print_analysis() untested (48% coverage)

The `analyze_gcode()` function is tested, but `main()` (lines 196-248) and `print_analysis()` (lines 144-193) are not. Together they are 99 lines / 60 statements. The `main()` function handles argparse, file existence checking, JSON output with `--output`, and quiet mode with `--quiet`. None of these code paths are exercised. This is the same pattern that was fixed for `splice3d_postprocessor.py` (which now uses `patch("sys.argv", ...)` to test its main), but was not applied to `analyze_gcode.py`.

**Severity: MEDIUM.** The core analysis logic is tested; the CLI wrapper is not.

### NEW-GAP-C2-2: simulator.py main() untested (92% coverage, lines 219-265 missed)

Similar to analyze_gcode.py: the `FirmwareSimulator` class is well-tested (state machine, recipe loading, running), but the `main()` CLI entry point (lines 218-265) is not tested at all. This function handles argparse and wires together the config/simulator/run pipeline. 44 lines, 14 missed statements.

**Severity: LOW.** The underlying logic is tested at 92%; only the argparse wrapper is missing.

### NEW-GAP-C2-3: CI does not run cli/tests/ -- tests exist but CI ignores them

The CI workflow (`.github/workflows/ci.yml` line 34) only runs:
```
python -m pytest postprocessor/tests/ -v --cov=postprocessor --cov-report=xml
```

The 30 new tests in `cli/tests/` (test_simulator.py, test_analyze_gcode.py) are never executed in CI. A regression in the simulator or analyze tool would not be caught by the pipeline. This was flagged in Cycle 1 (gap 8e) and remains unfixed.

**Severity: HIGH.** Tests exist but are invisible to CI.

### NEW-GAP-C2-4: No integration test for pip install entry points

The `pyproject.toml` declares three console script entry points:
- `splice3d = "postprocessor.splice3d_postprocessor:main"`
- `splice3d-analyze = "cli.analyze_gcode:main"`
- `splice3d-simulate = "cli.simulator:main"`

While individual `main()` functions are importable and (for splice3d_postprocessor) tested, there is no test that verifies `pip install -e .` followed by running the actual console scripts works. The Cycle 1 import breakage (bare imports) would not have been caught by any existing test because tests use direct Python imports, not subprocess calls to the installed entry points. A single integration test that runs `subprocess.run(["splice3d", "--help"])` after install would catch this class of bug.

**Severity: MEDIUM.** The bare-import bug was fixed, but the class of bug (entry point breaks on install) has no regression test.

### NEW-GAP-C2-5: Coverage threshold not enforced anywhere

Despite REQ-087 requiring 80% coverage:
- pytest has no `--cov-fail-under=80` flag in CI or locally
- codecov.yml uses `informational: true` (never blocks)
- pyproject.toml has no `[tool.pytest.ini_options]` coverage config
- No pre-commit hook checks coverage

Coverage can silently regress below 80% and nothing will flag it. This was identified in Cycle 1 (gap 8a) and remains unfixed.

**Severity: HIGH.** The requirement exists on paper but has zero enforcement.

---

## 6. Summary Scorecard

| Check | Cycle 1 | Cycle 2 | Delta |
|-------|---------|---------|-------|
| Tests passing | 585 | 615 | +30 |
| Overall coverage | ~55-60% (real) | 86% (measured) | Improved |
| Ruff lint errors | 29 | 0 | FIXED |
| Entry point import | BROKEN | Working | FIXED |
| splice3d_postprocessor.py coverage | 0% | 92% | FIXED |
| cli/simulator.py coverage | 0% | 92% | FIXED |
| cli/analyze_gcode.py coverage | 0% | 48% | Partial |
| cli/splice3d_cli.py coverage | 0% | 0% | No change |
| cli/gui.py coverage | 0% | 0% | No change |
| cli/api_server.py coverage | 0% | 0% | No change |
| services/mqtt_bridge.py coverage | 0% | 0% | No change |
| filament_profiles.py coverage | 70% | 70% | No change |
| CI runs cli/tests/ | NO | NO | No change |
| Coverage threshold enforced | NO | NO | No change |
| CI lint/build blocking | NO | NO | No change |

### Modules still failing REQ-087 (80% coverage): 6 of 9
### Total untested statements: 940 of 6829 (14% missed overall, but concentrated in 4 modules at 0%)

**Overall assessment:** Significant progress from Cycle 1. The critical entry-point breakage is fixed, lint errors are resolved, and the core postprocessor plus simulator have strong test coverage. However, 646 statements across `cli/splice3d_cli.py` (141), `cli/gui.py` (88), `cli/api_server.py` (12), and `services/mqtt_bridge.py` (405) remain at 0% coverage. The CI pipeline still cannot enforce any quality gate. The new cli/tests/ directory exists but CI does not run it.
