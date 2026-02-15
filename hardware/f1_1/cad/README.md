# F1.1 Mechanical CAD Assets

This directory contains parametric OpenSCAD source for the Phase 1.1 mechanical assembly.

## Files

| File | Purpose |
|------|---------|
| `common.scad` | Shared dimensions and primitives |
| `cutting_station.scad` | SG90 cutter enclosure with blade guide and filament alignment channel |
| `splice_chamber_station.scad` | Hotend-based splice chamber with PTFE constrained path |
| `cooling_station.scad` | Fan duct and heat sink flow channel |
| `encoder_station.scad` | Encoder wheel bracket with spring idler cavity |
| `filament_guides_jigs.scad` | Entry and transition guides plus alignment fixtures |
| `modular_mounts.scad` | Modular rail and removable station mount pads |
| `assembly_compact.scad` | Compact fit-check assembly layout |
| `assembly_exploded.scad` | Exploded view with numbered callouts |

## Export STL

`openscad` is used for direct STL export when installed.

```bash
python3 scripts/hardware/export_f1_1_stl.py
```

The export command reads `hardware/f1_1/spec/mechanical_layout.json` and writes STL files to `hardware/f1_1/stl/`.

## Fit and Quality Validation

```bash
python3 scripts/hardware/validate_f1_1.py
python3 -m pytest postprocessor/tests/test_mechanical_validation.py -v
```

Validation checks include:
- filament deflection angle limit (`<=30°`)
- printable part bed fit (`<=220x220mm`)
- station interface consistency for modular mounting
- non-overlapping station placement in compact assembly simulation
