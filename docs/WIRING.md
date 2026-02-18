# Splice3D Wiring Guide

> Complete wiring diagram for BTT SKR Mini E3 v2.0

## Board Overview

The BTT SKR Mini E3 v2.0 is a 32-bit drop-in replacement for Ender 3 boards.

Phase F1.2 electronics package:

1. `docs/F1.2_ELECTRONICS_DESIGN.md`
2. `hardware/f1_2/spec/electronics_design.json`
3. `scripts/hardware/validate_f1_2.py`

**Key Features:**
- MCU: STM32F103RCT6 (72MHz, 256KB flash, 48KB RAM)
- Drivers: 4x TMC2209 (silent, UART configurable)
- Voltage: 12-24V DC input
- USB: Type-C for serial communication

## Pin Mapping for Splice3D

```
┌─────────────────────────────────────────────────────────────┐
│                    BTT SKR Mini E3 v2.0                     │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │    X    │  │    Y    │  │    Z    │  │    E    │        │
│  │ TMC2209 │  │ TMC2209 │  │ TMC2209 │  │ TMC2209 │        │
│  │         │  │         │  │         │  │         │        │
│  │Extruder │  │Extruder │  │ Output  │  │ Cutter  │        │
│  │    A    │  │    B    │  │ Winder  │  │ (Servo) │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│                                                             │
│  Endstops:            Heater:              Fan:            │
│  X_STOP → Sensor A    HE0 → Weld Heater   FAN0 → Cooling   │
│  Y_STOP → Sensor B    TH0 → Thermistor                     │
│  Z_STOP → Sensor Out                                       │
│                                                             │
│  Power: 24V DC (same as Ender 3 PSU)                       │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Connections

### Stepper Motors

| Function | Driver | Step Pin | Dir Pin | Enable Pin | Motor |
|----------|--------|----------|---------|------------|-------|
| Input Extruder A | X | PB13 | PB12 | PB14 | NEMA17 (from Ender extruder) |
| Input Extruder B | Y | PB10 | PB2 | PB11 | NEMA17 (spare or purchased) |
| Output Winder | Z | PB0 | PC5 | PB1 | NEMA17 (from Ender Z) |
| Cutter | E | PB3 | PB4 | PD1 | Servo SG90 (not stepper) |

**Wiring (4-pin JST-XH):**
```
Motor cable:
  Black  (A-) ──► 1A
  Green  (A+) ──► 1B  
  Red    (B+) ──► 2A
  Blue   (B-) ──► 2B

Note: If motor spins wrong direction, swap A+/A- OR B+/B-
```

### Heater (Weld Chamber)

| Function | Pin | Connector |
|----------|-----|-----------|
| Heater Cartridge | PC8 (HE0) | 2-pin screw terminal |
| Thermistor | PA0 (TH0) | 2-pin JST |

**Wiring:**
```
24V Heater Cartridge (40W recommended):
  HE0+ ──► Red wire
  HE0- ──► Black wire

100K NTC Thermistor:
  TH0 ──► Either wire (not polarized)
```

### Cooling Fan

| Function | Pin | Connector |
|----------|-----|-----------|
| Cooling Fan | PC6 (FAN0) | 2-pin JST |

**Wiring:**
```
24V Axial Fan (4010 or 4020):
  FAN0+ ──► Red wire
  FAN0- ──► Black wire (GND)
```

### Filament Sensors

| Function | Pin | Connector |
|----------|-----|-----------|
| Sensor A (Input) | PC0 (X_STOP) | 3-pin JST |
| Sensor B (Input) | PC1 (Y_STOP) | 3-pin JST |
| Sensor Out | PC2 (Z_STOP) | 3-pin JST |

**Wiring (Microswitch):**
```
Endstop connector (3-pin):
  GND ──► C (Common)
  SIG ──► NC (Normally Closed)
  VCC ──► Not used for mechanical switch

For optical sensor:
  GND ──► GND
  SIG ──► Signal
  VCC ──► 3.3V or 5V
