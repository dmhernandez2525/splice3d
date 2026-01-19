# Phase 1: Hardware Design & Fabrication

## Overview

Design and build the core Splice3D hardware: splice head, encoder system, filament drive, and control electronics.

**Goal:** Working splice hardware with good splice quality

---

## Milestones

### M1: Splice Head Design (Week 1-2)

- [ ] CAD design for heated splice block
  - Aluminum heat block with 2.0mm bore
  - 40W cartridge heater pocket
  - NTC 100K thermistor pocket
  - PTFE tube fittings (inlet/outlet)
- [ ] Cooling system design
  - Heat break zone
  - Fan mount for controlled cooling
  - Temperature gradient management
- [ ] Filament path geometry
  - Smooth transitions to prevent grinding
  - Adequate length for heat transfer
  - Easy cleaning access

**Specifications:**
| Parameter | Value |
|-----------|-------|
| Max temperature | 300°C |
| Bore diameter | 2.0mm (for 1.75mm filament) |
| Heater | 40W cartridge |
| Splice time target | <3 seconds |

**Acceptance Criteria:**
- Heat block reaches 300°C in <60 seconds
- Temperature stable ±1°C at target
- Filament passes smoothly without grinding

### M2: Encoder System Design (Week 2)

- [ ] Encoder wheel design
  - 20mm diameter knurled wheel
  - Bearing-supported axle
  - Adjustable tension mechanism
- [ ] Optical encoder integration
  - 600 PPR minimum resolution
  - Quadrature output for direction detection
  - Dust protection housing
- [ ] Mounting bracket design
  - Adjustable position for wheel contact
  - Easy filament loading
  - Secure mounting to frame

**Accuracy Requirements:**
| Metric | Target |
|--------|--------|
| Resolution | <0.1mm per pulse |
| Accuracy | ±0.5mm per meter |
| Drift over 100m | <2mm |

**Acceptance Criteria:**
- Encoder tracks bidirectional movement
- Accuracy verified over 10m test length
- No slippage under normal tension

### M3: Filament Drive System (Week 2-3)

- [ ] Stepper motor selection and mount
  - NEMA 17 with sufficient torque
  - Direct drive or geared reduction
  - TMC2209 driver for quiet operation
- [ ] Drive gear design
  - Dual-gear extruder style for grip
  - Easy filament loading
  - Tension adjustment mechanism
- [ ] Multi-spool holder design
  - 4-8 spool capacity
  - Smooth filament runout
  - Tangle prevention guides

**Performance Targets:**
| Parameter | Target |
|-----------|--------|
| Feed rate | Up to 50mm/s |
| Grip force | Sufficient for TPU |
| Spool capacity | 4-8 colors |

**Acceptance Criteria:**
- Feeds PLA, PETG, ABS, TPU reliably
- No filament slippage during splice
- Smooth spool changes

### M4: Frame and Assembly Design (Week 3)

- [ ] Main frame CAD design
  - Rigid structure for encoder accuracy
  - Easy component access
  - Desktop footprint optimization
- [ ] 3D printable parts optimization
  - Material selection (PETG recommended)
  - Print orientation for strength
  - Minimal supports required
- [ ] Wiring management
  - Cable routing channels
  - Connector locations
  - Strain relief

**Acceptance Criteria:**
- All parts printable on standard printer (220x220mm)
- Assembly time <4 hours
- Stable, vibration-free operation

### M5: PCB Design (Week 3-4)

- [ ] Control board schematic
  - ESP32-S3 as main controller
  - TMC2209 stepper driver interface
  - Heater MOSFET with protection
  - Thermistor input with filtering
  - Encoder quadrature input
  - USB-C for power and communication
- [ ] PCB layout
  - Power section isolation
  - Thermal management for MOSFET
  - ESD protection on connectors
- [ ] Board fabrication and testing
  - Order prototype PCBs
  - Assembly and bring-up
  - Basic functionality test

