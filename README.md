# Splice3D

> Pre-splice multi-color filament for any FDM printer.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/dmhernandez2525/splice3d/actions/workflows/ci.yml/badge.svg)](https://github.com/dmhernandez2525/splice3d/actions)

## What is Splice3D?

Splice3D creates a single spool of pre-joined filament segments where color transitions are calculated to match exact extrusion points in a 3D print. This enables **multi-color printing on any single-extruder printer** without real-time tool changes.

**Target benchmark**: [Starry Night Vase](https://makerworld.com/en/models/2129520-starry-night-vase) (4000+ color changes)

## How It Works

```
[OrcaSlicer] → [Post-Processor] → [Splice3D Machine] → [Pre-spliced Spool] → [Any Printer]
```

1. Slice model with virtual multi-extruder in OrcaSlicer
2. Post-processor extracts segment lengths from G-code
3. Splice3D machine welds filament segments together
4. Print with the pre-spliced spool on any single-extruder printer

## Hardware

- **Controller**: BTT SKR Mini E3 v2.0 (STM32F103)
- **Motors**: 3x NEMA17 (from Ender 3)
- **Heater**: Hotend assembly (weld chamber)
- **Cutter**: SG90 servo + blade

**Estimated build cost**: $170-250 (using donor Ender 3 parts)

## Quick Start

### Install Post-Processor

```bash
# Option 1: Install as package (recommended)
pip install -e .

# Option 2: Install dependencies only
cd postprocessor
pip install -r requirements.txt
```

### Process Multi-Color G-code

```bash
python3 splice3d_postprocessor.py input.gcode --colors white black
# Outputs: input_splice_recipe.json + input_modified.gcode
```

### Simulate Splice Cycle

```bash
cd cli
python3 simulator.py ../samples/test_multicolor_splice_recipe.json
```

### Send to Machine (when built)

```bash
python3 splice3d_cli.py --port /dev/ttyACM0 --recipe recipe.json --start
```

## Documentation

| Document | Description |
|----------|-------------|
| [WIRING.md](docs/WIRING.md) | SKR Mini E3 v2 connection guide |
| [BOM.md](docs/BOM.md) | Bill of materials with prices |
| [MECHANICAL.md](docs/MECHANICAL.md) | Build guide |
| [SPLICE_CORE.md](docs/SPLICE_CORE.md) | Weld mechanism design |
| [CALIBRATION.md](docs/CALIBRATION.md) | Tuning steps/mm and weld quality |
| [ORCASLICER_SETUP.md](docs/ORCASLICER_SETUP.md) | Multi-extruder profile setup |
| [ROADMAP.md](docs/ROADMAP.md) | Future development phases |
| [VISION.md](docs/VISION.md) | Full vision: dimples, crimps, print farm |

## Project Structure

```
splice3d/
├── postprocessor/     # Python G-code tools
├── firmware/          # C++ for SKR Mini E3
├── cli/               # USB communication + simulator
├── docs/              # Documentation
└── samples/           # Test files
```

## Status

✅ Post-processor complete (30 tests passing)
✅ Firmware architecture complete
✅ CI/CD pipeline configured (Python 3.9-3.12)
✅ Documentation complete (25+ guides)
🔧 Hardware build pending  

## License

MIT
