# Splice3D Bill of Materials

> Parts needed to build the Splice3D filament splicer.

Phase F1.3 structured BOM package:

1. `docs/F1.3_BOM.md`
2. `hardware/f1_3/spec/bom_catalog.json`
3. `scripts/hardware/validate_f1_3.py`

## Core Electronics (From Ender 3)

These parts come from your donor Ender 3:

| Part | Quantity | Notes |
|------|----------|-------|
| BTT SKR Mini E3 v2 | 1 | Already have |
| NEMA17 Stepper Motor | 3 | X, Y, Z from Ender |
| Hotend Assembly | 1 | Used for weld chamber |
| 24V Power Supply | 1 | 350W Ender PSU |
| LCD Display | 1 | Stock Ender LCD |
| Endstop Switches | 3 | X, Y, Z limit switches |

## Additional Parts to Purchase

### Motors & Actuators

| Part | Quantity | Est. Price | Link/Source |
|------|----------|------------|-------------|
| SG90 Servo Motor | 1 | $3-5 | Amazon/AliExpress |
| NEMA17 Stepper | 1 | $10-15 | (If need 4th motor) |

### Extruder Components

| Part | Quantity | Est. Price | Notes |
|------|----------|------------|-------|
| MK8 Extruder Kit | 2 | $8-15 each | For input feeds |
| BMG Clone Extruder | 2 | $15-25 each | Better grip (optional upgrade) |
| Bowden Couplings (PC4-M6) | 6 | $5/pack | Push-fit connectors |
| PTFE Tube (2mm ID) | 1m | $5 | For weld chamber insert |
| PTFE Tube (4mm ID) | 2m | $8 | Standard Bowden |

### Weld Chamber

| Part | Quantity | Est. Price | Notes |
|------|----------|------------|-------|
| 40W Heater Cartridge | 1 | $3-5 | 24V, 6mm diameter |
| 100K NTC Thermistor | 1 | $2-3 | Standard 3D printer type |
| Heatsink (40mm) | 1 | $3 | Aluminum, for heat break |
| 4010 Axial Fan (24V) | 1 | $3-5 | Cooling |

### Cutter Mechanism

| Part | Quantity | Est. Price | Notes |
|------|----------|------------|-------|
| Flush Cut Blade | 2 | $5/pack | Replaceable |
| M3 Hardware Kit | 1 | $10 | Screws, nuts, washers |
| Spring (small) | 2 | $3/pack | For return mechanism |

### Frame & Mounting

| Part | Quantity | Est. Price | Notes |
|------|----------|------------|-------|
| 2020 Aluminum Extrusion | 1m | $8-12 | Or reuse Ender frame |
| 2020 Corner Brackets | 8 | $8/pack | L-brackets |
| M5 T-nuts | 20 | $5/pack | For 2020 extrusion |
| M5 x 8mm Bolts | 20 | $5/pack | Frame assembly |

### Spool Holders

| Part | Quantity | Est. Price | Notes |
|------|----------|------------|-------|
| 608 Bearings | 6 | $5/pack | Spool rotation |
| 8mm Smooth Rod | 30cm | $3 | Spool axle |
| Printed Spool Holders | 3 | $0 | Print yourself |

### Wiring & Connectors

| Part | Quantity | Est. Price | Notes |
|------|----------|------------|-------|
| JST-XH Connector Kit | 1 | $10 | 2/3/4 pin connectors |
| 18 AWG Silicone Wire | 2m | $5 | Heater, power |
| 22 AWG Wire | 5m | $5 | Signals, sensors |
| Heat Shrink Tubing | 1 kit | $5 | Various sizes |
| Cable Sleeve | 2m | $3 | Wire management |

### Optional Upgrades

| Part | Quantity | Est. Price | Notes |
|------|----------|------------|-------|
| Rotary Encoder | 1 | $5-10 | Precise length measurement |
| Filament Width Sensor | 1 | $15-25 | Quality monitoring |
| ESP32-CAM | 1 | $8 | Future: color detection |

## Cost Summary

| Category | Estimated Cost |
|----------|----------------|
| From Ender 3 | $0 (already have) |
| Motors & Actuators | $15-25 |
| Extruder Components | $50-80 |
| Weld Chamber | $15-20 |
| Cutter Mechanism | $20-30 |
| Frame & Mounting | $30-40 |
| Spool Holders | $10-15 |
| Wiring & Connectors | $30-40 |
| **TOTAL** | **$170-250** |

## Recommended Vendors

| Vendor | Best For |
|--------|----------|
| Amazon | Quick shipping, prime items |
| AliExpress | Bulk purchases, lowest prices |
| Filastruder | Specialty filament hardware |
| PrintedSolid | Quality 3D printer parts |
| Fabreeko | Premium components |

## 3D Printed Parts

Print these yourself (STL files to be created):

| Part | Quantity | Material | Notes |
|------|----------|----------|-------|
| Input Spool Holder | 2 | PETG | Holds input spools |
| Output Spool Holder | 1 | PETG | Holds queue spool |
| Extruder Mount | 2 | PETG | Mounts extruders to frame |
| Weld Chamber Housing | 1 | ABS/ASA | Heat resistant |
| Cutter Housing | 1 | PETG | Holds servo + blade |
| Electronics Enclosure | 1 | PETG | Protects SKR board |
| LCD Mount | 1 | PLA | Display holder |

## Notes

> [!TIP]
> - Buy spare heater cartridges and thermistors (they're cheap and fail)
> - Get extra PTFE tube - you'll experiment with weld chamber designs
> - Consider buying a crimping tool for JST connectors

> [!IMPORTANT]
> - Ensure all 24V components are properly rated
> - Use silicone wire for heater connections (heat resistant)
> - TMC2209 drivers need heatsinks if running >1A
