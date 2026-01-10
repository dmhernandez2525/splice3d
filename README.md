# Splice3D

Pre-splice multi-color filament for any FDM printer using G-code analysis and automated welding.

## Overview

Splice3D creates a single spool of pre-joined filament segments where color transitions are calculated to match exact extrusion points in a 3D print. This enables multi-color printing on any single-extruder printer without real-time tool changes.

## Components

| Directory | Description |
|-----------|-------------|
| `postprocessor/` | Python G-code parser and recipe generator |
| `cli/` | USB communication tools |
| `firmware/` | Ender 3 board firmware |
| `docs/` | Build and calibration guides |
| `hardware/` | CAD files (future) |
| `samples/` | Test G-code files |

## Quick Start

### 1. Install Post-Processor

```bash
cd postprocessor
pip install -r requirements.txt
```

### 2. Process G-code

```bash
python splice3d_postprocessor.py input_multicolor.gcode
# Outputs: splice_recipe.json + modified_print.gcode
```

### 3. Send Recipe to Machine

```bash
cd ../cli
python splice3d_cli.py --port /dev/ttyUSB0 --recipe ../splice_recipe.json
```

### 4. Print

Load the pre-spliced spool and print `modified_print.gcode`.

## Status

🚧 **Under Development** - Currently building V1 prototype.

## License

MIT