```

### Servo (Cutter)

| Function | Pin | Notes |
|----------|-----|-------|
| Servo Signal | PB3 (E_STEP) | PWM capable |
| Servo VCC | 5V rail | From board or separate |
| Servo GND | GND | Common ground |

**Wiring:**
```
SG90 Servo (3-wire):
  Orange ──► PB3 (Signal)
  Red    ──► 5V (from board or BEC)
  Brown  ──► GND

Note: If servo draws >500mA, use external 5V BEC
```

### LCD Display (Stock Ender 3)

The stock Ender 3 LCD plugs directly into EXP1:

```
EXP1 Connector:
  ┌─────────────────────┐
  │ 1  2  3  4  5  6  7 │
  └─────────────────────┘
    │  │  │  │  │  │  └── LCD_RS
    │  │  │  │  │  └───── LCD_D4
    │  │  │  │  └──────── LCD_EN
    │  │  │  └─────────── BTN_ENC
    │  │  └────────────── BTN_EN1
    │  └───────────────── BTN_EN2
    └──────────────────── BEEPER
```

## Power

| Input | Voltage | Source |
|-------|---------|--------|
| Main Power | 24V DC | Ender 3 PSU (350W) |
| Logic | 3.3V | Onboard regulator |
| Servo | 5V | Onboard or external BEC |

**Wiring:**
```
Ender 3 PSU:
  L (Live)   ──► AC Mains
  N (Neutral) ──► AC Mains
  ⏚ (Ground) ──► AC Ground

  V+ (24V)   ──► SKR Power Input +
  V- (GND)   ──► SKR Power Input -
```

## Complete Wiring Diagram

```
                                    ┌──────────────┐
    ┌─────────────┐                 │   24V PSU    │
    │  SPOOL A    │                 │  (Ender 3)   │
    │  (White)    │                 └──────┬───────┘
    └──────┬──────┘                        │
           │                               │ 24V
           ▼                               ▼
    ┌──────────────┐               ┌───────────────────────────────────────┐
    │ EXTRUDER A   │◄──────────────│  BTT SKR Mini E3 v2.0                 │
    │ (X Driver)   │   X_MOTOR     │                                       │
    └──────────────┘               │  X_STOP ◄── Filament Sensor A         │
                                   │  Y_STOP ◄── Filament Sensor B         │
    ┌─────────────┐                │  Z_STOP ◄── Output Sensor             │
    │  SPOOL B    │                │                                       │
    │  (Black)    │                │  HE0 ───► Weld Heater (40W)           │
    └──────┬──────┘                │  TH0 ◄── Thermistor (100K NTC)        │
           │                       │                                       │
           ▼                       │  FAN0 ──► Cooling Fan (24V)           │
    ┌──────────────┐               │                                       │
    │ EXTRUDER B   │◄──────────────│  E_STEP ──► Cutter Servo              │
    │ (Y Driver)   │   Y_MOTOR     │                                       │
    └──────────────┘               │  EXP1 ◄──► LCD Display                │
                                   │                                       │
    ┌──────────────┐               │  USB-C ◄──► Computer (Serial)         │
    │OUTPUT WINDER │◄──────────────│                                       │
    │ (Z Driver)   │   Z_MOTOR     └───────────────────────────────────────┘
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ OUTPUT SPOOL │
    │  (Queue)     │
    └──────────────┘
```

## TMC2209 UART Configuration

The SKR Mini E3 v2 has TMC2209 drivers with UART support. Configure in firmware:

```cpp
// Motor current (milliamps)
#define MOTOR_CURRENT_MA 800

// StealthChop for quiet operation
#define STEALTHCHOP_ENABLED true
```

## Safety Notes

> [!CAUTION]
> - Always disconnect power before wiring
> - Double-check polarity on heater and fan
> - Heater can reach 280°C - use appropriate wire gauge
> - Keep 24V and 5V circuits separate

## Testing Procedure

1. **Before powering on:**
   - Verify all connections with multimeter
   - Check for shorts between V+ and GND
   
2. **First power-on:**
   - USB only (no 24V) - check LEDs
   - Add 24V - verify no smoke/heat
   
3. **Individual tests:**
   - Motors: Send manual step commands
   - Heater: Set to 50°C, verify thermistor reads correctly
   - Servo: Test 0° and 90° positions
   - Sensors: Trigger manually, verify detection
