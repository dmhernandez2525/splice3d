# Splice3D Mechanical Design Guide

> Building the physical filament splicing machine from Ender 3 parts.

## Overview

The Splice3D machine repurposes an Ender 3 or CR-10's electronics and motors to create a filament splicing station. This guide documents the mechanical design concepts.

## Components Needed

### From Donor Printer
| Part | Use in Splice3D |
|------|-----------------|
| Mainboard | Main controller |
| X Stepper + Driver | Input Extruder A |
| Y Stepper + Driver | Input Extruder B |
| Z Stepper + Driver | Output Winder |
| E Stepper + Driver | Cutter/Spare |
| Hotend | Weld Chamber |
| Thermistor | Temperature Sensing |
| LCD + Encoder | Status Display |
| Power Supply | 24V Power |

### Additional Parts
| Part | Purpose | Notes |
|------|---------|-------|
| 2x Extruder Assembly | Pull filament | Stock or BMG clones |
| PTFE Tube (2mm ID) | Weld Chamber Insert | Must fit inside hotend |
| Servo (SG90) | Cutter Actuator | Or use spare stepper |
| Razor Blade | Cutting Element | Flush-cut style |
| Bearings + Rod | Spool Holders | Input and output |
| Limit Switches (x3) | Filament Sensors | Repurpose endstops |
| Cooling Fan | Weld Cooling | 24V 40mm |

## Weld Chamber Design

The weld chamber is built from the modified hotend:

```
        ┌─────────────────────────────────────┐
        │         PTFE Tube (2mm ID)          │
        │    ┌───────────────────────────┐    │
Filament A ─►│                           │◄── Filament B
        │    │   ═══════════════════════ │    │
        │    │         HEAT BLOCK        │    │
        │    │   ═══════════════════════ │    │
        │    └───────────────────────────┘    │
        │              │                      │
        │              ▼                      │
        │         Welded Output               │
        └─────────────────────────────────────┘
```

### Modification Steps

1. **Remove Nozzle**: Unscrew nozzle from heat block
2. **Remove Heat Break**: Unscrew standard heat break
3. **Insert PTFE**: Thread 2mm ID PTFE through entire assembly
4. **Secure**: Use set screws or epoxy to hold PTFE in place
5. **Test Flow**: Manually push filament through when hot

### Temperature Notes
- PLA: 200-210°C (start here)
- PETG: 230-240°C
- ABS: 245-255°C

## Cutter Mechanism

### Servo-Based (Recommended for V1)

```
    Servo Motor
        │
        ├──────┐
        │      │ Arm
    ────┴──────┴────
        │Blade│
    ────────────────
      Filament Path
```

- SG90 servo rotates arm with razor blade
- Blade cuts through filament against anvil
- Return to home position after cut

### Stepper-Based (Alternative)
- Use NEMA17 with cam mechanism
- More precise control of cut pressure
- Requires additional driver (use E stepper)

## Filament Path

```
┌──────────────┐     ┌──────────────┐
│  INPUT       │     │  INPUT       │
│  SPOOL A     │     │  SPOOL B     │
└──────┬───────┘     └───────┬──────┘
       │                     │
       ▼                     ▼
   ┌───────┐             ┌───────┐
   │EXTRUDR│             │EXTRUDR│
   │   A   │             │   B   │
   └───┬───┘             └───┬───┘
       │                     │
       ▼                     ▼
   ┌───────────────────────────┐
   │       CUTTER ZONE         │
   └───────────┬───────────────┘
               │
               ▼
       ┌───────────────┐
       │  WELD CHAMBER │
       │   (HOTEND)    │
       └───────┬───────┘
               │
               ▼
         ┌───────────┐
         │  WINDER   │
         │  EXTRUDER │
         └─────┬─────┘
               │
               ▼
       ┌───────────────┐
       │    OUTPUT     │
       │    SPOOL      │
       └───────────────┘
```

## Filament Sensors

Use endstop switches as filament presence detectors:

- **Sensor A**: Before Extruder A input
- **Sensor B**: Before Extruder B input  
- **Sensor Out**: After weld chamber (optional)

Wire to X_MIN, Y_MIN, Z_MIN endstop inputs.

## Frame Suggestions

Options for mounting everything:

1. **2020 Aluminum Extrusion**: Modular, adjustable
2. **Printed Frame**: Custom design, slower to iterate
3. **Wooden Base**: Quick prototype, not durable

## Calibration Checklist

1. [ ] Input extruders grip filament firmly
2. [ ] Weld chamber reaches and holds temperature
3. [ ] PTFE insert constrains filament to 1.75mm
4. [ ] Cutter fully severs filament
5. [ ] Output winder pulls welded filament smoothly
6. [ ] Test weld passes through Bowden tube without jamming
