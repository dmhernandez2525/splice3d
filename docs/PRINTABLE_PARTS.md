# Printable Parts List

> 3D printed parts needed for Splice3D build.

## Overview

These parts will need to be designed and printed. This document serves as the specification for future CAD work.

## Status

**Not yet designed** - STL files will be added as CAD work is completed.

---

## Required Parts

### Frame & Mounting

| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Main Frame Base | 1 | PETG | Holds all components |
| Input Spool Holder | 2 | PETG | Standard spool size |
| Output Spool Holder | 1 | PETG | For queue spool |
| Extruder Mount A | 1 | PETG | Mounts input extruder |
| Extruder Mount B | 1 | PETG | Mounts input extruder |
| Winder Mount | 1 | PETG | Mounts output extruder |

### Splice Chamber

| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Weld Chamber Housing | 1 | ABS/ASA | Heat resistant required |
| PTFE Tube Holder | 2 | PETG | Aligns PTFE to chamber |
| Heater Block Clamp | 1 | ABS/ASA | Secures heat block |
| Cooling Duct | 1 | PETG | Directs fan airflow |

### Cutter Assembly

| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Cutter Housing | 1 | PETG | Holds servo + blade |
| Blade Mount | 1 | PETG | Attaches blade to servo horn |
| Cutting Anvil | 1 | PETG | Surface for cutting against |
| Filament Guide Pre-Cut | 1 | PETG | Aligns filament for cut |
| Filament Guide Post-Cut | 1 | PETG | Guides cut filament |

### Electronics

| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| SKR Board Enclosure | 1 | PETG | Protects electronics |
| SKR Board Mount | 1 | PLA | Secures board in enclosure |
| LCD Mount | 1 | PLA | Holds Ender 3 LCD |
| PSU Mount | 1 | PETG | If using external PSU |
| Wire Management Clips | 10 | PLA | Cable organization |

### Filament Path

| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Bowden Coupling Mount | 4 | PETG | PC4-M6 fitting holders |
| Filament Sensor Mount | 3 | PETG | Holds endstop switches |
| Filament Guide Tube | 2 | PETG | Guides filament path |

---

## Design Requirements

### General

- All parts should use M3 hardware
- Include tolerances for heat expansion (PETG shrinks ~0.4%)
- Consider print orientation for strength
- Add chamfers/fillets for easier printing

### Spool Holders

```
                    ┌─────────────┐
                    │   SPOOL     │
                    │   HOLDER    │
                    │             │
  ┌─────────────────┼─────────────┼─────────────────┐
  │                 │  ─────────  │                 │
  │  Bearing        │   8mm rod   │        Bearing  │
  │  (608)          │             │        (608)    │
  └─────────────────┴─────────────┴─────────────────┘

Requirements:
- Holds 608 bearings (22mm OD)
- 8mm rod for axle
- Fits standard 200mm/1kg spool
- Maybe 15+° tilt for gravity feed
```

### Extruder Mounts

- Holes for M3 screws
- Slot for NEMA17 mounting pattern (31mm spacing)
- Bowden fitting on output
- Adjustable tension lever clearance

### Weld Chamber Housing

- Must withstand 80°C ambient (near heater)
- Hole for 40W heater cartridge (6mm)
- Hole for thermistor (M3)
- PTFE tube pass-through (4mm ID)
- Cooling fan mount (40mm)

### Cutter Housing

- Servo horn clearance for full rotation
- Blade guard for safety
- Filament guide channels (2mm ID)
- Access for blade replacement

---

## Print Settings

### PLA Parts
- Layer height: 0.2mm
- Infill: 20%
- Perimeters: 3
- Material: Any PLA

### PETG Parts
- Layer height: 0.2mm
- Infill: 40%
- Perimeters: 4
- Material: PETG
- Enclosure recommended

### ABS/ASA Parts (Heat Resistant)
- Layer height: 0.2mm
- Infill: 50%
- Perimeters: 4
- Enclosure required
- Material: ABS or ASA

---

## Future: CAD Files

When designed, files will be added:

```
splice3d/
└── cad/
    ├── README.md
    ├── frame/
    │   └── *.stl
    ├── splice_chamber/
    │   └── *.stl
    ├── cutter/
    │   └── *.stl
    └── electronics/
        └── *.stl
```

## Contributing CAD

If you'd like to help design these parts:

1. Use FreeCAD, Fusion 360, or OnShape
2. Follow the specifications above
3. Include STEP files (editable) and STL (printable)
4. Submit PR with photos of printed parts
