# Project Organization

> Overview of Splice3D project structure and file organization.

## Directory Structure

```
splice3d/
├── README.md                    # Project overview
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # MIT License
│
├── postprocessor/               # Python G-code tools
│   ├── __init__.py
│   ├── splice3d_postprocessor.py  # Main CLI entry point
│   ├── gcode_parser.py            # Parse multi-tool G-code
│   ├── gcode_modifier.py          # Modify G-code for single-extruder
│   ├── recipe_generator.py        # Generate splice JSON
│   ├── recipe_validator.py        # Validate recipes before use
│   ├── filament_profiles.py       # Material splice parameters
│   ├── requirements.txt           # Python dependencies
│   └── tests/                     # Unit tests
│       ├── test_parser.py
│       └── test_recipe.py
│
├── firmware/                    # C++ for SKR Mini E3 v2
│   ├── platformio.ini           # Build configuration
│   └── src/
│       ├── main.cpp             # Entry point
│       ├── config.h             # Pin mappings, settings
│       ├── state_machine.cpp/h  # 13-state splice cycle
│       ├── stepper_control.cpp/h # Motor control
│       ├── temperature.cpp/h    # PID heater control
│       ├── serial_handler.cpp/h # USB command parsing
│       ├── error_handler.cpp/h  # Error recovery
│       ├── tmc_config.cpp/h     # TMC2209 UART configuration
│       └── lcd_display.cpp/h    # Stock Ender 3 LCD
│
├── cli/                         # Command-line tools
│   ├── splice3d_cli.py          # USB communication
│   ├── simulator.py             # Test without hardware
│   ├── analyze_gcode.py         # G-code statistics
│   ├── gui.py                   # Simple tkinter GUI
│   └── requirements.txt
│
├── docs/                        # Documentation
│   ├── WIRING.md                # Hardware connections
│   ├── BOM.md                   # Bill of materials
│   ├── MECHANICAL.md            # Build guide
│   ├── SPLICE_CORE.md           # Weld mechanism
│   ├── CALIBRATION.md           # Tuning procedures
│   ├── TROUBLESHOOTING.md       # Common issues
│   ├── ORCASLICER_SETUP.md      # Slicer configuration
│   ├── STARRY_NIGHT_ANALYSIS.md # Benchmark analysis
│   ├── ROADMAP.md               # Development phases
│   ├── VISION.md                # Full project vision
│   ├── INTEGRATION_OPTIONS.md   # Plugin vs web analysis
│   └── PROJECT_ORGANIZATION.md  # This file
│
├── samples/                     # Test files
│   ├── test_multicolor.gcode    # Multi-tool example
│   ├── test_m600_colorchange.gcode # M600 example
│   └── test_multicolor_splice_recipe.json # Sample recipe
│
├── scripts/                     # Utility scripts
│   ├── setup.sh                 # Environment setup
│   └── test.sh                  # Run all tests
│
└── integrations/                # External integrations
    └── octoprint/               # OctoPrint plugin (future)
        └── README.md
```

## Key Files by Purpose

### For End Users
| File | Purpose |
|------|---------|
| `README.md` | Getting started |
| `docs/WIRING.md` | Wire up the machine |
| `docs/BOM.md` | Parts to buy |
| `docs/CALIBRATION.md` | Tune for your setup |

### For Developers
| File | Purpose |
|------|---------|
| `CONTRIBUTING.md` | How to contribute |
| `CHANGELOG.md` | What changed |
| `docs/PROJECT_ORGANIZATION.md` | This file |

### Core Functionality
| Module | Entry Point |
|--------|-------------|
| Post-processor | `postprocessor/splice3d_postprocessor.py` |
| Firmware | `firmware/src/main.cpp` |
| CLI | `cli/splice3d_cli.py` |

## Build Commands

### Python Post-Processor
```bash
cd postprocessor
pip install -r requirements.txt
python splice3d_postprocessor.py input.gcode
```

### Firmware
```bash
cd firmware
pio run              # Build
pio run -t upload    # Flash to board
```

### Tests
```bash
./scripts/test.sh
```

## Configuration

| Component | Config Location |
|-----------|-----------------|
| Firmware | `firmware/src/config.h` |
| Splice Params | `postprocessor/filament_profiles.py` |
| Build | `firmware/platformio.ini` |