**Acceptance Criteria:**
- Board powers up without issues
- All I/O functional
- Heater control stable

### M6: Firmware Development (Week 5-6)

- [ ] PlatformIO project setup
- [ ] Stepper motor control
  - AccelStepper library integration
  - Smooth acceleration profiles
  - Position tracking
- [ ] PID temperature control
  - Auto-tune capability
  - Configurable PID gains
  - Safety limits and watchdog
- [ ] Encoder reading
  - Interrupt-driven counting
  - Direction detection
  - Overflow handling
- [ ] Serial communication protocol
  - Command parsing
  - Status reporting
  - Error handling

**Acceptance Criteria:**
- Motor responds to movement commands
- Temperature holds ±1°C at setpoint
- Encoder counts accurately

### M7: Splice Sequence Implementation (Week 6-7)

- [ ] Splice algorithm firmware
  - Feed color A to splice point
  - Heat and compress
  - Cool for strength
  - Feed color B
  - Verify splice position
- [ ] Material profiles
  - PLA splice parameters
  - PETG splice parameters
  - ABS splice parameters
  - Custom profile support
- [ ] Splice quality testing
  - Strength testing (pull test)
  - Visual inspection criteria
  - Failure mode analysis

**Splice Sequence:**
```
1. Feed filament A to splice position
2. Cut/prepare filament A end
3. Heat to splice temperature (material-specific)
4. Insert filament B with overlap
5. Compress and hold (~1 second)
6. Cool to handling temperature
7. Verify splice via tension test
8. Continue to next splice
```

**Acceptance Criteria:**
- Splice strength >80% of filament strength
- Consistent splice diameter (no blobs/necking)
- <5% splice failure rate

### M8: Calibration & Testing (Week 7-8)

- [ ] Encoder calibration procedure
  - Known-length filament test
  - Correction factor calculation
  - Verification protocol
- [ ] Splice parameter tuning
  - Temperature optimization per material
  - Timing optimization
  - Pressure optimization
- [ ] Full system integration test
  - 5-color splice test
  - 50-splice endurance test
  - Error recovery testing
- [ ] Documentation
  - Assembly guide with photos
  - Calibration guide
  - Troubleshooting guide

**Acceptance Criteria:**
- Encoder calibrated to ±0.5mm/m
- Material profiles tuned
- 95%+ splice success rate

---

## Technical Specifications

### Electrical

| Component | Specification |
|-----------|---------------|
| Input voltage | 24V DC |
| Heater power | 40W max |
| Stepper current | 1.0A RMS |
| Total power | <60W peak |

### Mechanical

| Parameter | Value |
|-----------|-------|
| Filament size | 1.75mm |
| Max spool size | 1kg standard |
| Footprint | ~200x150x200mm |
| Weight | <2kg assembled |

### Performance

| Metric | Target |
|--------|--------|
| Splice time | <3 seconds |
| Feed rate | 50mm/s max |
| Position accuracy | ±0.5mm/m |
| Temperature accuracy | ±1°C |

---

## Bill of Materials

| Component | Qty | Est. Cost |
|-----------|-----|-----------|
| ESP32-S3 DevKit | 1 | $10 |
| NEMA 17 Stepper | 1 | $12 |
| TMC2209 Driver | 1 | $8 |
| Rotary Encoder 600PPR | 1 | $15 |
| Heater Cartridge 40W | 1 | $5 |
| Thermistor NTC 100K | 1 | $2 |
| Aluminum Heat Block | 1 | $8 |
| PTFE Tube 2m | 1 | $5 |
| Custom PCB | 1 | $15 |
| Printed Parts | - | $5 |
| Fasteners, Wiring | - | $15 |
| **Total** | | **~$100** |

---

## Definition of Done

- [ ] All milestones complete
- [ ] Splice head heats and maintains temperature
- [ ] Encoder tracks with <1mm/m error
- [ ] Splices hold under printing tension
- [ ] 5+ color print successful
- [ ] Assembly guide documented
- [ ] BOM finalized with sources
