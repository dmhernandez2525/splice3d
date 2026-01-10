# Changelog

All notable changes to Splice3D will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and documentation
- G-code parser with T command and M600 support
- Recipe generator with segment merging
- Recipe validator for pre-flight checks
- G-code modifier for single-extruder output
- Firmware architecture for BTT SKR Mini E3 v2
- 13-state splice cycle state machine
- Error handler with recovery actions
- TMC2209 UART configuration (StealthChop, current control)
- LCD display support for stock Ender 3 screen
- CLI tools: `splice3d_cli.py`, `simulator.py`, `analyze_gcode.py`, `gui.py`
- Filament profile database for common materials
- Comprehensive documentation suite
- Setup and test scripts

### Documentation
- WIRING.md: SKR Mini E3 v2 wiring diagram
- BOM.md: Bill of materials ($170-250 estimate)
- MECHANICAL.md: Build guide
- SPLICE_CORE.md: Weld mechanism design
- CALIBRATION.md: Tuning procedures
- TROUBLESHOOTING.md: Common issues and solutions
- ORCASLICER_SETUP.md: Multi-extruder profile setup
- STARRY_NIGHT_ANALYSIS.md: Benchmark analysis
- ROADMAP.md: 6-phase development plan
- VISION.md: Full project vision
- INTEGRATION_OPTIONS.md: Slicer plugin vs web analysis
- PROJECT_ORGANIZATION.md: Directory structure reference
- CHANGELOG.md: Version history (Keep a Changelog format)
- CONTRIBUTING.md: Contribution guidelines
- LICENSE: MIT

---

## [0.1.0] - 2026-01-10

### Added
- **Post-processor** (Python)
  - `gcode_parser.py`: Parse multi-tool G-code, extract extrusion lengths
  - `recipe_generator.py`: Generate splice recipe JSON
  - `gcode_modifier.py`: Strip tool changes, add pause for spool load
  - `filament_profiles.py`: Material database with splice parameters
  - Support for both T commands and M600 color changes

- **Firmware** (C++ for BTT SKR Mini E3 v2)
  - `main.cpp`: Entry point with serial and stepper initialization
  - `config.h`: Pin mappings for SKR Mini E3 v2 (STM32F103)
  - `state_machine.cpp`: 13-state splice cycle
  - `stepper_control.cpp`: AccelStepper wrapper for feed/wind/cut
  - `temperature.cpp`: PID temperature control with Steinhart-Hart
  - `serial_handler.cpp`: USB command parsing
  - `error_handler.cpp`: Error codes and recovery logic

- **CLI Tools**
  - `splice3d_cli.py`: USB serial communication with machine
  - `simulator.py`: Test state machine without hardware
  - `analyze_gcode.py`: G-code segment statistics

- **Tests**
  - `test_parser.py`: 10 unit tests for G-code parser
  - `test_recipe.py`: 8 tests for recipe generator

- **Samples**
  - `test_multicolor.gcode`: Multi-tool G-code example
  - `test_m600_colorchange.gcode`: M600 color change example

### Technical Details
- Target board: BTT SKR Mini E3 v2.0 (STM32F103RCT6)
- Target printer: Centauri Carbon (OrcaSlicer)
- Benchmark: Starry Night Vase (4000+ color changes)
- Estimated waste reduction: 79% vs traditional purge towers

### Known Limitations
- V1 supports 2 colors only (selector mechanism needed for 7)
- Position tracking (dimple encoding) not yet implemented
- Hardware not yet built/tested

---

## Future Releases

### [0.2.0] - Planned
- Dimple encoding for position tracking
- Drift compensation algorithm
- LCD display support
- Configuration via serial commands

### [0.3.0] - Planned
- Multi-input selector (4+ colors)
- Wi-Fi connectivity (ESP32)
- Web interface for recipe upload

### [1.0.0] - Planned
- Full Starry Night Vase benchmark completion
- Proven splice reliability over 4000+ changes
- Complete documentation with video guides
